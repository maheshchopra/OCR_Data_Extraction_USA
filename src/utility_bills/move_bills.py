import shutil
from pathlib import Path
import logging
from logging_setup import setup_logging

# Setup logging
logger = setup_logging(__name__)


def copy_pdfs_to_inbox(source_folder, inbox_folder):
    """
    Recursively find all PDFs in source_folder and move them to inbox_folder.

    Args:
        source_folder: Path to the folder containing PDFs (may have subfolders)
        inbox_folder: Path to the inbox folder where PDFs should be moved
    """

    source_path = Path(source_folder)
    inbox_path = Path(inbox_folder)

    # Ensure inbox folder exists
    inbox_path.mkdir(parents=True, exist_ok=True)

    # Check if source folder exists
    if not source_path.exists():
        logger.error(f"Source folder does not exist: {source_folder}")
        return

    # Find all PDF files recursively
    pdf_files = list(source_path.rglob("*.pdf"))

    if not pdf_files:
        logger.info(f"No PDF files found in {source_folder}")
        return

    logger.info(f"Found {len(pdf_files)} PDF file(s)")

    # Move each PDF to inbox
    copy_count = 0
    for pdf_file in pdf_files:
        try:
            destination = inbox_path / pdf_file.name

            # Handle duplicate filenames
            if destination.exists():
                logger.warning(f"File already exists in inbox: {pdf_file.name}")
                # Add a counter to make the filename unique
                counter = 1
                while destination.exists():
                    stem = pdf_file.stem
                    destination = inbox_path / f"{stem}_{counter}.pdf"
                    counter += 1
                logger.info(f"Renaming to: {destination.name}")

            shutil.copy2(str(pdf_file), str(destination))
            logger.info(f"Copied: {pdf_file.name} -> {destination}")
            copy_count += 1

        except Exception as e:
            logger.error(f"Failed to move {pdf_file.name}: {e}")

    logger.info(f"Successfully moved {copy_count} out of {len(pdf_files)} PDF files")


def main():
    # Define paths relative to the project structure
    base_dir = Path(__file__).parent.parent
    source_folder = r"C:\Users\tejas\Downloads\2026-01-07"
    inbox_folder = base_dir / "data" / "inbox"

    logger.info(f"Source folder: {source_folder}")
    logger.info(f"Inbox folder: {inbox_folder}")

    copy_pdfs_to_inbox(source_folder, inbox_folder)


if __name__ == "__main__":
    main()
