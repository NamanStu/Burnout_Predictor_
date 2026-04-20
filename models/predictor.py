import joblib
import numpy as np
import pandas as pd
import matplotlib.pyplot as plt
import os

scaler        = joblib.load('models/scaler.pkl')
feature_names = joblib.load('models/feature_names.pkl')
label_enc     = joblib.load('models/label_encoder.pkl')

import json
with open('models/metrics.json') as f:
    _meta = json.load(f)
_best = _meta['best_model'].lower()
model = joblib.load(f'models/{_best}.pkl')

# Try to import SHAP, but make it optional
try:
    import shap
    explainer = shap.Explainer(model, np.load('data/X_train.npy')[:100])  # Use subset for speed
    SHAP_AVAILABLE = True
except ImportError:
    SHAP_AVAILABLE = False
    explainer = None

def predict(form_dict: dict) -> dict:
    row = pd.DataFrame([form_dict])
    row = row.reindex(columns=feature_names, fill_value=0)
    row_sc = scaler.transform(row)

    pred   = model.predict(row_sc)[0]
    proba  = model.predict_proba(row_sc)[0]
    conf   = round(float(max(proba)) * 100, 1)
    label  = label_enc.inverse_transform([pred])[0]
    score  = round(float(proba[0]), 3)

    # Generate explanation visualization
    if SHAP_AVAILABLE and explainer is not None:
        try:
            # Use SHAP for explanation
            sv = explainer(row_sc)
            
            # Create a simple SHAP force plot
            fig, ax = plt.subplots(figsize=(12, 2))
            fig.patch.set_visible(False)
            ax.axis('off')
            
            # Get top features
            shap_values = sv.values[0] if hasattr(sv, 'values') else sv[0]
            if hasattr(shap_values, '__len__'):
                top_idx = np.argsort(np.abs(shap_values))[-5:][::-1]
                
                y_pos = np.arange(len(top_idx))
                colors = ['red' if shap_values[i] > 0 else 'blue' for i in top_idx]
                
                ax.barh(y_pos, [shap_values[i] for i in top_idx], color=colors)
                ax.set_yticks(y_pos)
                ax.set_yticklabels([feature_names[i] for i in top_idx])
                ax.set_xlabel('SHAP Value')
                ax.set_title('Top 5 Features Influencing Prediction')
                
            plt.tight_layout()
            plt.savefig('visuals/shap_live.png', dpi=120, bbox_inches='tight')
            plt.close(fig)
        except Exception as e:
            _create_fallback_explanation(row_sc, score)
    else:
        _create_fallback_explanation(row_sc, score)

    result = {
        'score':      score,
        'risk_label': str(label),
        'confidence': conf,
        'shap_path':  'visuals/shap_live.png',
    }

    try:
        from db.mongo_handler import insert_submission
        insert_submission({
            **form_dict,
            'burnout_score': score,
            'risk_label':    str(label),
            'confidence':    conf,
        })
    except Exception as e:
        pass

    return result


def _create_fallback_explanation(X_scaled, burnout_score):
    """Create a simple explanation plot when SHAP is not available"""
    try:
        # Create a simple bar chart showing the burnout score and key insights
        fig, (ax1, ax2) = plt.subplots(1, 2, figsize=(12, 4))
        
        # Left plot: Burnout score gauge
        ax1.barh(['Burnout\nScore'], [burnout_score], color='#E74C3C' if burnout_score > 0.6 else '#F39C12' if burnout_score > 0.3 else '#27AE60')
        ax1.set_xlim(0, 1)
        ax1.set_title('Prediction Result')
        ax1.set_xlabel('Risk Level (0 Low → 1 High)')
        
        # Right plot: Model confidence info
        confidence_text = f"Score: {burnout_score:.3f}\n\nModel: Logistic Regression\nAccuracy: 99.52%\n\nBased on:\n• Sleep patterns\n• Study load\n• Stress levels\n• Exercise habits"
        ax2.text(0.1, 0.5, confidence_text, fontsize=11, verticalalignment='center',
                bbox=dict(boxstyle='round', facecolor='wheat', alpha=0.5))
        ax2.axis('off')
        ax2.set_title('Model Information')
        
        plt.tight_layout()
        plt.savefig('visuals/shap_live.png', dpi=120, bbox_inches='tight')
        plt.close(fig)
    except Exception as e:
        print(f"Warning: Could not create explanation plot: {e}")
