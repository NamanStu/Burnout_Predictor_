import pandas as pd
import numpy as np

df = pd.read_csv('data/raw_burnout.csv')

print("="*60)
print("EXPLORATORY DATA ANALYSIS - Student Burnout Dataset")
print("="*60)

print("\n📊 DATASET SHAPE:", df.shape)
print(f"   Rows: {df.shape[0]} students")
print(f"   Columns: {df.shape[1]} features")

print("\n📋 COLUMN TYPES:")
print(df.dtypes)

print("\n❌ NULL VALUES:")
null_counts = df.isnull().sum()
if null_counts.sum() > 0:
    print(null_counts[null_counts > 0])
else:
    print("   ✅ No missing values!")

print("\n🎯 TARGET VARIABLE DISTRIBUTION (Burnout Risk):")
print(df['burnout_risk'].value_counts())
print("\nPercentage distribution:")
print(df['burnout_risk'].value_counts(normalize=True) * 100)

print("\n📈 NUMERIC COLUMNS STATISTICS:")
print(df.describe())

print("\n🏷️  CATEGORICAL COLUMNS:")
categorical_cols = df.select_dtypes(include='object').columns
for col in categorical_cols:
    if col != 'weekly_journal':
        print(f"\n   {col}: {df[col].nunique()} unique values")
        print(f"   {df[col].value_counts().to_dict()}")

print("\n✅ Data inspection complete!")

