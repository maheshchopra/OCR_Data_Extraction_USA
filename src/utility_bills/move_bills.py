import shutil
from pathlib import Path
import logging
from logging_setup import setup_logging

# Setup logging
logger = setup_logging(__name__)


def copy_files_to_inbox(source_folder, inbox_folder, file_extensions=None):
    """
    Recursively find all files with specified extensions in source_folder and copy them to inbox_folder.

    Args:
        source_folder: Path to the folder containing files (may have subfolders)
        inbox_folder: Path to the inbox folder where files should be copied
        file_extensions: List of file extensions to search for (e.g., ['.pdf', '.png'])
                        If None, defaults to ['.pdf', '.png']
    """

    if file_extensions is None:
        file_extensions = [".pdf", ".png"]

    source_path = Path(source_folder)
    inbox_path = Path(inbox_folder)

    # Ensure inbox folder exists
    inbox_path.mkdir(parents=True, exist_ok=True)

    # Check if source folder exists
    if not source_path.exists():
        logger.error(f"Source folder does not exist: {source_folder}")
        return

    # Find all files with specified extensions recursively
    all_files = []
    for ext in file_extensions:
        # Use rglob to find files recursively with the specified extension
        files = list(source_path.rglob(f"*{ext}"))
        all_files.extend(files)
        logger.info(f"Found {len(files)} {ext.upper()} file(s)")

    if not all_files:
        logger.info(
            f"No files found with extensions {file_extensions} in {source_folder}"
        )
        return

    logger.info(f"Found {len(all_files)} total file(s) to process")

    # Copy each file to inbox
    copy_count = 0
    for file_path in all_files:
        try:
            destination = inbox_path / file_path.name

            # Handle duplicate filenames
            if destination.exists():
                logger.warning(f"File already exists in inbox: {file_path.name}")
                # Add a counter to make the filename unique
                counter = 1
                while destination.exists():
                    stem = file_path.stem
                    suffix = file_path.suffix
                    destination = inbox_path / f"{stem}_{counter}{suffix}"
                    counter += 1
                logger.info(f"Renaming to: {destination.name}")

            shutil.copy2(str(file_path), str(destination))
            logger.info(f"Copied: {file_path.name} -> {destination}")
            copy_count += 1

        except Exception as e:
            logger.error(f"Failed to copy {file_path.name}: {e}")

    logger.info(f"Successfully copied {copy_count} out of {len(all_files)} file(s)")


def main():
    # Define paths relative to the project structure
    base_dir = Path(__file__).parent.parent
    source_folder = r"C:\Users\tejas\Downloads\New Folder"
    inbox_folder = base_dir / "data" / "inbox"

    logger.info(f"Source folder: {source_folder}")
    logger.info(f"Inbox folder: {inbox_folder}")

    # Copy both PDFs and PNGs
    copy_files_to_inbox(source_folder, inbox_folder, file_extensions=[".pdf", ".png"])


if __name__ == "__main__":
    main()
