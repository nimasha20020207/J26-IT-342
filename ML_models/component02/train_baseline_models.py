"""
train_baseline_models.py
------------------------
Component 02: Model Training, Baseline Comparison, and Ablation Evaluation

Trains machine learning models across the three research baseline settings:
1. Baseline 01: Environmental Data Only
2. Baseline 02: Conventional Fixed Multi-Source Fusion
3. Baseline 03: Proposed Reliability-Aware Adaptive Multi-Source Fusion

Evaluates:
- Hazard Classification (Accuracy, Precision, Recall, F1-Score, ROC-AUC)
- Risk Score Regression (MAE, RMSE)
- Ablation Performance Drops (Figure 3.3 in Proposal)
- Saves trained models, evaluation summary tables, and interactive test-set charts.
"""

import json
from pathlib import Path
import joblib
import numpy as np
import pandas as pd
from sklearn.ensemble import (
    GradientBoostingClassifier,
    GradientBoostingRegressor,
    RandomForestClassifier,
    RandomForestRegressor,
)
from sklearn.metrics import (
    accuracy_score,
    f1_score,
    mean_absolute_error,
    precision_score,
    recall_score,
    roc_auc_score,
    root_mean_squared_error,
)
from sklearn.preprocessing import LabelEncoder
import plotly.graph_objects as go
from plotly.subplots import make_subplots

ROOT = Path(__file__).resolve().parent
OUTPUT_DIR = ROOT / "outputs"
MODELS_DIR = ROOT / "models" / "saved_baselines"
VISUALIZATIONS_PATH = OUTPUT_DIR / "model_evaluation_visualizations.html"
MODELS_DIR.mkdir(parents=True, exist_ok=True)

# Non-feature metadata columns to exclude from training
EXCLUDE_COLS = [
    "date",
    "trail_name",
    "hazard_type",
    "severity",
    "risk_score",
    "is_hazard",
    "split",
]


