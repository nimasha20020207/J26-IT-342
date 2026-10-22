import os
import pandas as pd
import numpy as np

BASE_DIR = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
PROJECT_ROOT = os.path.dirname(os.path.dirname(BASE_DIR))

RAW_DATA_DIR = os.path.join(PROJECT_ROOT, 'datasets', 'component01', 'raw')
PROCESSED_DATA_DIR = os.path.join(PROJECT_ROOT, 'datasets', 'component01', 'processed')

# 1. Datasets Load 
users_df = pd.read_csv(os.path.join(RAW_DATA_DIR, 'Hiking Trail Preference & Fitness Assessment Survey.csv'))
trails_df = pd.read_csv(os.path.join(RAW_DATA_DIR, 'hiking_trails_sri_lanka.csv'))

# 2. Categorical දත්ත අංක බවට හැරවීමේ Functions (Encoding)
def map_fitness(val):
    if 'Low' in str(val): return 1
    elif 'Moderate' in str(val): return 2
    elif 'High' in str(val): return 3
    return 2

def map_experience(val):
    if 'Beginner' in str(val): return 1
    elif 'Intermediate' in str(val): return 2
    elif 'Expert' in str(val): return 3
    return 1

def map_duration_max(val):
    if 'Short' in str(val): return 3.0
    elif 'Medium' in str(val): return 6.0
    elif 'Full Day' in str(val): return 10.0
    return 6.0

def map_difficulty(val):
    return {'Easy': 1, 'Moderate': 2, 'Hard': 3}.get(val, 2)

def extract_scenic_tags(val):
    if pd.isna(val): return set()
    tags = set()
    s = str(val)
    for keyword in ['Waterfalls', 'Dense Forests', 'Panoramic Mountain Views', 'Caves', 'Tea Estates', 'Historic / Cultural Sites']:
        if keyword in s or (keyword == 'Dense Forests' and 'Forest' in s):
            tags.add(keyword)
    return tags

# 3. User සහ Trail features සකස් කිරීම
users_df['User_ID'] = [f"U{i+1:03d}" for i in range(len(users_df))]
users_df['User_Age'] = users_df['02. Age 🎂 ']
users_df['User_Fitness_Score'] = users_df['01. Fitness Level 💪  '].apply(map_fitness)
users_df['User_Exp_Score'] = users_df['02. Hiking Experience Level 🥾  '].apply(map_experience)
users_df['Has_Medical_Issue'] = users_df['03. Medical Conditions / Physical Limitations🩺'].notna().astype(int)
users_df['Pref_Max_Hours'] = users_df['02. Preferred Hiking Duration ⏱️  '].apply(map_duration_max)
users_df['User_Scenic_Set'] = users_df['01. Preferred Scenic Features 🏞️  '].apply(extract_scenic_tags)

trails_df['Trail_Diff_Score'] = trails_df['Base_Difficulty'].apply(map_difficulty)
trails_df['Trail_Scenic_Set'] = trails_df['Scenic_Features'].apply(extract_scenic_tags)
trails_df['Is_Steep_Rock'] = trails_df['Terrain_Type'].apply(lambda x: 1 if any(w in str(x) for w in ['Steep', 'Rock', 'Boulder']) else 0)

# 4. User-Trail Interactions (500 x 24 = 12,000 rows) ගොඩනැගීම
interactions = []
np.random.seed(42)

for _, u in users_df.iterrows():
    for _, t in trails_df.iterrows():
        user_cap = (u['User_Fitness_Score'] * 0.6) + (u['User_Exp_Score'] * 0.4)
        fitness_diff_gap = user_cap - t['Trail_Diff_Score']
        duration_diff = u['Pref_Max_Hours'] - t['Avg_Completion_Time_Hours']
        
        t_scenic, u_scenic = t['Trail_Scenic_Set'], u['User_Scenic_Set']
        scenic_overlap = len(u_scenic.intersection(t_scenic)) / max(len(t_scenic), 1)
        
        medical_risk_penalty = 1 if (u['Has_Medical_Issue'] == 1 and (t['Trail_Diff_Score'] == 3 or t['Elevation_Gain_M'] > 500)) else 0
        
        # Suitability Score (0 - 100%) ගණනය කිරීම
        base_score = 70.0
        fit_impact = (15.0 - (fitness_diff_gap * 3.0)) if fitness_diff_gap >= 0 else (fitness_diff_gap * 22.0)
        dur_impact = (10.0 - min(duration_diff * 1.2, 6.0)) if duration_diff >= 0 else (duration_diff * 8.0)
        scenic_impact = scenic_overlap * 15.0
        strain_penalty = max(0, (t['Elevation_Gain_M'] / 100.0) - (u['User_Fitness_Score'] * 2.5)) * 2.5
        med_impact = -25.0 if medical_risk_penalty == 1 else 0.0
        
        suitability_score = np.clip(base_score + fit_impact + dur_impact + scenic_impact - strain_penalty + med_impact + np.random.normal(0, 1.5), 5.0, 99.0)
        
        interactions.append({
            'User_ID': u['User_ID'],
            'Trail_ID': t['Trail_ID'],
            'Trail_Name': t['Trail_Name'],
            'User_Age': u['User_Age'],
            'User_Fitness_Score': u['User_Fitness_Score'],
            'User_Exp_Score': u['User_Exp_Score'],
            'Has_Medical_Issue': u['Has_Medical_Issue'],
            'Pref_Max_Hours': u['Pref_Max_Hours'],
            'Distance_KM': t['Distance_KM'],
            'Elevation_Gain_M': t['Elevation_Gain_M'],
            'Avg_Completion_Time_Hours': t['Avg_Completion_Time_Hours'],
            'Trail_Diff_Score': t['Trail_Diff_Score'],
            'Is_Steep_Rock': t['Is_Steep_Rock'],
            'Fitness_Difficulty_Gap': round(fitness_diff_gap, 2),
            'Duration_Diff_Hours': round(duration_diff, 2),
            'Scenic_Match_Ratio': round(scenic_overlap, 2),
            'Medical_Risk_Flag': medical_risk_penalty,
            'Suitability_Score': round(suitability_score, 2)
        })

fe_df = pd.DataFrame(interactions)
os.makedirs(PROCESSED_DATA_DIR, exist_ok=True)
fe_df.to_csv(os.path.join(PROCESSED_DATA_DIR, 'engineered_user_trail_dataset.csv'), index=False)
print("Saved engineered_user_trail_dataset.csv with shape:", fe_df.shape)