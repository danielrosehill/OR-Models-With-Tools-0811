#!/usr/bin/env python3
"""
Generate PNG visualizations for all CSV files in the analysis folder.
Creates bar charts showing the 10 most expensive models with model names on x-axis.
"""

import pandas as pd
import matplotlib.pyplot as plt
import seaborn as sns
from pathlib import Path
import os

# Set style
sns.set_style("whitegrid")
plt.rcParams['figure.figsize'] = (14, 8)
plt.rcParams['font.size'] = 10

def extract_model_name(model_id):
    """Extract a readable model name from the model ID."""
    if pd.isna(model_id):
        return "Unknown"

    # Remove common prefixes
    model_id = str(model_id)
    prefixes_to_remove = [
        'anthropic.', 'meta.', 'amazon.', 'cohere.', 'ai21.',
        'mistral.', 'stability.', 'google.', 'openai.',
    ]

    for prefix in prefixes_to_remove:
        if model_id.startswith(prefix):
            model_id = model_id[len(prefix):]

    # Clean up version numbers and make more readable
    model_id = model_id.replace('-', ' ').replace('_', ' ')

    # Capitalize appropriately
    parts = model_id.split()
    if parts:
        # Keep version numbers lowercase, capitalize model names
        cleaned_parts = []
        for part in parts:
            if part[0].isdigit() or part.startswith('v'):
                cleaned_parts.append(part)
            else:
                cleaned_parts.append(part.capitalize())
        return ' '.join(cleaned_parts)

    return model_id

def create_visualization(csv_path, output_dir):
    """Create a bar chart visualization for a CSV file."""
    try:
        df = pd.read_csv(csv_path)

        # Skip if dataframe is empty
        if df.empty:
            print(f"Skipping empty CSV: {csv_path}")
            return

        # Determine which price column to use and sort accordingly
        price_col = None
        title_suffix = ""

        # Check for different naming conventions
        if 'avg_price_usd_per_m' in df.columns:
            price_col = 'avg_price_usd_per_m'
            title_suffix = "Average Price"
        elif 'average_price_per_1m_tokens' in df.columns:
            price_col = 'average_price_per_1m_tokens'
            title_suffix = "Average Price"
        elif 'input_price_usd_per_m' in df.columns:
            price_col = 'input_price_usd_per_m'
            title_suffix = "Input Price"
        elif 'input_price_per_1m_tokens' in df.columns:
            price_col = 'input_price_per_1m_tokens'
            title_suffix = "Input Price"
        elif 'output_price_usd_per_m' in df.columns:
            price_col = 'output_price_usd_per_m'
            title_suffix = "Output Price"
        elif 'output_price_per_1m_tokens' in df.columns:
            price_col = 'output_price_per_1m_tokens'
            title_suffix = "Output Price"

        if price_col is None or price_col not in df.columns:
            print(f"Skipping {csv_path} - no price column found")
            return

        # Sort by price and get top 10
        df_sorted = df.sort_values(by=price_col, ascending=False).head(10)

        # Skip if we have no data after filtering
        if df_sorted.empty:
            print(f"Skipping {csv_path} - no data after filtering")
            return

        # Extract model names - check for both model_id and model_name columns
        if 'model_name' in df_sorted.columns:
            # Already have model_name, just clean it up
            df_sorted['display_name'] = df_sorted['model_name'].apply(lambda x: str(x).split(': ')[-1] if ': ' in str(x) else str(x))
        elif 'model_id' in df_sorted.columns:
            df_sorted['display_name'] = df_sorted['model_id'].apply(extract_model_name)
        else:
            print(f"Skipping {csv_path} - no model_name or model_id column")
            return

        # Create the plot
        fig, ax = plt.subplots(figsize=(14, 8))

        # Create bar chart
        bars = ax.bar(range(len(df_sorted)), df_sorted[price_col], color='steelblue', edgecolor='black')

        # Customize the plot
        ax.set_xlabel('Model', fontsize=12, fontweight='bold')
        ax.set_ylabel(f'Price per 1M Tokens ($)', fontsize=12, fontweight='bold')

        # Generate title from file path
        csv_name = Path(csv_path).stem
        parent_dir = Path(csv_path).parent.name
        title = f"Top 10 Most Expensive Models - {title_suffix}\n{parent_dir}/{csv_name}"
        ax.set_title(title, fontsize=14, fontweight='bold', pad=20)

        # Set x-axis labels (model names)
        ax.set_xticks(range(len(df_sorted)))
        ax.set_xticklabels(df_sorted['display_name'], rotation=45, ha='right')

        # Add value labels on top of bars
        for i, (bar, value) in enumerate(zip(bars, df_sorted[price_col])):
            height = bar.get_height()
            ax.text(bar.get_x() + bar.get_width()/2., height,
                   f'${value:.2f}',
                   ha='center', va='bottom', fontsize=9, fontweight='bold')

        # Add grid for better readability
        ax.grid(axis='y', alpha=0.3, linestyle='--')
        ax.set_axisbelow(True)

        # Adjust layout to prevent label cutoff
        plt.tight_layout()

        # Save the figure
        output_path = output_dir / f"{Path(csv_path).stem}.png"
        plt.savefig(output_path, dpi=300, bbox_inches='tight')
        plt.close()

        print(f"Created: {output_path}")

    except Exception as e:
        print(f"Error processing {csv_path}: {str(e)}")

def main():
    """Main function to process all CSV files."""
    base_dir = Path(__file__).parent.parent / "analysis"

    # Find all CSV files
    csv_files = list(base_dir.rglob("*.csv"))

    print(f"Found {len(csv_files)} CSV files to process\n")

    # Process each CSV file
    for csv_file in csv_files:
        # Create corresponding output directory structure
        relative_path = csv_file.relative_to(base_dir)
        output_dir = base_dir / relative_path.parent

        # Ensure output directory exists
        output_dir.mkdir(parents=True, exist_ok=True)

        create_visualization(csv_file, output_dir)

    print(f"\nVisualization generation complete!")

if __name__ == "__main__":
    main()
