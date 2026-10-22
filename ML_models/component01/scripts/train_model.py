import os
import pandas as pd
import numpy as np
import xgboost as xgb
import shap
from sklearn.model_selection import train_test_split
from sklearn.metrics import mean_squared_error, mean_absolute_error, r2_score
import matplotlib.pyplot as plt
import joblib

BASE_DIR = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
PROJECT_ROOT = os.path.dirname(os.path.dirname(BASE_DIR))

PROCESSED_DATA_PATH = os.path.join(PROJECT_ROOT, 'datasets', 'component01', 'processed', 'engineered_user_trail_dataset.csv')
MODEL_PATH = os.path.join(BASE_DIR, 'models', 'xgboost_trail_model.pkl')

PLOTS_DIR = os.path.join(BASE_DIR, 'outputs', 'plots')

# 1. Engineered Dataset Load 
df = pd.read_csv(PROCESSED_DATA_PATH)

# 2. Model එකට දෙන Features (X) සහ Target එක (y) තෝරාගැනීම
feature_cols = [
    'User_Age', 'User_Fitness_Score', 'User_Exp_Score', 'Has_Medical_Issue',
    'Pref_Max_Hours', 'Distance_KM', 'Elevation_Gain_M', 'Avg_Completion_Time_Hours',
    'Trail_Diff_Score', 'Is_Steep_Rock', 'Fitness_Difficulty_Gap',
    'Duration_Diff_Hours', 'Scenic_Match_Ratio', 'Medical_Risk_Flag'
]

X = df[feature_cols]
y = df['Suitability_Score']

# 3. Data ටික Train (80%) සහ Test (20%) ලෙස බෙදීම
X_train, X_test, y_train, y_test = train_test_split(X, y, test_size=0.2, random_state=42)

# 4. XGBoost Model Train 
print("Training XGBoost Model...")
model = xgb.XGBRegressor(
    n_estimators=200,
    learning_rate=0.08,
    max_depth=6,
    subsample=0.8,
    colsample_bytree=0.8,
    random_state=42
)
model.fit(X_train, y_train)

# 5. Model Accuracy 
y_pred = model.predict(X_test)
rmse = np.sqrt(mean_squared_error(y_test, y_pred))
mae = mean_absolute_error(y_test, y_pred)
r2 = r2_score(y_test, y_pred)

print(f"\n--- Model Evaluation ---")
print(f"RMSE : {rmse:.4f}")
print(f"MAE  : {mae:.4f}")
print(f"R2   : {r2:.4f}")

# 6. Flutter App එකේ Backend API එකට ගන්න Model එක Save කිරීම
os.makedirs(os.path.dirname(MODEL_PATH), exist_ok=True)
joblib.dump(model, MODEL_PATH)
print("\nSaved trained model as 'xgboost_trail_model.pkl'")

# 7. SHAP Explainability (XAI) 
print("Generating SHAP Explanations...")
explainer = shap.TreeExplainer(model)
shap_values = explainer(X_test)

# Save SHAP Global Summary Plot 
os.makedirs(PLOTS_DIR, exist_ok=True)
plt.figure(figsize=(10, 6))
shap.summary_plot(shap_values, X_test, show=False)
plt.title("SHAP Summary Plot - Feature Impact on Trail Suitability", fontsize=13)
plt.tight_layout()
plt.savefig(os.path.join(PLOTS_DIR, 'shap_summary_plot.png'), dpi=150)
plt.close()
print("Saved 'shap_summary_plot.png'")

