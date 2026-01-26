from pathlib import Path
from .llm_transformer import transform_to_standard
from .provider_detector import load_and_detect_provider
import sys

sys.path.insert(0, str(Path(__file__).parent.parent))

from standard_template.standard_model import StandardUtilityBill
from typing import Optional
import logging
from openai import OpenAI

# Setup logging
logging.basicConfig(
    level=logging.INFO, format="%(asctime)s - %(levelname)s - %(message)s"
)
logger = logging.getLogger(__name__)


def transform_single_bill(
    input_path: str, output_path: str, client: OpenAI = None
) -> Optional[StandardUtilityBill]:
    """
    Transform a single processed JSON bill to standard format.
    Automatically detects provider from JSON content.

    Args:
        input_path: Path to processed JSON file
        output_path: Path to save standardized JSON file
        client: OpenAI client instance. If None, creates a new one.

    Returns:
        StandardUtilityBill object if successful, None if failed
    """

    if client is None:
        client = OpenAI()

    try:
        # Load JSON and detect provider automatically
        logger.info(f"Loading file: {input_path}")
        provider_json, provider_name = load_and_detect_provider(input_path)

        logger.info(f"Detected provider: {provider_name}")

        # Transform using LLM
        logger.info("Transforming to standard format...")
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

        logger.info(f" Successfully transformed bill!")
        logger.info(f"  Provider: {provider_name}")
        logger.info(f"  Input: {input_path}")
        logger.info(f"  Output: {output_path}")

        return standard_bill

    except Exception as e:
        logger.error(f" Error transforming {input_path}: {e}")
        import traceback

        traceback.print_exc()
        return None


def batch_transform_directory(
    input_dir: str = "data/processed/json",
    output_dir: str = "data/json_results",
    client: OpenAI = None,
):
    """
    Transform all JSON files in the processed directory.

    Args:
        input_dir: Directory containing processed JSON files
        output_dir: Directory to save standardized JSON files
        client: OpenAI client instance. If None, creates a new one.
    """

    if client is None:
        client = OpenAI()

    input_path = Path(input_dir)
    output_path = Path(output_dir)

    # Create output directory if it doesn't exist
    output_path.mkdir(exist_ok=True, parents=True)

    # Find all JSON files
    json_files = list(input_path.glob("*.json"))

    if not json_files:
        logger.warning(f"No JSON files found in {input_dir}")
        return

    logger.info(f"Found {len(json_files)} JSON files to process")

    success_count = 0
    failed_count = 0

    for json_file in json_files:
        # Create output filename (keep same name)
        output_file = output_path / json_file.name

        # Transform
        result = transform_single_bill(str(json_file), str(output_file), client)

        if result:
            success_count += 1
        else:
            failed_count += 1

        logger.info("-" * 60)

    # Summary
    logger.info("=" * 60)
    logger.info(f"Batch processing complete!")
    logger.info(f"  Successful: {success_count}")
    logger.info(f"  Failed: {failed_count}")
    logger.info(f"  Total: {len(json_files)}")
    logger.info("=" * 60)


def process_latest_bill(
    input_dir: str = "data/processed/json",
    output_dir: str = "data/json_results",
    client: OpenAI = None,
) -> Optional[StandardUtilityBill]:
    """
    Process the most recently created JSON file in the processed directory.
    Useful for automated workflows that trigger after each PDF is processed.

    Args:
        input_dir: Directory containing processed JSON files
        output_dir: Directory to save standardized JSON files
        client: OpenAI client instance. If None, creates a new one.

    Returns:
        StandardUtilityBill object if successful, None if no files or failed
    """

    if client is None:
        client = OpenAI()

    input_path = Path(input_dir)

    # Find all JSON files
    json_files = list(input_path.glob("*.json"))

    if not json_files:
        logger.warning(f"No JSON files found in {input_dir}")
        return None

    # Get the most recently modified file
    latest_file = max(json_files, key=lambda f: f.stat().st_mtime)

    logger.info(f"Processing latest bill: {latest_file.name}")

    # Create output filename
    output_file = Path(output_dir) / latest_file.name

    # Transform
    return transform_single_bill(str(latest_file), str(output_file), client)


if __name__ == "__main__":
    import sys

    if len(sys.argv) > 1:
        arg = sys.argv[1]

        if arg == "--batch":
            # Process all files
            batch_transform_directory()

        elif arg == "--latest":
            # Process most recent file
            process_latest_bill()

        else:
            # Process specific file
            input_file = arg
            output_file = sys.argv[2] if len(sys.argv) > 2 else None

            if not output_file:
                # Generate output filename
                input_path = Path(input_file)
                output_file = f"data/json_results/{input_path.name}"

            transform_single_bill(input_file, output_file)
    else:
        print("Usage:")
        print("  Transform single file:")
        print(
            "    python universal_transformer.py <input_json_path> [output_json_path]"
        )
        print()
        print("  Transform all files:")
        print("    python universal_transformer.py --batch")
        print()
        print("  Transform latest file:")
        print("    python universal_transformer.py --latest")
