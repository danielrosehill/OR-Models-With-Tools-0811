#!/usr/bin/env python3
"""
Create visualizations for cost vs context window analysis of LLM models.
Generates:
1. Interactive-style scatter plot (saved as static PNG)
2. Quadrant analysis plot
"""

import pandas as pd
import matplotlib.pyplot as plt
import numpy as np
import seaborn as sns

# Set style for better-looking plots
sns.set_style("whitegrid")
plt.rcParams['figure.figsize'] = (14, 10)
plt.rcParams['font.size'] = 10

# Load data
df = pd.read_csv('/home/daniel/repos/github/OR-Models-With-Tools-0811/data/parsed/all-models.csv')

# Calculate average cost (input + output) / 2
df['avg_cost'] = (df['input_price_usd_per_m'] + df['output_price_usd_per_m']) / 2

# Remove models with 0 cost (free tier) for better visualization
df_paid = df[df['avg_cost'] > 0].copy()

print(f"Total models: {len(df)}")
print(f"Paid models: {len(df_paid)}")
print(f"Free models: {len(df[df['avg_cost'] == 0])}")

# ============================================================================
# Visualization 1: Full scatter plot with provider colors
# ============================================================================

fig, ax = plt.subplots(figsize=(16, 12))

# Get unique vendors and assign colors
vendors = df_paid['vendor'].unique()
colors = plt.cm.tab20(np.linspace(0, 1, len(vendors)))
vendor_colors = dict(zip(vendors, colors))

# Plot each vendor with different color
for vendor in vendors:
    vendor_data = df_paid[df_paid['vendor'] == vendor]
    ax.scatter(
        vendor_data['context_length'] / 1000,  # Convert to K tokens
        vendor_data['avg_cost'],
        label=vendor,
        alpha=0.6,
        s=100,
        color=vendor_colors[vendor],
        edgecolors='black',
        linewidth=0.5
    )

# Logarithmic scale for better visibility
ax.set_xscale('log')
ax.set_yscale('log')

# Labels and title
ax.set_xlabel('Context Window (K tokens, log scale)', fontsize=14, fontweight='bold')
ax.set_ylabel('Average Cost ($/M tokens, log scale)', fontsize=14, fontweight='bold')
ax.set_title('LLM Cost vs Context Window Analysis\n(Tool-Use Capable Models)',
             fontsize=16, fontweight='bold', pad=20)

# Grid
ax.grid(True, alpha=0.3, which='both')

# Legend
ax.legend(bbox_to_anchor=(1.05, 1), loc='upper left', borderaxespad=0,
          frameon=True, shadow=True, ncol=1)

plt.tight_layout()
plt.savefig('/home/daniel/repos/github/OR-Models-With-Tools-0811/analysis/cost_vs_context_full.png',
            dpi=300, bbox_inches='tight')
print("✓ Saved: analysis/cost_vs_context_full.png")
plt.close()

# ============================================================================
# Visualization 2: Quadrant Analysis
# ============================================================================

fig, ax = plt.subplots(figsize=(16, 12))

# Calculate median values for quadrant divisions
median_context = df_paid['context_length'].median()
median_cost = df_paid['avg_cost'].median()

print(f"\nQuadrant divisions:")
print(f"Median context: {median_context:,.0f} tokens ({median_context/1000:.0f}K)")
print(f"Median cost: ${median_cost:.2f}/M tokens")

# Define quadrants and assign colors
def assign_quadrant(row):
    if row['avg_cost'] < median_cost and row['context_length'] >= median_context:
        return 'Low Cost / High Context\n(Budget Champions)'
    elif row['avg_cost'] >= median_cost and row['context_length'] >= median_context:
        return 'High Cost / High Context\n(Premium Options)'
    elif row['avg_cost'] < median_cost and row['context_length'] < median_context:
        return 'Low Cost / Low Context\n(Budget Basic)'
    else:
        return 'High Cost / Low Context\n(Avoid)'

df_paid['quadrant'] = df_paid.apply(assign_quadrant, axis=1)

# Quadrant colors
quadrant_colors = {
    'Low Cost / High Context\n(Budget Champions)': '#2ecc71',  # Green
    'High Cost / High Context\n(Premium Options)': '#3498db',  # Blue
    'Low Cost / Low Context\n(Budget Basic)': '#f39c12',  # Orange
    'High Cost / Low Context\n(Avoid)': '#e74c3c'  # Red
}

# Plot each quadrant
for quadrant, color in quadrant_colors.items():
    quad_data = df_paid[df_paid['quadrant'] == quadrant]
    ax.scatter(
        quad_data['context_length'] / 1000,
        quad_data['avg_cost'],
        label=f"{quadrant} ({len(quad_data)} models)",
        alpha=0.7,
        s=120,
        color=color,
        edgecolors='black',
        linewidth=0.8
    )

# Add quadrant dividing lines
ax.axvline(x=median_context/1000, color='gray', linestyle='--', linewidth=2, alpha=0.5, label='Median Context')
ax.axhline(y=median_cost, color='gray', linestyle='--', linewidth=2, alpha=0.5, label='Median Cost')

# Logarithmic scale
ax.set_xscale('log')
ax.set_yscale('log')

# Labels and title
ax.set_xlabel('Context Window (K tokens, log scale)', fontsize=14, fontweight='bold')
ax.set_ylabel('Average Cost ($/M tokens, log scale)', fontsize=14, fontweight='bold')
ax.set_title('LLM Quadrant Analysis: Finding Cost-Effective Models\n(Tool-Use Capable Models)',
             fontsize=16, fontweight='bold', pad=20)

# Grid
ax.grid(True, alpha=0.3, which='both')

# Legend
ax.legend(bbox_to_anchor=(1.05, 1), loc='upper left', borderaxespad=0,
          frameon=True, shadow=True, fontsize=11)

plt.tight_layout()
plt.savefig('/home/daniel/repos/github/OR-Models-With-Tools-0811/analysis/cost_vs_context_quadrants.png',
            dpi=300, bbox_inches='tight')
print("✓ Saved: analysis/cost_vs_context_quadrants.png")
plt.close()

# ============================================================================
# Generate summary statistics
# ============================================================================

print("\n" + "="*70)
print("QUADRANT SUMMARY")
print("="*70)

for quadrant in quadrant_colors.keys():
    quad_data = df_paid[df_paid['quadrant'] == quadrant]
    print(f"\n{quadrant}")
    print(f"  Count: {len(quad_data)}")
    print(f"  Avg Cost: ${quad_data['avg_cost'].mean():.2f}/M")
    print(f"  Avg Context: {quad_data['context_length'].mean()/1000:.0f}K tokens")

    # Show top 5 models in this quadrant by context/cost ratio
    if len(quad_data) > 0:
        quad_data['value_score'] = quad_data['context_length'] / quad_data['avg_cost']
        top_5 = quad_data.nlargest(5, 'value_score')[['model_name', 'vendor', 'context_length', 'avg_cost', 'value_score']]
        print("\n  Top 5 by value (context/cost):")
        for idx, row in top_5.iterrows():
            print(f"    - {row['model_name'][:50]} ({row['vendor']})")
            print(f"      Context: {row['context_length']/1000:.0f}K | Cost: ${row['avg_cost']:.2f} | Score: {row['value_score']:.0f}")

print("\n" + "="*70)
print("Visualizations complete!")
print("="*70)
