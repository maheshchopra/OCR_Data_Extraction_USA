import sys
from pathlib import Path

from openai import OpenAI

# Add parent directory to path to import standard_model
sys.path.insert(0, str(Path(__file__).parent.parent))

import json
import logging
from typing import Any, Dict

from standard_template.standard_model import StandardUtilityBill

# Setup logging
logging.basicConfig(
    level=logging.INFO, format="%(asctime)s - %(levelname)s - %(message)s"
)
logger = logging.getLogger(__name__)


def transform_to_standard(
    provider_json: Dict[str, Any], provider_name: str, client: OpenAI = None
) -> StandardUtilityBill:
    """
    Use LLM to transform provider-specific JSON to standard format.

    Args:
        provider_json: The provider-specific JSON structure
        provider_name: Name of the provider (e.g., "Seattle Public Utilities")
        client: OpenAI client instance. If None, creates a new one.

    Returns:
        StandardUtilityBill object matching the uniform template

    Raises:
        Exception: If transformation fails
    """

    if client is None:
        client = OpenAI()

    # Remove provider_name from the JSON before sending to LLM (avoid redundancy)
    provider_json_copy = provider_json.copy()
    provider_json_copy.pop("provider_name", None)

    # Load tax transformation instructions
    tax_instructions_path = (
        Path(__file__).parent.parent
        / "transformation_prompts"
        / "tax_transformation_instructions.txt"
    )
    tax_instructions = ""
    if tax_instructions_path.exists():
        tax_instructions = tax_instructions_path.read_text(encoding="utf-8")

    prompt = f"""You are a utility bill data transformation expert. Your task is to transform a provider-specific utility bill JSON into a standardized format.

        PROVIDER: {provider_name}

        SOURCE DATA (Provider-specific format):
        {json.dumps(provider_json_copy, indent=2)}

        TRANSFORMATION INSTRUCTIONS:
        1. Map all fields from the source data to the appropriate fields in the standard format
        2. Convert ALL date formats to ISO format (YYYY-MM-DD). Handle these formats:
        - "January 05, 2026" → "2026-01-05"
        - "Dec 30, 2025" → "2025-12-30"
        - "1/6/2026" → "2026-01-06"
        - "Nov 29, 2025" → "2025-11-29"
        3. For fields that are strings in source but arrays in target, wrap them in array with appropriate objects
        4. Map service types to standard values: WATER, SEWER, SOLID_WASTE, ELECTRIC, GAS, STORMWATER, WASTEWATER, ADJUSTMENT, OTHER
        5. Extract and organize meter information from line items into proper meter_level_data structure
        6. Group line item charges appropriately into charge_groups
        7. If a field doesn't exist in source data, leave it empty ("") or null as appropriate
        8. Ensure all numeric calculations are accurate (totals, subtotals, etc.)
        9. Parse rates like "$5.98 per CCF" into:
        - rate: 5.98 (numeric)
        - rate_type: "per CCF" (string)
        10. Generate meter_id values as "M1", "M2", "M3", etc. for each unique meter_number found
        11. Link charges to meters using applies_to_meters array with meter_id values

        IMPORTANT STRUCTURAL TRANSFORMATIONS:

        For single contact strings, wrap in arrays:
        - Phone: "206-684-3000" → [{{"type": "call", "phone": "206-684-3000", "time": ""}}]
        - Website: "seattle.gov/utilities" → [{{"type": "Pay bill Online", "link": "seattle.gov/utilities"}}]
        - Email: "email@provider.com" → [{{"type": "", "email": "email@provider.com"}}]

        For customer names:
        - "COMPANY NAME" → [{{"type": "Property Owner", "name": "COMPANY NAME"}}]

        For payments/fees/adjustments from single values to arrays:
        - payments_applied: -1073.54 → [{{"payment_details": "", "payment_date": "2025-12-17", "payment_amount": -1073.54}}]

        For meter_level_data (most complex transformation):
        - Extract unique meters from line items based on meter_number
        - Create meter objects with meter_id (M1, M2, etc.), meter_number, readings, and usage
        - Organize meter_reading array with service dates, previous/current readings, usage
        - Separate meter data from charge data

        {tax_instructions}

        For service_level_data structure:
        - Group by service type (Water Service, Sewer Service, etc.)
        - Move meter information into meter_level_data array within each service
        - Move line item charges into charge_groups array
        - Create appropriate charge group names
        - Calculate group_subtotal for each charge group
        - Set service_type to standard value (WATER, SEWER, etc.)

        METADATA HANDLING:
        - Remove any validation objects (line_item_charges_validation, total_amount_validation, etc.)
        - These are internal and not part of the standard template

        Return ONLY the transformed data in the standard format. Do not include explanations or extra text."""

    try:
        logger.info(f"Calling OpenAI API to transform {provider_name} bill...")

        response = client.beta.chat.completions.parse(
            model="gpt-4o-2024-08-06",  # Supports structured outputs
            messages=[
                {
                    "role": "system",
                    "content": "You are a data transformation expert that converts utility bill data to a standardized format. Always follow the exact structure specified.",
                },
                {"role": "user", "content": prompt},
            ],
            response_format=StandardUtilityBill,
            temperature=0,  # Deterministic output
        )

        logger.info("Transformation successful!")
        return response.choices[0].message.parsed

    except Exception as e:
        logger.error(f"Error during transformation: {e}")
        raise


def transform_bill_file(
    input_path: str, output_path: str, provider_name: str, client: OpenAI = None
) -> StandardUtilityBill:
    """
    Transform a provider bill JSON file to standard format.

    Args:
        input_path: Path to provider-specific JSON file
        output_path: Path to save standardized JSON file
        provider_name: Name of the provider
        client: OpenAI client instance. If None, creates a new one.

    Returns:
        StandardUtilityBill object

    Raises:
        Exception: If transformation fails
    """

    # Load provider JSON
    logger.info(f"Loading file: {input_path}")
    with open(input_path, "r") as f:
        provider_json = json.load(f)

    # Transform using LLM
    standard_bill = transform_to_standard(provider_json, provider_name, client)

    # Ensure output directory exists
    output_file = Path(output_path)
    output_file.parent.mkdir(exist_ok=True, parents=True)

    # Save to output
    with open(output_path, "w") as f:
        f.write(
            standard_bill.model_dump_json(
                indent=4, exclude_none=False, exclude_unset=False
            )
        )

    logger.info(f" Transformed {provider_name} bill successfully!")
    logger.info(f"  Input: {input_path}")
    logger.info(f"  Output: {output_path}")

    return standard_bill


if __name__ == "__main__":
    # Test transformation
    import sys

    if len(sys.argv) < 3:
        print(
            "Usage: python llm_transformer.py <input_json> <output_json> [provider_name]"
        )
        sys.exit(1)

    input_file = sys.argv[1]
    output_file = sys.argv[2]
    provider = sys.argv[3] if len(sys.argv) > 3 else "Unknown Provider"

    transform_bill_file(input_file, output_file, provider)
