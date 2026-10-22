# Component 02 model evaluation

Install the model dependencies and run the baseline evaluation from the
repository root:

```powershell
python -m pip install -r ML_models/component02/requirements.txt
python ML_models/component02/train_baseline_models.py
```

The evaluation uses the held-out test split and saves an interactive Plotly
report to `ML_models/component02/outputs/model_evaluation_visualizations.html`.
The report includes a color-coded scorecard with the exact classification and
risk-error values, plus detailed metric charts and F1 changes from the ablation
analysis. Scorecard colors show relative performance per metric (green is
better; for MAE and RMSE, lower errors are better). Open the HTML report in a
browser after the script finishes.
