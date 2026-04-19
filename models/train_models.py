import json
import numpy as np
import joblib
import matplotlib.pyplot as plt
from sklearn.linear_model    import LogisticRegression
from sklearn.tree            import DecisionTreeClassifier
from sklearn.ensemble        import RandomForestClassifier, GradientBoostingClassifier
from sklearn.metrics         import (accuracy_score, f1_score,
                                     classification_report,
                                     ConfusionMatrixDisplay)
from sklearn.model_selection import cross_val_score

X_train = np.load('data/X_train.npy')
X_test  = np.load('data/X_test.npy')
y_train = np.load('data/y_train.npy')
y_test  = np.load('data/y_test.npy')

models = {
    'LogisticRegression':  LogisticRegression(max_iter=1000, random_state=42),
    'DecisionTree':        DecisionTreeClassifier(max_depth=5, random_state=42),
    'RandomForest':        RandomForestClassifier(n_estimators=100, random_state=42),
    'GradientBoosting':    GradientBoostingClassifier(n_estimators=100,
                               learning_rate=0.1, max_depth=3, random_state=42),
}

metrics = {}

for name, model in models.items():
    print(f"Training {name}...")
    model.fit(X_train, y_train)
    preds = model.predict(X_test)

    acc = round(accuracy_score(y_test, preds), 4)
    f1  = round(f1_score(y_test, preds, average='weighted'), 4)
    cv  = cross_val_score(model, X_train, y_train, cv=5)

    metrics[name] = {
        'accuracy': acc, 'f1': f1,
        'cv_mean':  round(cv.mean(), 4),
        'cv_std':   round(cv.std(),  4)
    }
    print(f"  Accuracy: {acc}  F1: {f1}  CV: {cv.mean():.4f} ± {cv.std():.4f}")
    print(classification_report(y_test, preds))

    joblib.dump(model, f'models/{name.lower()}.pkl')

    # Confusion matrix plot
    fig, ax = plt.subplots(figsize=(6, 5))
    ConfusionMatrixDisplay.from_predictions(y_test, preds, ax=ax)
    ax.set_title(f'{name} — Confusion Matrix')
    plt.tight_layout()
    plt.savefig(f'visuals/cm_{name.lower()}.png', dpi=150)
    plt.close(fig)

# Pick best model by F1 score
best = max(metrics, key=lambda k: metrics[k]['f1'])
metrics['best_model'] = best
print(f"\nBest model: {best}")

with open('models/metrics.json', 'w') as f:
    json.dump(metrics, f, indent=2)
print("metrics.json saved.")
