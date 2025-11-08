#!/usr/bin/env python3
"""
Create CSV files with quadrant assignments for each model.
Output:
1. Overview map showing the 4 quadrants with labels (no individual labels)
2. CSV file for each quadrant with model details
3. Master CSV with all models and their quadrant assignments
"""

import pandas as pd
import matplotlib.pyplot as plt
import numpy as np
import seaborn as sns

# Set style for better-looking plots
sns.set_style("whitegrid")
plt.rcParams['font.size'] = 10

# Load data
df = pd.read_csv('/home/daniel/repos/github/OR-Models-With-Tools-0811/data/parsed/all-models.csv')

# Calculate average cost (input + output) / 2
df['avg_cost'] = (df['input_price_usd_per_m'] + df['output_price_usd_per_m']) / 2

# Remove models with 0 cost (free tier)
df_paid = df[df['avg_cost'] > 0].copy()

# Calculate median values for quadrant divisions
median_context = df_paid['context_length'].median()
median_cost = df_paid['avg_cost'].median()

print(f"Median context: {median_context:,.0f} tokens ({median_context/1000:.0f}K)")
print(f"Median cost: ${median_cost:.2f}/M tokens")

# Define quadrants
def assign_quadrant(row):
    if row['avg_cost'] < median_cost and row['context_length'] >= median_context:
        return 'Low Cost / High Context'
    elif row['avg_cost'] >= median_cost and row['context_length'] >= median_context:
        return 'High Cost / High Context'
    elif row['avg_cost'] < median_cost and row['context_length'] < median_context:
        return 'Low Cost / Low Context'
    else:
        return 'High Cost / Low Context'

df_paid['quadrant'] = df_paid.apply(assign_quadrant, axis=1)

# Calculate value score
df_paid['value_score'] = df_paid['context_length'] / df_paid['avg_cost']

# ============================================================================
# Save CSVs
# ============================================================================

# Master CSV with all models
output_cols = ['model_name', 'model_id', 'vendor', 'context_length',
               'input_price_usd_per_m', 'output_price_usd_per_m', 'avg_cost',
               'quadrant', 'value_score', 'description']

df_paid_sorted = df_paid.sort_values('value_score', ascending=False)
df_paid_sorted[output_cols].to_csv(
    '/home/daniel/repos/github/OR-Models-With-Tools-0811/analysis/data/all_models_with_quadrants.csv',
    index=False
)
print(f"✓ Saved: analysis/data/all_models_with_quadrants.csv ({len(df_paid)} models)")

# Individual quadrant CSVs
quadrant_info = {
    'Low Cost / High Context': {'color': '#2ecc71'},
    'High Cost / High Context': {'color': '#3498db'},
    'Low Cost / Low Context': {'color': '#f39c12'},
    'High Cost / Low Context': {'color': '#e74c3c'}
}

for quadrant in quadrant_info.keys():
    quad_data = df_paid[df_paid['quadrant'] == quadrant].copy()
    quad_data_sorted = quad_data.sort_values('value_score', ascending=False)

    filename = quadrant.lower().replace(' / ', '_').replace(' ', '_')
    filepath = f'/home/daniel/repos/github/OR-Models-With-Tools-0811/analysis/data/quadrant_{filename}.csv'

    quad_data_sorted[output_cols].to_csv(filepath, index=False)
    print(f"✓ Saved: analysis/data/quadrant_{filename}.csv ({len(quad_data)} models)")

# ============================================================================
# Visualization: Overview Map with Quadrant Labels
# ============================================================================

fig, ax = plt.subplots(figsize=(14, 10))

# Plot all points in light gray first
ax.scatter(
    df_paid['context_length'] / 1000,
    df_paid['avg_cost'],
    alpha=0.2,
    s=50,
    color='gray',
    edgecolors='none'
)

# Add quadrant dividing lines
ax.axvline(x=median_context/1000, color='black', linestyle='-', linewidth=2.5, alpha=0.7)
ax.axhline(y=median_cost, color='black', linestyle='-', linewidth=2.5, alpha=0.7)