def save_evaluation_visualizations(class_df, reg_df, ablation_summary):
    """Save interactive comparisons for the held-out test-set metrics."""
    baseline_labels = [
        "Baseline 01<br>Environmental only",
        "Baseline 02<br>Fixed fusion",
        "Baseline 03<br>Adaptive fusion",
    ]
    class_metrics = [
        ("Accuracy", "Accuracy"),
        ("Precision (Weighted)", "Weighted precision"),
        ("Recall (Weighted)", "Weighted recall"),
        ("F1-Score (Weighted)", "Weighted F1"),
        ("ROC-AUC", "ROC-AUC"),
    ]
    regression_metrics = [
        ("MAE (Risk Score)", "MAE"),
        ("RMSE (Risk Score)", "RMSE"),
    ]

    fig = make_subplots(
        rows=4,
        cols=1,
        specs=[
            [{"type": "heatmap"}],
            [{"type": "bar"}],
            [{"type": "bar"}],
            [{"type": "bar"}],
        ],
        subplot_titles=(
            "Test results scorecard - exact values",
            "Hazard classification metrics",
            "Risk-score prediction error",
            "Ablation impact on weighted F1",
        ),
        vertical_spacing=0.12,
    )

    results_df = class_df.merge(reg_df, on="Setting")
    scorecard_columns = [
        "Accuracy",
        "F1-Score (Weighted)",
        "ROC-AUC",
        "MAE (Risk Score)",
        "RMSE (Risk Score)",
    ]
    scorecard_labels = [
        "Accuracy",
        "Weighted F1",
        "ROC-AUC",
        "Risk MAE",
        "Risk RMSE",
    ]
    raw_scores = results_df[scorecard_columns].to_numpy(dtype=float)
    better_is_higher = np.array([True, True, True, False, False])
    relative_scores = np.zeros_like(raw_scores)
    for column_index, higher_is_better in enumerate(better_is_higher):
        column = raw_scores[:, column_index]
        minimum, maximum = column.min(), column.max()
        if maximum == minimum:
            relative_scores[:, column_index] = 0.5
        elif higher_is_better:
            relative_scores[:, column_index] = (column - minimum) / (maximum - minimum)
        else:
            relative_scores[:, column_index] = (maximum - column) / (maximum - minimum)

    fig.add_trace(
        go.Heatmap(
            z=relative_scores,
            x=scorecard_labels,
            y=baseline_labels,
            text=[[f"{value:.4f}" for value in row] for row in raw_scores],
            customdata=raw_scores,
            colorscale="RdYlGn",
            zmin=0,
            zmax=1,
            showscale=False,
            hovertemplate=(
                "%{y}<br>%{x}: %{customdata:.4f}"
                "<br>Relative result: %{z:.0%}<extra></extra>"
            ),
        ),
        row=1,
        col=1,
    )
    fig.update_traces(
        texttemplate="%{text}",
        textfont_size=14,
        selector={"type": "heatmap"},
    )

    for column, label in class_metrics:
        fig.add_trace(
            go.Bar(
                name=label,
                x=baseline_labels,
                y=class_df[column],
                customdata=class_df["Setting"],
                hovertemplate="%{customdata}<br>" + label + ": %{y:.3f}<extra></extra>",
            ),
            row=2,
            col=1,
        )

    for column, label in regression_metrics:
        fig.add_trace(
            go.Bar(
                name=label,
                x=baseline_labels,
                y=reg_df[column],
                customdata=reg_df["Setting"],
                hovertemplate="%{customdata}<br>" + label + ": %{y:.2f}<extra></extra>",
            ),
            row=3,
            col=1,
        )

    fig.add_trace(
        go.Bar(
            name="F1 change",
            orientation="h",
            x=[
                ablation_summary["reliability_assessment_gain_f1"],
                ablation_summary["total_fusion_gain_f1"],
            ],
            y=[
                "Adaptive vs. fixed fusion",
                "Adaptive vs. environmental only",
            ],
            marker_color=["#d95f59", "#2a9d8f"],
            hovertemplate="%{y}<br>F1 change: %{x:+.4f}<extra></extra>",
        ),
        row=4,
        col=1,
    )
    fig.add_vline(x=0, line_color="#555", line_width=1, row=4, col=1)
    fig.add_annotation(
        text=(
            "Adaptive fusion MAE reduction vs. environmental only: "
            f"{ablation_summary['mae_error_reduction_pct']:.2f}%"
        ),
        xref="paper",
        yref="paper",
        x=1,
        y=0.01,
        showarrow=False,
        xanchor="right",
    )
    fig.update_layout(
        title="Baseline Model Evaluation - Held-out Test Set",
        barmode="group",
        height=1400,
        template="plotly_white",
        legend_title_text="Metric",
        margin=dict(l=170, r=40, t=100, b=90),
    )
    fig.update_xaxes(side="top", row=1, col=1)
    fig.update_yaxes(autorange="reversed", row=1, col=1)
    fig.update_yaxes(title_text="Score", range=[0, 1.05], row=2, col=1)
    fig.update_yaxes(title_text="Error (risk-score points)", row=3, col=1)
    fig.update_xaxes(title_text="F1 change (absolute points)", row=4, col=1)
    fig.write_html(VISUALIZATIONS_PATH, include_plotlyjs=True)
    print(f"\nInteractive test-set visualizations saved to: {VISUALIZATIONS_PATH}")


