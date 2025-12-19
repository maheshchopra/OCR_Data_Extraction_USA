from pathlib import Path
import shutil

# Configure your folders here
SOURCE_ROOT = Path(r"C:\Users\tejas\Documents\Utility Bills Project\Sridhar PDFs\Downloaded Bills 2025-12-18")
INBOX_DIR = Path(r"C:\Users\tejas\Documents\Utility Bills Project\first_phase\version_2\inbox")

def ensure_inbox():
    INBOX_DIR.mkdir(parents=True, exist_ok=True)

def next_unique_name(target_dir: Path, original_name: str) -> Path:
    candidate = target_dir / original_name
    if not candidate.exists():
        return candidate
    stem, suffix = Path(original_name).stem, Path(original_name).suffix
    counter = 1
    while True:
        new_name = f"{stem}_{counter:03d}{suffix}"
        candidate = target_dir / new_name
        if not candidate.exists():
            return candidate
        counter += 1


def collect_and_copy_pdfs():
    ensure_inbox()
    pdf_files = SOURCE_ROOT.rglob("*.pdf")
    copied = 0
    for pdf_path in pdf_files:
        if not pdf_path.is_file():
            continue
        destination = next_unique_name(INBOX_DIR, pdf_path.name)
        shutil.copy2(pdf_path, destination)
        copied += 1
    print(f"Copied {copied} PDF files to {INBOX_DIR}")


if __name__ == "__main__":
    collect_and_copy_pdfs()