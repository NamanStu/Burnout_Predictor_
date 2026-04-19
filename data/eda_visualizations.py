import pandas as pd
import matplotlib.pyplot as plt
import seaborn as sns
import numpy as np

df = pd.read_csv('data/raw_burnout.csv')
sns.set_theme(style='whitegrid')   # call ONCE at top

# Select only numeric columns for visualization
numeric_df = df.select_dtypes(include=[np.number])

# ── Plot 1: Correlation heatmap ──────────────────────
fig, ax = plt.subplots(figsize=(10, 8))
sns.heatmap(numeric_df.corr(),
            annot=True, fmt='.2f', ax=ax, cmap='Blues',
            square=True, cbar_kws={'shrink': 0.8})
ax.set_title('Feature Correlation Heatmap')
plt.tight_layout()
plt.savefig('visuals/heatmap.png', dpi=150)
plt.close(fig)
print("✅ Correlation heatmap saved")

# ── Plot 2: Burnout distribution ─────────────────────
fig, ax = plt.subplots(figsize=(8, 5))
df['burnout_risk'].value_counts().plot(kind='bar', ax=ax, color=['#E74C3C', '#F39C12', '#27AE60'])
ax.set_title('Burnout Risk Distribution')
ax.set_xlabel('Risk Level')
ax.set_ylabel('Count')
plt.tight_layout()
plt.savefig('visuals/burnout_distribution.png', dpi=150)
plt.close(fig)
print("✅ Burnout distribution saved")

# ── Plot 3: Feature boxplots ──────────────────────────
num_cols = numeric_df.columns[:9]  # Select first 9 numeric columns
fig, axes = plt.subplots(3, 3, figsize=(14, 10))
axes = axes.flatten()
for i, col in enumerate(num_cols):
    sns.boxplot(y=df[col], ax=axes[i], color='steelblue')
    axes[i].set_title(col)
plt.tight_layout()
plt.savefig('visuals/boxplots.png', dpi=150)
plt.close(fig)
print("✅ Boxplots saved")

print("\n✅ All EDA plots saved to visuals/")
