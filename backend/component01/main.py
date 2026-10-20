import time
import os
from fastapi import FastAPI, HTTPException
from fastapi.middleware.cors import CORSMiddleware
import pandas as pd
import numpy as np
import joblib
import shap
import json
import sqlite3

# Import our custom modules
from schemas import UserRegistrationRequest, PeerFitnessSyncRequest, RecommendationRequest
from database import init_db, get_registered_user, DB_FILE
from nlp_scraper import fetch_live_social_data
from utils import map_difficulty, extract_scenic_tags, build_route_geometry_from_csv

BASE_DIR = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
MODEL_PATH = os.path.join(BASE_DIR, 'models', 'xgboost_trail_model.pkl')
TRAILS_DATA_PATH = os.path.join(BASE_DIR, 'data', 'raw', 'hiking_trails_sri_lanka.csv')

app = FastAPI(
    title="Venture - Explainable Trail Recommendation API",
    description="Multi-Modal XGBoost, SHAP & Live NLP Backend for Component 1",
    version="2.1.0"
)

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

model = joblib.load(MODEL_PATH)
explainer = shap.TreeExplainer(model)
trails_df = pd.read_csv(TRAILS_DATA_PATH)

FEATURE_COLS = [
    'User_Age', 'User_Fitness_Score', 'User_Exp_Score', 'Has_Medical_Issue',
    'Pref_Max_Hours', 'Distance_KM', 'Elevation_Gain_M', 'Avg_Completion_Time_Hours',
    'Trail_Diff_Score', 'Is_Steep_Rock', 'Fitness_Difficulty_Gap',
    'Duration_Diff_Hours', 'Scenic_Match_Ratio', 'Medical_Risk_Flag'
]

FEATURE_LABELS = {
    'Fitness_Difficulty_Gap': 'Fitness vs Difficulty Match',
    'Duration_Diff_Hours': 'Duration Preference Match',
    'Scenic_Match_Ratio': 'Scenic Feature Overlap',
    'Medical_Risk_Flag': 'Medical Safety Factor',
    'Elevation_Gain_M': 'Elevation Gain Impact',
    'Distance_KM': 'Trail Distance Impact',
    'Trail_Diff_Score': 'Base Trail Difficulty',
    'User_Fitness_Score': 'User Fitness Baseline',
    'User_Exp_Score': 'Hiking Experience',
    'Avg_Completion_Time_Hours': 'Estimated Hike Duration',
    'Pref_Max_Hours': 'Preferred Time Limit',
    'Has_Medical_Issue': 'Medical Condition Status',
    'Is_Steep_Rock': 'Terrain Steepness',
    'User_Age': 'Age Factor'
}

trails_df['Trail_Diff_Score'] = trails_df['Base_Difficulty'].apply(map_difficulty)
trails_df['Trail_Scenic_Set'] = trails_df['Scenic_Features'].apply(extract_scenic_tags)
trails_df['Is_Steep_Rock'] = trails_df['Terrain_Type'].apply(
    lambda x: 1 if any(w in str(x) for w in ['Steep', 'Rock', 'Boulder']) else 0
)

@app.get("/")
def home():
    user = get_registered_user()
    return {
        "status": "online",
        "app": "Venture Trail Recommendation API",
        "user_registered": user is not None
    }

@app.get("/profile")
def get_profile():
    user = get_registered_user()
    if not user:
        return {"registered": False, "message": "No user registered yet."}
    return user