def train_and_evaluate_baselines():
    print("=" * 70)
    print("THREE BASELINE MODELS: TRAINING & COMPARATIVE EVALUATION")
    print("=" * 70)

    # 1. Load Baseline Datasets
    b1_path = OUTPUT_DIR / "dataset_baseline1_env.csv"
    b2_path = OUTPUT_DIR / "dataset_baseline2_fixed.csv"
    b3_path = OUTPUT_DIR / "dataset_baseline3_adaptive.csv"

    b1_df = pd.read_csv(b1_path, low_memory=False)
    b2_df = pd.read_csv(b2_path, low_memory=False)
    b3_df = pd.read_csv(b3_path, low_memory=False)

    datasets = {
        "Baseline 01 (Environmental Only)": b1_df,
        "Baseline 02 (Fixed Multi-Source Fusion)": b2_df,
        "Baseline 03 (Proposed Reliability-Aware Adaptive Fusion)": b3_df,
    }

    # Prepare common labels and time-aware split mask
    train_mask = b1_df["split"] == "train"
    test_mask = b1_df["split"] == "test"

    print(f"\nTime-Aware Split: {train_mask.sum()} Train samples | {test_mask.sum()} Test samples")

    # Encode multi-class hazard category
    le = LabelEncoder()
    # Fit label encoder on all hazard types
    all_hazard_types = b1_df["hazard_type"].astype(str).tolist()
    le.fit(all_hazard_types)

    y_train_cat = le.transform(b1_df.loc[train_mask, "hazard_type"].astype(str))
    y_test_cat = le.transform(b1_df.loc[test_mask, "hazard_type"].astype(str))

    # Binary hazard indicator (0 = Calm / No Hazard, 1 = Hazard)
    y_train_bin = b1_df.loc[train_mask, "is_hazard"].values
    y_test_bin = b1_df.loc[test_mask, "is_hazard"].values

    # Continuous Risk Score (0 - 100)
    y_train_risk = b1_df.loc[train_mask, "risk_score"].values
    y_test_risk = b1_df.loc[test_mask, "risk_score"].values

    classification_results = []
    regression_results = []

    trained_models = {}

    for name, df in datasets.items():
        print(f"\n>>> Evaluating: {name} <<<")
        # Extract features
        feature_cols = [c for c in df.columns if c not in EXCLUDE_COLS]
        print(f"Feature count: {len(feature_cols)}")

        X_train = df.loc[train_mask, feature_cols].fillna(0)
        X_test = df.loc[test_mask, feature_cols].fillna(0)

        # -------------------------------------------------------------
        # 1. HAZARD CLASSIFICATION (Random Forest & Gradient Boosting)
        # -------------------------------------------------------------
        clf = RandomForestClassifier(n_estimators=100, max_depth=8, random_state=42)
        clf.fit(X_train, y_train_cat)
        preds_cat = clf.predict(X_test)
        prob_cat = clf.predict_proba(X_test)

        acc = accuracy_score(y_test_cat, preds_cat)
        prec = precision_score(y_test_cat, preds_cat, average="weighted", zero_division=0)
        rec = recall_score(y_test_cat, preds_cat, average="weighted", zero_division=0)
        f1 = f1_score(y_test_cat, preds_cat, average="weighted", zero_division=0)

        # Binary Hazard Detection Model for ROC-AUC
        bin_clf = GradientBoostingClassifier(n_estimators=100, max_depth=4, random_state=42)
        bin_clf.fit(X_train, y_train_bin)
        preds_bin = bin_clf.predict_proba(X_test)[:, 1]
        auc = roc_auc_score(y_test_bin, preds_bin)

        classification_results.append({
            "Setting": name,
            "Accuracy": round(acc, 4),
            "Precision (Weighted)": round(prec, 4),
            "Recall (Weighted)": round(rec, 4),
            "F1-Score (Weighted)": round(f1, 4),
            "ROC-AUC": round(auc, 4),
        })

        # -------------------------------------------------------------
        # 2. RISK SCORE REGRESSION (Gradient Boosting Regressor)
        # -------------------------------------------------------------
        reg = GradientBoostingRegressor(n_estimators=100, max_depth=4, random_state=42)
        reg.fit(X_train, y_train_risk)
        preds_risk = reg.predict(X_test)

        mae = mean_absolute_error(y_test_risk, preds_risk)
        rmse = root_mean_squared_error(y_test_risk, preds_risk)

        regression_results.append({
            "Setting": name,
            "MAE (Risk Score)": round(mae, 4),
            "RMSE (Risk Score)": round(rmse, 4),
        })

        # Save model objects
        slug = name.split()[0].lower() + "_" + name.split()[1].replace("(", "").replace(")", "").lower()
        joblib.dump(clf, MODELS_DIR / f"{slug}_hazard_classifier.pkl")
        joblib.dump(bin_clf, MODELS_DIR / f"{slug}_binary_detector.pkl")
        joblib.dump(reg, MODELS_DIR / f"{slug}_risk_regressor.pkl")

    joblib.dump(le, MODELS_DIR / "label_encoder.pkl")

    # -------------------------------------------------------------
    # 3. COMPILE COMPARATIVE TABLES (Table 3.6 & 3.7)
    # -------------------------------------------------------------
    class_df = pd.DataFrame(classification_results)
    reg_df = pd.DataFrame(regression_results)

    # Save to outputs
    class_df.to_csv(OUTPUT_DIR / "baseline_classification_results.csv", index=False)
    reg_df.to_csv(OUTPUT_DIR / "baseline_regression_results.csv", index=False)

    print("\n" + "=" * 75)
    print("TABLE 3.6: HAZARD FORECASTING CLASSIFICATION COMPARISON")
    print("=" * 75)
    print(class_df.to_string(index=False))

    print("\n" + "=" * 75)
    print("TABLE 3.7: RISK SCORE & TREND REGRESSION COMPARISON")
    print("=" * 75)
    print(reg_df.to_string(index=False))

    # -------------------------------------------------------------
    # 4. ABLATION ANALYSIS (Figure 3.3 in Proposal)
    # -------------------------------------------------------------
    print("\n" + "=" * 75)
    print("ABLATION STUDY: QUANTIFYING SCIENTIFIC CONTRIBUTION")
    print("=" * 75)

    b3_f1 = class_df.loc[class_df["Setting"].str.contains("Baseline 03"), "F1-Score (Weighted)"].values[0]
    b2_f1 = class_df.loc[class_df["Setting"].str.contains("Baseline 02"), "F1-Score (Weighted)"].values[0]
    b1_f1 = class_df.loc[class_df["Setting"].str.contains("Baseline 01"), "F1-Score (Weighted)"].values[0]

    b3_auc = class_df.loc[class_df["Setting"].str.contains("Baseline 03"), "ROC-AUC"].values[0]
    b2_auc = class_df.loc[class_df["Setting"].str.contains("Baseline 02"), "ROC-AUC"].values[0]
    b1_auc = class_df.loc[class_df["Setting"].str.contains("Baseline 01"), "ROC-AUC"].values[0]

    b3_mae = reg_df.loc[reg_df["Setting"].str.contains("Baseline 03"), "MAE (Risk Score)"].values[0]
    b1_mae = reg_df.loc[reg_df["Setting"].str.contains("Baseline 01"), "MAE (Risk Score)"].values[0]

    rel_module_contrib = (b3_f1 - b2_f1)
    fusion_contrib = (b3_f1 - b1_f1)
    error_reduction = ((b1_mae - b3_mae) / b1_mae) * 100

    print(f"1. Contribution of Reliability Assessment Module (B3 F1 - B2 F1): {rel_module_contrib:+.4f} F1")
    print(f"2. Overall Multi-Source Fusion Improvement over Env Only (B3 F1 - B1 F1): {fusion_contrib:+.4f} F1")
    print(f"3. ROC-AUC Gain over Environmental Only: +{(b3_auc - b1_auc):.4f}")
    print(f"4. Risk Score Prediction Error Reduction: {error_reduction:.2f}% reduction in MAE")

    ablation_summary = {
        "proposed_f1": b3_f1,
        "fixed_fusion_f1": b2_f1,
        "env_only_f1": b1_f1,
        "reliability_assessment_gain_f1": rel_module_contrib,
        "total_fusion_gain_f1": fusion_contrib,
        "mae_error_reduction_pct": error_reduction,
    }

    with open(OUTPUT_DIR / "ablation_summary.json", "w") as f:
        json.dump(ablation_summary, f, indent=2)

    save_evaluation_visualizations(class_df, reg_df, ablation_summary)

    print("\nAll baseline models trained, evaluated, and saved to models/saved_baselines/.")
    return class_df, reg_df


if __name__ == "__main__":
    train_and_evaluate_baselines()
