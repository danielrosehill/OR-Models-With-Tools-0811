#!/usr/bin/env python3
"""
Find the 10 least expensive (cheapest) models by input, output, and average pricing.
Excludes free models (where both input and output price are 0).
"""

import csv
from pathlib import Path

def main():
    # Read the CSV file
    input_file = Path("data/parsed/all-models.csv")
    output_dir = Path("analysis")
    output_dir.mkdir(parents=True, exist_ok=True)

    # Read all models
    models = []
    with open(input_file, 'r', encoding='utf-8') as f:
        reader = csv.DictReader(f)
        for row in reader:
            try:
                row['input_price_usd_per_m'] = float(row['input_price_usd_per_m'])
                row['output_price_usd_per_m'] = float(row['output_price_usd_per_m'])
                row['avg_price_usd_per_m'] = (row['input_price_usd_per_m'] + row['output_price_usd_per_m']) / 2

                # Exclude free models (both input and output must be > 0)
                if row['input_price_usd_per_m'] > 0 or row['output_price_usd_per_m'] > 0:
                    models.append(row)
            except (ValueError, KeyError) as e:
                print(f"Skipping row due to error: {e}")
                continue

    # Sort and get bottom 10 by input price (excluding 0s)
    non_zero_input = [m for m in models if m['input_price_usd_per_m'] > 0]
    by_input = sorted(non_zero_input, key=lambda x: x['input_price_usd_per_m'])[:10]

    # Sort and get bottom 10 by output price (excluding 0s)
    non_zero_output = [m for m in models if m['output_price_usd_per_m'] > 0]
    by_output = sorted(non_zero_output, key=lambda x: x['output_price_usd_per_m'])[:10]

    # Sort and get bottom 10 by average price (excluding fully free models)
    by_average = sorted(models, key=lambda x: x['avg_price_usd_per_m'])[:10]

    # Save bottom 10 by input price
    output_file = output_dir / "bottom-10-by-input-price.csv"
    with open(output_file, 'w', encoding='utf-8', newline='') as f:
        fieldnames = ['model_name', 'vendor', 'context_length', 'input_price_usd_per_m',
                     'output_price_usd_per_m', 'avg_price_usd_per_m']
        writer = csv.DictWriter(f, fieldnames=fieldnames, extrasaction='ignore')
        writer.writeheader()
        writer.writerows(by_input)
    print(f"Created {output_file}")

    # Save bottom 10 by output price
    output_file = output_dir / "bottom-10-by-output-price.csv"
    with open(output_file, 'w', encoding='utf-8', newline='') as f:
        fieldnames = ['model_name', 'vendor', 'context_length', 'input_price_usd_per_m',
                     'output_price_usd_per_m', 'avg_price_usd_per_m']
        writer = csv.DictWriter(f, fieldnames=fieldnames, extrasaction='ignore')
        writer.writeheader()
        writer.writerows(by_output)
    print(f"Created {output_file}")

    # Save bottom 10 by average price
    output_file = output_dir / "bottom-10-by-average-price.csv"
    with open(output_file, 'w', encoding='utf-8', newline='') as f:
        fieldnames = ['model_name', 'vendor', 'context_length', 'input_price_usd_per_m',
                     'output_price_usd_per_m', 'avg_price_usd_per_m']
        writer = csv.DictWriter(f, fieldnames=fieldnames, extrasaction='ignore')
        writer.writeheader()
        writer.writerows(by_average)
    print(f"Created {output_file}")

    print("\n=== Top 10 Cheapest by Input Price (excluding free) ===")
    for i, model in enumerate(by_input, 1):
        print(f"{i}. {model['model_name']} ({model['vendor']}) - ${model['input_price_usd_per_m']:.4f}/M")

    print("\n=== Top 10 Cheapest by Output Price (excluding free) ===")
    for i, model in enumerate(by_output, 1):
        print(f"{i}. {model['model_name']} ({model['vendor']}) - ${model['output_price_usd_per_m']:.4f}/M")

    print("\n=== Top 10 Cheapest by Average Price (excluding free) ===")
    for i, model in enumerate(by_average, 1):
        print(f"{i}. {model['model_name']} ({model['vendor']}) - ${model['avg_price_usd_per_m']:.4f}/M avg (In: ${model['input_price_usd_per_m']:.4f}, Out: ${model['output_price_usd_per_m']:.4f})")

    print(f"\n\nNote: Analyzed {len(models)} paid models (excluded fully free models)")

if __name__ == "__main__":
    main()
