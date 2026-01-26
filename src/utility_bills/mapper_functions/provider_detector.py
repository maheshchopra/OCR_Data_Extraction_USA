import json
from typing import Dict, Any, Tuple


def detect_provider_from_json(json_data: Dict[str, Any]) -> str:
    """Get the provider name from the processed JSON."""

    # Check top-level provider_name field (added during extraction)
    if "provider_name" in json_data:
        return json_data["provider_name"]

    # Fallback to account_level_data if needed
    if "account_level_data" in json_data:
        provider = json_data["account_level_data"].get("provider")
        if provider:
            return provider

    return "Unknown Provider"


def load_and_detect_provider(file_path: str) -> Tuple[Dict[str, Any], str]:
    """
    Load JSON file and get provider name.

    Args:
        file_path: Path to the processed JSON file

    Returns:
        Tuple of (json_data, provider_name)
    """

    with open(file_path, "r") as f:
        json_data = json.load(f)

    provider_name = detect_provider_from_json(json_data)

    return json_data, provider_name
