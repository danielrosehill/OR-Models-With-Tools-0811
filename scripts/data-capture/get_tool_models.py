#!/usr/bin/env python3
"""
Poll OpenRouter API for models that support tools/function calling.
"""

import os
import sys
import json
import requests
from typing import List, Dict, Any


def get_models_with_tools(api_key: str = None) -> List[Dict[str, Any]]:
    """
    Fetch all models from OpenRouter API and filter for those supporting tools.

    Args:
        api_key: OpenRouter API key (optional, can be None for public endpoint)

    Returns:
        List of models that support tools
    """
    url = "https://openrouter.ai/api/v1/models"

    headers = {}
    if api_key:
        headers["Authorization"] = f"Bearer {api_key}"

    try:
        response = requests.get(url, headers=headers)
        response.raise_for_status()
        data = response.json()

        # Filter models that support tools
        models_with_tools = []
        for model in data.get("data", []):
            # Check if 'tools' is in supported_parameters
            supported_params = model.get("supported_parameters", [])
            if "tools" in supported_params:
                models_with_tools.append(model)

        return models_with_tools

    except requests.RequestException as e:
        print(f"Error fetching models: {e}", file=sys.stderr)
        sys.exit(1)


def format_model_info(model: Dict[str, Any]) -> str:
    """Format model information for display."""
    name = model.get("name", "N/A")
    model_id = model.get("id", "N/A")
    context = model.get("context_length", "N/A")
    pricing = model.get("pricing", {})
    input_price = pricing.get("prompt", "N/A")
    output_price = pricing.get("completion", "N/A")

    # Convert pricing from per-token to per-million tokens (USD)
    if input_price != "N/A":
        input_price_m = float(input_price) * 1_000_000
    else:
        input_price_m = "N/A"

    if output_price != "N/A":
        output_price_m = float(output_price) * 1_000_000
    else:
        output_price_m = "N/A"

    return f"""
Model: {name}
ID: {model_id}
Context: {context:,} tokens
Input: ${input_price_m:.4f}/M tokens
Output: ${output_price_m:.4f}/M tokens
---"""


def main():
    """Main function."""
    # Try to get API key from environment
    api_key = os.environ.get("OPENROUTER_API_KEY")

    print("Fetching models from OpenRouter API...")
    models = get_models_with_tools(api_key)

    print(f"\nFound {len(models)} models that support tools:\n")
    print("=" * 60)

    for model in models:
        print(format_model_info(model))

    # Optionally save to JSON file
    output_file = "models_with_tools.json"
    with open(output_file, "w") as f:
        json.dump(models, f, indent=2)

    print(f"\nFull model data saved to: {output_file}")


if __name__ == "__main__":
    main()
