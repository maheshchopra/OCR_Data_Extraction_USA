import json
import shutil
from pathlib import Path

from logging_setup import setup_logging
from openai import OpenAI
from provider_router import (
    check_validation_for_provider,
    detect_provider_from_file_id,
    get_model_for_provider,
    get_prompt_path_for_provider,
    postprocess_for_provider,
)


class Extractor:
    """
    A class for extracting structured data from utility bill PDFs using OpenAI's API.

    This class handles the complete workflow of processing PDF files:
    - Uploading PDFs to OpenAI
    - Detecting the utility provider
    - Extracting structured JSON data using LLM
    - Saving extracted data and organizing processed files

    The class automatically sets up logging to both console and log files,
    and provides error handling for each processing step.
    """

    def __init__(
        self, client: OpenAI | None = None, project_root: str | Path | None = None
    ):
        """
        Initialize the Extractor with an OpenAI client and logging setup.

        Args:
            client: OpenAI client instance.
            project_root: Path to the project root directory. Used to set up
                          the logs directory at <project_root>/logs.

        Note:
            The logger is configured to write to both console and a rotating log file
            at <project_root>/logs/utility_bills.log.
        """

        self.client = client or OpenAI()

        if project_root is None:
            project_root = Path(__file__).resolve().parents[2]
        else:
            project_root = Path(project_root)

        log_dir = project_root / "logs"
        self.logger = setup_logging(log_dir)

    def load_prompt(self, file_path: str | Path) -> str:
        """
        Load a prompt template from a text file.

        Args:
            file_path: Path to the prompt text file to load.

        Returns:
            The contents of the prompt file as a string.

        Raises:
            FileNotFoundError: If the prompt file does not exist.
            UnicodeDecodeError: If the file cannot be decoded as UTF-8.
        """

        return Path(file_path).read_text(encoding="utf-8")

    def upload_pdf(self, file_path: str | Path) -> str:
        """
        Upload a PDF file to OpenAI's file storage.

        Args:
            file_path: Path to the PDF file to upload.

        Returns:
            The OpenAI file ID of the uploaded PDF.

        Raises:
            FileNotFoundError: If the PDF file does not exist.
            openai.APIError: If the upload fails due to API issues.
        """

        with open(file_path, "rb") as f:
            return self.client.files.create(file=f, purpose="user_data").id

    def extract_json_from_pdf(self, file_id: str, prompt: str, model_class) -> dict:
        """
        Extract structured JSON data from a PDF using OpenAI's structured output API.

        This method uses GPT-4o to parse the PDF and extract utility bill information
        according to the provided Pydantic model schema.

        Args:
            file_id: The OpenAI file ID of the uploaded PDF.
            prompt: The prompt text instructing the LLM on what to extract.
            model_class: The Pydantic model class to use for structured output.

        Returns:
            A dictionary containing the extracted utility bill data, conforming to
            the provided model schema.

        Raises:
            openai.APIError: If the API call fails.
            ValidationError: If the extracted data doesn't match the Pydantic schema.
        """

        response = self.client.responses.parse(
            model="gpt-4o-2024-08-06",
            input=[
                {
                    "role": "user",
                    "content": [
                        {"type": "input_file", "file_id": file_id},
                        {"type": "input_text", "text": prompt},
                    ],
                }
            ],
            text_format=model_class,
        )
        return response.output_parsed.model_dump()

    def process_inbox_pdfs(self, project_root: str | Path) -> list[dict]:
        """
        Process all PDF files in the inbox directory.

        This method processes each PDF file found in <project_root>/src/data/inbox:
        1. Uploads the PDF to OpenAI
        2. Detects the utility provider and selects the appropriate prompt
        3. Extracts structured JSON data using the LLM
        4. Saves the JSON to <project_root>/src/data/processed/json/
        5. Moves the processed PDF to <project_root>/src/data/processed/pdf/

        Each file is processed independently, and errors for one file don't stop
        processing of other files. All operations are logged.

        Args:
            project_root: Path to the project root directory containing the
                         src/data/inbox and src/data/processed directories.

        Returns:
            A list of dictionaries, one per processed PDF. Each dictionary contains:
            - "pdf": Path to the original PDF file
            - "ok": Boolean indicating success (True) or failure (False)
            - "json_path": Path to saved JSON file (only if ok=True)
            - "moved_pdf_path": Path where PDF was moved (only if ok=True)
            - "error": Error message string (only if ok=False)

        Note:
            The processed/json and processed/pdf directories are created automatically
            if they don't exist. PDFs are processed in sorted order by filename.
        """

        project_root = Path(project_root)
        inbox_dir = project_root / "src" / "data" / "inbox"

        processed_json_dir = project_root / "src" / "data" / "processed" / "json"
        processed_pdf_dir = project_root / "src" / "data" / "processed" / "pdf"
        unprocessed_json_dir = project_root / "src" / "data" / "unprocessed" / "json"
        unprocessed_pdf_dir = project_root / "src" / "data" / "unprocessed" / "pdf"

        processed_json_dir.mkdir(parents=True, exist_ok=True)
        processed_pdf_dir.mkdir(parents=True, exist_ok=True)
        unprocessed_json_dir.mkdir(parents=True, exist_ok=True)
        unprocessed_pdf_dir.mkdir(parents=True, exist_ok=True)

        pdf_paths = sorted(inbox_dir.glob("*.pdf"))
        self.logger.info(f"Found {len(pdf_paths)} PDF(s) in inbox. Starting extraction")

        results: list[dict] = []

        for pdf_path in pdf_paths:
            self.logger.info(f"Processing PDF: {pdf_path.name}")
            file_result = {"pdf": str(pdf_path), "ok": False}

            try:
                file_id = self.upload_pdf(str(pdf_path))
                self.logger.info(
                    "Uploaded PDF, detecting the provider and selecting the prompt"
                )

                # Detect provider
                provider_name = detect_provider_from_file_id(file_id)
                self.logger.info(f"Detected provider: {provider_name}")

                # Get its prompt
                prompt_path = get_prompt_path_for_provider(project_root, provider_name)
                self.logger.info(f"Using prompt: {prompt_path.name}")

                # Extract JSON
                prompt_text = self.load_prompt(str(prompt_path))
                self.logger.info("Calling LLM to extract the JSON")

                # provider-specific post‑processing
                model_class = get_model_for_provider(provider_name)
                if model_class is None:
                    raise ValueError(
                        f"No Pydantic model registered for provider: {provider_name}"
                    )

                extracted = self.extract_json_from_pdf(
                    file_id, prompt_text, model_class
                )
                extracted = postprocess_for_provider(provider_name, extracted)

                # Check validation results using provider-specific checker
                validation_passed = check_validation_for_provider(
                    provider_name, extracted
                )
                self.logger.info(
                    f"Validation {'passed' if validation_passed else 'failed'} for {pdf_path.name}"
                )

                # Determine destination folders based on validation
                if validation_passed:
                    json_dir = processed_json_dir
                    pdf_dir = processed_pdf_dir
                    folder_type = "processed"
                else:
                    json_dir = unprocessed_json_dir
                    pdf_dir = unprocessed_pdf_dir
                    folder_type = "unprocessed"

                # Save JSON
                json_path = json_dir / f"{pdf_path.stem}.json"
                json_path.write_text(
                    json.dumps(
                        extracted, indent=4, ensure_ascii=False, sort_keys=False
                    ),
                    encoding="utf-8",
                )
                self.logger.debug(f"Saved JSON to {json_path}")

                pdf_dest = pdf_dir / pdf_path.name
                shutil.move(pdf_path, pdf_dest)
                self.logger.debug(f"Moved PDF to {pdf_dest} ({folder_type})")

                file_result.update(
                    {
                        "ok": True,
                        "json_path": str(json_path),
                        "moved_pdf_path": str(pdf_dest),
                        "validation_passed": validation_passed,
                    }
                )

                self.logger.info(f"Finished: {pdf_path.name} -> {folder_type}")

            except Exception as e:
                self.logger.error(
                    f"Error processing {pdf_path.name}: {repr(e)}", exc_info=True
                )
                file_result["error"] = repr(e)

            results.append(file_result)

        self.logger.info("All PDFs processed.")
        return results


if __name__ == "__main__":
    project_root = Path(__file__).resolve().parents[2]
    extractor = Extractor()
    results = extractor.process_inbox_pdfs(project_root)
    print(json.dumps(results, indent=2))