@app.post("/profile")
def save_or_update_profile(req: UserRegistrationRequest):
    init_db()
    conn = sqlite3.connect(DB_FILE)
    cursor = conn.cursor()
    cursor.execute("""
        INSERT INTO user_profile (
            id, name, email, age, weight_kg, height_cm, resting_hr,
            experience_level, has_medical_issue, medical_notes,
            preferred_max_hours, preferred_scenic, fitness_level, fitness_source
        ) VALUES (1, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
        ON CONFLICT(id) DO UPDATE SET
            name=excluded.name,
            email=excluded.email,
            age=excluded.age,
            weight_kg=excluded.weight_kg,
            height_cm=excluded.height_cm,
            resting_hr=excluded.resting_hr,
            experience_level=excluded.experience_level,
            has_medical_issue=excluded.has_medical_issue,
            medical_notes=excluded.medical_notes,
            preferred_max_hours=excluded.preferred_max_hours,
            preferred_scenic=excluded.preferred_scenic,
            fitness_level=excluded.fitness_level
    """, (
        req.name, req.email, req.age, req.weight_kg, req.height_cm, req.resting_hr,
        req.experience_level, int(req.has_medical_issue), req.medical_notes,
        req.preferred_max_hours, json.dumps(req.preferred_scenic),
        req.fitness_level, "Manual Selection / Smartwatch Baseline"
    ))
    conn.commit()
    conn.close()
    return {"status": "saved", "profile": get_registered_user()}

@app.delete("/profile")
def reset_profile():
    conn = sqlite3.connect(DB_FILE)
    cursor = conn.cursor()
    cursor.execute("DELETE FROM user_profile")
    conn.commit()
    conn.close()
    return {"status": "deleted", "registered": False}

@app.post("/sync-fitness-model")
def sync_fitness_from_peer_model(req: PeerFitnessSyncRequest):
    user = get_registered_user()
    if not user:
        raise HTTPException(status_code=400, detail="Please register a user profile first.")
    conn = sqlite3.connect(DB_FILE)
    cursor = conn.cursor()
    cursor.execute("""
        UPDATE user_profile
        SET fitness_level = ?, resting_hr = COALESCE(?, resting_hr), fitness_source = ?
        WHERE id = 1
    """, (req.predicted_fitness_level, req.resting_hr, req.source_model))
    conn.commit()
    conn.close()
    return {"status": "synced", "profile": get_registered_user()}

