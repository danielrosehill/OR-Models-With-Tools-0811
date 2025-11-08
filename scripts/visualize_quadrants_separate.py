#!/usr/bin/env python3
"""
Create separate visualizations for each quadrant.
Output:
1. Overview map showing the 4 quadrants with labels
2-5. Individual plots for each quadrant with model details
"""

import pandas as pd
import matplotlib.pyplot as plt
import numpy as np
import seaborn as sns
try:
    from adjustText import adjust_text
    ADJUST_TEXT_AVAILABLE = True
except ImportError:
    ADJUST_TEXT_AVAILABLE = False
    print("Note: adjustText not available, labels may overlap")

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

# ============================================================================
# Visualization 1: Overview Map with Quadrant Labels
# ============================================================================

fig, ax = plt.subplots(figsize=(14, 10))

# Quadrant colors (muted for overview)
quadrant_info = {
    'Low Cost / High Context': {'color': '#2ecc71', 'label': 'Low Cost / High Context'},
    'High Cost / High Context': {'color': '#3498db', 'label': 'High Cost / High Context'},
    'Low Cost / Low Context': {'color': '#f39c12', 'label': 'Low Cost / Low Context'},
    'High Cost / Low Context': {'color': '#e74c3c', 'label': 'High Cost / Low Context'}
}

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
            f"{info['label']}\n({count} models)",
            fontsize=14, fontweight='bold',
            ha='center', va='center',
            bbox=dict(boxstyle='round,pad=0.8', facecolor=info['color'],
                     edgecolor='black', linewidth=2, alpha=0.8),
            color='white')

plt.tight_layout()
plt.savefig('/home/daniel/repos/github/OR-Models-With-Tools-0811/analysis/quadrant_overview.png',
            dpi=300, bbox_inches='tight')
print("✓ Saved: analysis/quadrant_overview.png")
plt.close()

# ============================================================================
# Visualizations 2-5: Individual Quadrant Details
# ============================================================================

for quadrant, info in quadrant_info.items():
    quad_data = df_paid[df_paid['quadrant'] == quadrant].copy()

    if len(quad_data) == 0:
        continue

    fig, ax = plt.subplots(figsize=(16, 12))

    # Plot all points in the quadrant color
    ax.scatter(
        quad_data['context_length'] / 1000,
        quad_data['avg_cost'],
        alpha=0.6,
        s=100,
        color=info['color'],
        edgecolors='black',
        linewidth=0.8
    )

    # Add labels for each model
    # For models, extract a short name from model_name (before first parenthesis or colon)
    texts = []
    for idx, row in quad_data.iterrows():
        # Extract short model name
        model_name = row['model_name']
        # Try to get the part after the first colon (e.g., "OpenAI: GPT-4" -> "GPT-4")
        if ':' in model_name:
            short_name = model_name.split(':', 1)[1].strip()
        else:
            short_name = model_name

        # Limit length
        if len(short_name) > 40:
            short_name = short_name[:37] + '...'

        text = ax.text(
            row['context_length'] / 1000,
            row['avg_cost'],
            short_name,
            fontsize=7,
            alpha=0.8
        )
        texts.append(text)

    # Adjust text to avoid overlaps (this may take a moment)
    if ADJUST_TEXT_AVAILABLE:
        try:
            adjust_text(texts, arrowprops=dict(arrowstyle='-', color='gray', lw=0.5, alpha=0.5))
        except:
            # If adjust_text fails, just skip the adjustment
            pass

    # Logarithmic scale
    ax.set_xscale('log')
    ax.set_yscale('log')

    # Labels and title
    ax.set_xlabel('Context Window (K tokens, log scale)', fontsize=14, fontweight='bold')
    ax.set_ylabel('Average Cost ($/M tokens, log scale)', fontsize=14, fontweight='bold')

    # Title with quadrant info
    title = f"{info['label']}: {quadrant}\n({len(quad_data)} models)"
    ax.set_title(title, fontsize=16, fontweight='bold', pad=20,
                bbox=dict(boxstyle='round,pad=0.8', facecolor=info['color'],
                         edgecolor='black', linewidth=2, alpha=0.3))

    # Grid
    ax.grid(True, alpha=0.3, which='both')

    # Add summary statistics box
    stats_text = (
        f"Statistics:\n"
        f"Models: {len(quad_data)}\n"
        f"Avg Cost: ${quad_data['avg_cost'].mean():.2f}/M\n"
        f"Cost Range: ${quad_data['avg_cost'].min():.2f} - ${quad_data['avg_cost'].max():.2f}\n"
        f"Avg Context: {quad_data['context_length'].mean()/1000:.0f}K\n"
        f"Context Range: {quad_data['context_length'].min()/1000:.0f}K - {quad_data['context_length'].max()/1000:.0f}K"
    )

    ax.text(0.02, 0.98, stats_text,
            transform=ax.transAxes,
            fontsize=10,
            verticalalignment='top',
            bbox=dict(boxstyle='round', facecolor='white',
                     edgecolor='black', linewidth=1.5, alpha=0.9))

    plt.tight_layout()

    # Save with sanitized filename
    filename = quadrant.lower().replace(' / ', '_').replace(' ', '_')
    filepath = f'/home/daniel/repos/github/OR-Models-With-Tools-0811/analysis/quadrant_{filename}.png'
    plt.savefig(filepath, dpi=300, bbox_inches='tight')
    print(f"✓ Saved: analysis/quadrant_{filename}.png")
    plt.close()

    # Print top models in this quadrant
    print(f"\n{quadrant} - Top 10 models by value (context/cost):")
    quad_data['value_score'] = quad_data['context_length'] / quad_data['avg_cost']
    top_10 = quad_data.nlargest(10, 'value_score')[['model_name', 'vendor', 'context_length', 'avg_cost']]
    for idx, (i, row) in enumerate(top_10.iterrows(), 1):
        print(f"  {idx}. {row['model_name'][:60]} ({row['vendor']})")
        print(f"     Context: {row['context_length']/1000:.0f}K | Cost: ${row['avg_cost']:.2f}/M")

print("\n" + "="*70)
print("All visualizations complete!")
print("="*70)
