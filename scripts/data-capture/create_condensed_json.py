#!/usr/bin/env python3
"""
Create a condensed JSON file with only the essential fields for models that support tools.
"""

import json
import sys
from typing import List, Dict, Any


def extract_vendor(model_id: str) -> str:
    """Extract vendor from model ID (e.g., 'anthropic/claude-3' -> 'anthropic')."""
    if "/" in model_id:
        return model_id.split("/")[0]
    return "Unknown"


def get_model_params(architecture: Dict[str, Any]) -> str:
    """Extract model parameters if available."""
    # The API doesn't seem to provide explicit parameter counts
    # We'll return empty string if not available
    return ""


def extract_condensed_model_info(model: Dict[str, Any]) -> Dict[str, Any]:
    """
    Extract only the essential fields from a model object.

    Fields extracted:
    - model_name: Readable model name
    - model_id: API model identifier
    - vendor: Model vendor/provider
    - context: Context length in tokens
    - input_price_usd_m: Input price in USD per million tokens
    - output_price_usd_m: Output price in USD per million tokens
    - description: Model description
    - model_params: Model parameter count (if available)
    """
    model_id = model.get("id", "")
    vendor = extract_vendor(model_id)

    # Get pricing information
    pricing = model.get("pricing", {})
    prompt_price = float(pricing.get("prompt", "0"))
    completion_price = float(pricing.get("completion", "0"))

    # Convert from per-token to per-million tokens
    input_price_m = prompt_price * 1_000_000
    output_price_m = completion_price * 1_000_000

    condensed = {
        "model_name": model.get("name", ""),
        "model_id": model_id,
        "vendor": vendor,
        "context": model.get("context_length", 0),
        "input_price_usd_m": round(input_price_m, 4),
        "output_price_usd_m": round(output_price_m, 4),
        "description": model.get("description", ""),
        "model_params": get_model_params(model.get("architecture", {}))
    }

    return condensed


def main():
    """Main function."""
    input_file = "models_with_tools.json"
    output_file = "models_with_tools_condensed.json"

    try:
        # Read the full models data
        with open(input_file, "r") as f:
            models = json.load(f)

        print(f"Processing {len(models)} models...")

        # Extract condensed information
        condensed_models = [extract_condensed_model_info(model) for model in models]

        # Write to output file
        with open(output_file, "w") as f:
            json.dump(condensed_models, f, indent=2)

        print(f"✓ Created condensed JSON with {len(condensed_models)} models")
        print(f"✓ Output saved to: {output_file}")

        # Print some statistics
        total_free = sum(1 for m in condensed_models if m["input_price_usd_m"] == 0)
        print(f"\nStatistics:")
        print(f"  Total models: {len(condensed_models)}")
        print(f"  Free models: {total_free}")
        print(f"  Paid models: {len(condensed_models) - total_free}")

        # Show sample of the condensed data
        print(f"\nSample entry:")
        print(json.dumps(condensed_models[0], indent=2))

    except FileNotFoundError:
        print(f"Error: {input_file} not found. Please run get_tool_models.py first.", file=sys.stderr)
        sys.exit(1)
    except json.JSONDecodeError as e:
        print(f"Error: Failed to parse JSON: {e}", file=sys.stderr)
        sys.exit(1)


if __name__ == "__main__":
    main()
