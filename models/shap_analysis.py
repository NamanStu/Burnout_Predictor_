import joblib
import numpy as np
import matplotlib.pyplot as plt
import json

try:
    import shap
    
    best_name    = 'logisticregression'   # Updated to actual best model
    model        = joblib.load(f'models/{best_name}.pkl')
    feature_names= joblib.load('models/feature_names.pkl')
    X_test       = np.load('data/X_test.npy')

    explainer   = shap.Explainer(model, X_test)
    shap_values = explainer(X_test)

    # ── Plot 1: Bar chart (feature importance) ────────────
    fig, ax = plt.subplots(figsize=(10, 6))
    shap.summary_plot(shap_values, X_test, feature_names=feature_names,
                      plot_type='bar', show=False)
    plt.tight_layout()
    plt.savefig('visuals/shap_bar.png', dpi=150, bbox_inches='tight')
    plt.close()
    print("✅ SHAP bar plot saved")

    # ── Plot 2: Beeswarm summary (global) ────────────────
    fig, ax = plt.subplots(figsize=(10, 8))
    shap.summary_plot(shap_values, X_test, feature_names=feature_names,
                      show=False)
    plt.tight_layout()
    plt.savefig('visuals/shap_summary.png', dpi=150, bbox_inches='tight')
    plt.close()
    print("✅ SHAP summary plot saved")

    print("✅ All SHAP plots generated successfully!")
    
except Exception as e:
    print(f"⚠️  SHAP analysis skipped (optional): {e}")
    print("Proceeding without SHAP visuals - models are ready to use!")

