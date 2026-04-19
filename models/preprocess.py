import pandas as pd
import numpy as np
from sklearn.model_selection import train_test_split
from sklearn.preprocessing import StandardScaler, LabelEncoder
import joblib

# Load raw dataset
df = pd.read_csv('data/raw_burnout.csv')
print("Dataset shape:", df.shape)
print("\nColumns:", list(df.columns))

# ── Drop text columns not needed for model ─────────────────
df.drop(columns=['weekly_journal'], inplace=True)

# ── Identify categorical columns (excluding target) ────────
target_col = 'burnout_risk'
categorical_cols = df.select_dtypes(include='object').columns.tolist()
if target_col in categorical_cols:
    categorical_cols.remove(target_col)

print("\nCategorical columns to encode:", categorical_cols)

# ── Convert categorical columns to numeric ────────────────
# Use pd.get_dummies for one-hot encoding
df_encoded = pd.get_dummies(df, columns=categorical_cols, drop_first=False)

print("\nShape after encoding:", df_encoded.shape)
print("Columns after encoding:", list(df_encoded.columns))

# ── Encode target label (burnout_risk) ─────────────────────
le = LabelEncoder()
df_encoded[target_col] = le.fit_transform(df_encoded[target_col])
joblib.dump(le, 'models/label_encoder.pkl')
print("\nTarget classes:", le.classes_)

# ── Split FIRST (80% train, 20% test), then scale ──────────
X = df_encoded.drop(target_col, axis=1)
y = df_encoded[target_col]

X_train, X_test, y_train, y_test = train_test_split(
    X, y, test_size=0.2, random_state=42, stratify=y)

print(f"\nTrain size: {X_train.shape[0]} samples (80%)")
print(f"Test size: {X_test.shape[0]} samples (20%)")

# Fit scaler on X_train ONLY (prevent data leakage)
scaler = StandardScaler()
X_train_sc = scaler.fit_transform(X_train)
X_test_sc  = scaler.transform(X_test)

# Save scaler, feature names, and data
joblib.dump(scaler,             'models/scaler.pkl')
joblib.dump(list(X.columns),   'models/feature_names.pkl')

# Save preprocessed arrays for quick loading
np.save('data/X_train.npy', X_train_sc)
np.save('data/X_test.npy',  X_test_sc)
np.save('data/y_train.npy', y_train.values)
np.save('data/y_test.npy',  y_test.values)

print("\n✅ Preprocessing complete!")
print(f"Feature count: {X_train_sc.shape[1]}")
print(f"Class distribution (train): {np.bincount(y_train.values)}")
print(f"Class distribution (test): {np.bincount(y_test.values)}")