# Logarithmic scale
ax.set_xscale('log')
ax.set_yscale('log')

# Labels
ax.set_xlabel('Context Window (K tokens, log scale)', fontsize=14, fontweight='bold')
ax.set_ylabel('Average Cost ($/M tokens, log scale)', fontsize=14, fontweight='bold')
ax.set_title('LLM Cost vs Context Window: Quadrant Overview',
             fontsize=16, fontweight='bold', pad=20)

# Grid
ax.grid(True, alpha=0.3, which='both')

# Add quadrant labels as text annotations
# Get axis limits for positioning
xlim = ax.get_xlim()
ylim = ax.get_ylim()

# Calculate positions (in log space, use geometric mean)
x_low = np.exp((np.log(xlim[0]) + np.log(median_context/1000)) / 2)
x_high = np.exp((np.log(median_context/1000) + np.log(xlim[1])) / 2)
y_low = np.exp((np.log(ylim[0]) + np.log(median_cost)) / 2)
y_high = np.exp((np.log(median_cost) + np.log(ylim[1])) / 2)

# Quadrant labels with counts
for quadrant, info in quadrant_info.items():
    count = len(df_paid[df_paid['quadrant'] == quadrant])

    if quadrant == 'Low Cost / High Context':
        x_pos, y_pos = x_high, y_low
    elif quadrant == 'High Cost / High Context':
        x_pos, y_pos = x_high, y_high
    elif quadrant == 'Low Cost / Low Context':
        x_pos, y_pos = x_low, y_low
    else:  # High Cost / Low Context
        x_pos, y_pos = x_low, y_high

    ax.text(x_pos, y_pos,
            f"{quadrant}\n({count} models)",
            fontsize=13, fontweight='bold',
            ha='center', va='center',
            bbox=dict(boxstyle='round,pad=0.8', facecolor=info['color'],
                     edgecolor='black', linewidth=2, alpha=0.8),
            color='white')

plt.tight_layout()
plt.savefig('/home/daniel/repos/github/OR-Models-With-Tools-0811/analysis/charts/quadrant_overview.png',
            dpi=300, bbox_inches='tight')
print("✓ Saved: analysis/charts/quadrant_overview.png")
plt.close()

# ============================================================================
# Print summary statistics
# ============================================================================

print("\n" + "="*70)
print("QUADRANT SUMMARY")
print("="*70)

for quadrant in quadrant_info.keys():
    quad_data = df_paid[df_paid['quadrant'] == quadrant]
    print(f"\n{quadrant}")
    print(f"  Count: {len(quad_data)}")
    print(f"  Avg Cost: ${quad_data['avg_cost'].mean():.2f}/M")
    print(f"  Cost Range: ${quad_data['avg_cost'].min():.2f} - ${quad_data['avg_cost'].max():.2f}")
    print(f"  Avg Context: {quad_data['context_length'].mean()/1000:.0f}K tokens")
    print(f"  Context Range: {quad_data['context_length'].min()/1000:.0f}K - {quad_data['context_length'].max()/1000:.0f}K")

    # Show top 5 models
    print("\n  Top 5 by value (context/cost):")
    top_5 = quad_data.nlargest(5, 'value_score')[['model_name', 'vendor', 'context_length', 'avg_cost']]
    for idx, (i, row) in enumerate(top_5.iterrows(), 1):
        print(f"    {idx}. {row['model_name']} ({row['vendor']})")
        print(f"       Context: {row['context_length']/1000:.0f}K | Cost: ${row['avg_cost']:.2f}/M")

print("\n" + "="*70)
print("Complete! Check the analysis/ directory for:")
print("  - quadrant_overview.png (visualization)")
print("  - all_models_with_quadrants.csv (master list)")
print("  - quadrant_*.csv (individual quadrant CSVs)")
print("="*70)