@app.post("/recommend")
def recommend_trails(req: RecommendationRequest):
    start_time = time.time()
    
    user = get_registered_user()
    if not user:
        raise HTTPException(
            status_code=400,
            detail="USER_NOT_REGISTERED: Please complete your hiker registration first."
        )

    age = user["age"]
    experience_level = user["experience_level"]
    has_medical_issue = user["has_medical_issue"]
    preferred_max_hours = user["preferred_max_hours"]
    fitness_level = req.fitness_level if req.fitness_level else user["fitness_level"]
    preferred_scenic = req.preferred_scenic if req.preferred_scenic is not None else user["preferred_scenic"]

    fit_map = {"low": 1, "beginner": 1, "moderate": 2, "high": 3, "advanced": 3}
    exp_map = {"beginner": 1, "intermediate": 2, "expert": 3, "advanced": 3}

    u_fit = fit_map.get(fitness_level.lower(), 2)
    u_exp = exp_map.get(experience_level.lower(), 1)
    u_med = 1 if has_medical_issue else 0
    u_scenic = set(preferred_scenic)

    filtered_trails = trails_df[
        (trails_df['Distance_KM'] <= req.max_distance_km) &
        (trails_df['Elevation_Gain_M'] <= req.max_elevation_m)
    ].copy()

    if filtered_trails.empty:
        filtered_trails = trails_df.copy()

    rows = []
    for _, t in filtered_trails.iterrows():
        user_cap = (u_fit * 0.6) + (u_exp * 0.4)
        fitness_diff_gap = round(user_cap - t['Trail_Diff_Score'], 2)
        duration_diff = round(preferred_max_hours - t['Avg_Completion_Time_Hours'], 2)

        t_scenic = t['Trail_Scenic_Set']
        scenic_overlap = round(len(u_scenic.intersection(t_scenic)) / max(len(t_scenic), 1), 2)
        med_risk = 1 if (u_med == 1 and (t['Trail_Diff_Score'] == 3 or t['Elevation_Gain_M'] > 500)) else 0

        rows.append({
            'Trail_ID': t['Trail_ID'],
            'Trail_Name': t['Trail_Name'],
            'Region': t.get('Region', 'Sri Lanka'),
            'Base_Difficulty': t['Base_Difficulty'],
            'Scenic_Features': t['Scenic_Features'],
            'Terrain_Type': t['Terrain_Type'],
            'Start_Lat': t['Start_Lat'],
            'Start_Lon': t['Start_Lon'],
            'End_Lat': t['End_Lat'],
            'End_Lon': t['End_Lon'],
            'GPX_File_Path': t.get('GPX_File_Path', ''),
            'Social_Search_Query': t.get('Social_Search_Query', f"{t['Trail_Name']} Sri Lanka hike"),
            'Steep_Start_KM': t.get('Steep_Start_KM', round(t['Distance_KM'] * 0.35, 1)),
            'Steep_End_KM': t.get('Steep_End_KM', round(t['Distance_KM'] * 0.55, 1)),
            'User_Age': age,
            'User_Fitness_Score': u_fit,
            'User_Exp_Score': u_exp,
            'Has_Medical_Issue': u_med,
            'Pref_Max_Hours': preferred_max_hours,
            'Distance_KM': t['Distance_KM'],
            'Elevation_Gain_M': t['Elevation_Gain_M'],
            'Avg_Completion_Time_Hours': t['Avg_Completion_Time_Hours'],
            'Trail_Diff_Score': t['Trail_Diff_Score'],
            'Is_Steep_Rock': t['Is_Steep_Rock'],
            'Fitness_Difficulty_Gap': fitness_diff_gap,
            'Duration_Diff_Hours': duration_diff,
            'Scenic_Match_Ratio': scenic_overlap,
            'Medical_Risk_Flag': med_risk
        })

    eval_df = pd.DataFrame(rows)
    X_input = eval_df[FEATURE_COLS]

    preds = np.clip(model.predict(X_input), 5.0, 99.5)
    eval_df['Base_Suitability'] = np.round(preds, 1)
    shap_vals = explainer.shap_values(X_input)

    eval_df['orig_idx'] = range(len(eval_df))
    top_candidates = eval_df.sort_values(by='Base_Suitability', ascending=False).head(req.top_k).copy()

    recommendations = []
    for _, row in top_candidates.iterrows():
        idx = int(row['orig_idx'])
        row_shap = shap_vals[idx]
        t_name = row['Trail_Name']

        social_info = fetch_live_social_data(
            t_name, str(row['Social_Search_Query']), force_refresh=req.refresh_social
        )

        social_adjustment = (social_info["sentiment_score"] - 0.75) * 6.0 - social_info["hazard_penalty"]
        final_suitability = round(float(np.clip(row['Base_Suitability'] + social_adjustment, 5.0, 99.5)), 1)

        shap_pairs = list(zip(FEATURE_COLS, row_shap))
        shap_pairs.sort(key=lambda x: abs(x[1]), reverse=True)
        top_shap = shap_pairs[:5]

        shap_breakdown = []
        for feat_name, s_val in top_shap:
            shap_breakdown.append({
                "feature": FEATURE_LABELS.get(feat_name, feat_name),
                "impact_score": round(float(s_val), 2),
                "positive": bool(s_val >= 0)
            })

        pos_reasons = []
        neg_reasons = []
        used_categories = set()

        for feat_name, s_val in shap_pairs:
            if abs(s_val) < 0.3:
                continue
            is_pos = s_val >= 0

            if feat_name in ['Fitness_Difficulty_Gap', 'Trail_Diff_Score', 'User_Fitness_Score']:
                if 'fitness' in used_categories:
                    continue
                used_categories.add('fitness')
                if row['Fitness_Difficulty_Gap'] >= 0:
                    pos_reasons.append(f"its {row['Base_Difficulty'].lower()} difficulty matches well with your {fitness_level.lower()} fitness level")
                else:
                    neg_reasons.append(f"its {row['Base_Difficulty'].lower()} terrain may feel demanding for your {fitness_level.lower()} fitness level")

            elif feat_name in ['Duration_Diff_Hours', 'Avg_Completion_Time_Hours', 'Pref_Max_Hours']:
                if 'duration' in used_categories:
                    continue
                used_categories.add('duration')
                if row['Duration_Diff_Hours'] >= 0:
                    pos_reasons.append(f"the {row['Avg_Completion_Time_Hours']}-hour hike fits comfortably within your {preferred_max_hours:g}-hour limit")
                else:
                    neg_reasons.append(f"the {row['Avg_Completion_Time_Hours']}-hour hike exceeds your preferred {preferred_max_hours:g}-hour duration")

            elif feat_name == 'Scenic_Match_Ratio':
                if 'scenic' in used_categories:
                    continue
                used_categories.add('scenic')
                pct = int(row['Scenic_Match_Ratio'] * 100)
                if is_pos and pct > 0:
                    pos_reasons.append(f"it includes {pct}% of your favorite scenery ({row['Scenic_Features']})")

            elif feat_name == 'Elevation_Gain_M':
                if 'elevation' in used_categories:
                    continue
                used_categories.add('elevation')
                if is_pos:
                    pos_reasons.append(f"the gentle {int(row['Elevation_Gain_M'])}m elevation gain is very comfortable")
                else:
                    neg_reasons.append(f"the steep {int(row['Elevation_Gain_M'])}m elevation gain requires extra effort")

            elif feat_name == 'Distance_KM':
                if 'distance' in used_categories:
                    continue
                used_categories.add('distance')
                if is_pos:
                    pos_reasons.append(f"the {row['Distance_KM']} km distance suits your pace")
                else:
                    neg_reasons.append(f"the {row['Distance_KM']} km total distance requires steady endurance")

            elif feat_name in ['Medical_Risk_Flag', 'Has_Medical_Issue'] and not is_pos:
                if 'medical' not in used_categories:
                    used_categories.add('medical')
                    neg_reasons.append("extra caution is advised due to high elevation and your medical condition")

        if pos_reasons:
            main_text = f"This trail is a {final_suitability}% match for you primarily because " + " and ".join(pos_reasons[:2]) + "."
        else:
            main_text = f"This trail has a {final_suitability}% suitability score based on your registered profile."

        if neg_reasons:
            main_text += f" However, note that {neg_reasons[0]}."
        elif row['Is_Steep_Rock'] == 1:
            main_text += " Note: Expect some rocky or steep sections along the trail."

        route_geo = build_route_geometry_from_csv(row)

        recommendations.append({
            "trail_id": row['Trail_ID'],
            "trail_name": t_name,
            "region": row['Region'],
            "difficulty": row['Base_Difficulty'],
            "distance_km": float(row['Distance_KM']),
            "elevation_m": int(row['Elevation_Gain_M']),
            "duration_hours": float(row['Avg_Completion_Time_Hours']),
            "scenic_features": row['Scenic_Features'],
            "terrain_type": row['Terrain_Type'],
            "suitability_score": final_suitability,
            "enjoyment_score": round(min(99.0, float(final_suitability * 0.90 + social_info['sentiment_score'] * 9.5)), 1),
            "completion_likelihood": round(min(99.0, max(40.0, 85.0 + row['Fitness_Difficulty_Gap'] * 10)), 1),
            "justification": main_text,
            "shap_explanation": shap_breakdown,
            "social_metadata": social_info,
            "route_geometry": route_geo
        })

    recommendations.sort(key=lambda x: x["suitability_score"], reverse=True)
    for i, item in enumerate(recommendations, start=1):
        item["rank"] = i
        
    end_time = time.time()
    latency = round(end_time - start_time, 4)
    print(f"System Latency: {latency} seconds")

    return {
        "user_summary": user,
        "recommendations": recommendations,
        "processing_time_seconds": latency
    }