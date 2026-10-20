"""
Component 4 baseline ML training.
IMPORTANT: data/synthetic_emergency_incidents.csv is synthetic demo data, not real accident evidence.
Run from project root: python src/train_models.py
"""
from pathlib import Path
import json, joblib
import pandas as pd
from sklearn.model_selection import train_test_split
from sklearn.compose import ColumnTransformer
from sklearn.preprocessing import OneHotEncoder
from sklearn.pipeline import Pipeline
from sklearn.impute import SimpleImputer
from sklearn.ensemble import RandomForestClassifier, RandomForestRegressor
from sklearn.metrics import classification_report, confusion_matrix, mean_absolute_error, mean_squared_error, r2_score
from sklearn.feature_extraction.text import TfidfVectorizer
from sklearn.linear_model import LogisticRegression

ROOT = Path(__file__).resolve().parents[1]
DATA = ROOT / "data"
MODELS = ROOT / "models"
REPORTS = ROOT / "reports"
MODELS.mkdir(exist_ok=True); REPORTS.mkdir(exist_ok=True)

df = pd.read_csv(DATA / "synthetic_emergency_incidents.csv")
# Keep synthetic rows grouped out of real-world evaluation. This demo split only demonstrates workflow.
features = [
    "elevation_m","slope_degrees","rainfall_mm","temperature_c","wind_speed_kmh",
    "visibility_pct","hours_hiking","distance_from_trailhead_km","phone_battery_pct",
    "fatigue_score_1_10","water_remaining_l","remote_area","terrain_type"
]
X = df[features].copy()
y = df["emergency_type"]
cat = ["terrain_type"]
num = [c for c in features if c not in cat]
pre = ColumnTransformer([
    ("num", Pipeline([("imputer", SimpleImputer(strategy="median"))]), num),
    ("cat", Pipeline([("imputer", SimpleImputer(strategy="most_frequent")),
                      ("onehot", OneHotEncoder(handle_unknown="ignore"))]), cat)
])
X_train, X_test, y_train, y_test = train_test_split(
    X, y, test_size=0.20, random_state=42, stratify=y
)
clf = Pipeline([("preprocess", pre), ("model", RandomForestClassifier(
    n_estimators=300, class_weight="balanced", random_state=42, min_samples_leaf=2
))])
clf.fit(X_train, y_train)
pred = clf.predict(X_test)
with open(REPORTS/"emergency_classification_report.json","w") as f:
    json.dump(classification_report(y_test,pred,output_dict=True,zero_division=0),f,indent=2)
with open(REPORTS/"emergency_confusion_matrix.json","w") as f:
    json.dump({"labels":list(clf.classes_),"matrix":confusion_matrix(y_test,pred,labels=clf.classes_).tolist()},f,indent=2)
joblib.dump(clf, MODELS/"emergency_classifier.joblib")

# Severity model: ordinal label treated as numeric baseline; evaluate MAE/RMSE/R2.
ys = df["severity_level"]
Xs_train, Xs_test, ys_train, ys_test = train_test_split(
    X, ys, test_size=0.20, random_state=42
)
sev = Pipeline([("preprocess", pre), ("model", RandomForestRegressor(
    n_estimators=300, random_state=42, min_samples_leaf=2
))])
sev.fit(Xs_train, ys_train)
sev_pred = sev.predict(Xs_test)
severity_metrics = {
    "MAE": float(mean_absolute_error(ys_test, sev_pred)),
    "RMSE": float(mean_squared_error(ys_test, sev_pred) ** 0.5),
    "R2": float(r2_score(ys_test, sev_pred))
}
(REPORTS/"severity_metrics.json").write_text(json.dumps(severity_metrics,indent=2))
joblib.dump(sev, MODELS/"severity_regressor.joblib")

# NLP baseline: TF-IDF + logistic regression on synthetic report text.
text_df = df[["incident_text","emergency_type"]].dropna()
Xt_train, Xt_test, yt_train, yt_test = train_test_split(
    text_df["incident_text"], text_df["emergency_type"],
    test_size=0.20, random_state=42, stratify=text_df["emergency_type"]
)
nlp = Pipeline([("tfidf", TfidfVectorizer(ngram_range=(1,2), max_features=10000)),
                ("model", LogisticRegression(max_iter=1500, class_weight="balanced"))])
nlp.fit(Xt_train, yt_train)
nlp_pred = nlp.predict(Xt_test)
nlp_report = classification_report(yt_test,nlp_pred,output_dict=True,zero_division=0)
(REPORTS/"nlp_classification_report.json").write_text(json.dumps(nlp_report,indent=2))
joblib.dump(nlp, MODELS/"incident_text_classifier.joblib")

print("Training complete. Metrics saved to reports/.")
print("Research warning: scores from synthetic data are not evidence of real-world performance.")
