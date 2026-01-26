# Utility Bills Data Extraction System

## Overview

This project is an automated utility bill data extraction system that processes PDF utility bills and converts them into structured JSON data. The system uses OpenAI's GPT-4o API with structured outputs to intelligently extract billing information from various utility providers across Washington State and beyond.

The system is designed to handle multiple utility providers with different bill formats, automatically detecting the provider and applying the appropriate extraction logic and validation rules.

## Key Features

- Automatic provider detection from PDF bills
- Support for 30+ utility providers with different bill formats
- Structured data extraction using Pydantic models
- Provider-specific validation and post-processing
- Automatic file organization (inbox, processed, unprocessed)
- Comprehensive logging system
- Handles multiple bill format variants (e.g., Seattle City Light residential vs commercial)

## Supported Utility Providers

### Electric Utilities
- **Seattle City Light** (2 formats: residential and commercial)
- **Puget Sound Energy Electric**
- **Snohomish County PUD** (Skagit)
- **Everett Public Works**
- **CenTrio Energy Seattle**

### Gas Utilities
- **Puget Sound Energy Gas**
- **Puget Sound Energy Gas and Electric** (combined bills)

### Water Utilities
- **Seattle Public Utilities** (SPU)
- **Sammamish Plateau Water**
- **King County Water District 20**
- **Alderwood Water & Wastewater District**
- **City of Bellevue**
- **City of Lynnwood**
- **City of Kent**
- **City of Redmond**
- **City of Renton**
- **City of Edmonds**
- **City of Lacey**
- **City of Bothell**
- **City of Olympia**
- **City of Auburn**
- **City of Ocean Shores**
- **City of Frisco**

### Sewer/Wastewater Utilities
- **King County Wastewater Treatment Division**
- **Valley View Sewer District**
- **Southwest Suburban Sewer District (SSSD)**

### Waste Management
- **Waste Management of Washington**
- **Republic Services**
- **Rubatino Refuse Removal**
- **Recology King County**
- **Cedar Grove Organics Recycling LLC**

## System Architecture

### High-Level Workflow

```
PDF Bill (inbox)
    ↓
Upload to OpenAI
    ↓
Detect Provider (LLM)
    ↓
Select Prompt Template
    ↓
Extract Data (LLM + Pydantic)
    ↓
Post-process & Validate
    ↓
Save JSON + Move PDF (processed)
```

### Core Components

1. **Extractor** (`extractor.py`)
   - Main orchestration class
   - Handles PDF upload, extraction workflow, and file management
   - Coordinates all components

2. **Provider Router** (`provider_router.py`)
   - Detects utility provider from PDF
   - Routes to appropriate prompt, model, and functions
   - Manages provider-specific configurations

3. **Prompts** (`prompts/`)
   - Provider-specific extraction instructions
   - Defines what data to extract and how to interpret bill formats
   - Plain text templates used by the LLM

4. **Pydantic Models** (`pydantic_models/`)
   - Type-safe data schemas for each provider
   - Ensures consistent JSON structure
   - Validates extracted data types

5. **Provider Functions** (`provider_functions/`)
   - Post-processing logic (e.g., calculations, data transformations)
   - Validation checks (e.g., verifying totals match)
   - Provider-specific business rules

## Directory Structure

```
utility_bills_project/phase_2/version_1/
├── docs/                           # Documentation
├── logs/                           # Application logs
│   └── utility_bills.log          # Rotating log file
├── src/
│   ├── data/
│   │   ├── inbox/                 # Drop PDFs here for processing
│   │   ├── processed/
│   │   │   ├── json/              # Extracted JSON data
│   │   │   └── pdf/               # Successfully processed PDFs
│   │   └── unprocessed/
│   │       ├── json/              # JSON from failed validations
│   │       └── pdf/               # PDFs that failed processing
│   └── utility_bills/
│       ├── extractor.py           # Main extraction orchestrator
│       ├── provider_router.py     # Provider detection & routing
│       ├── logging_setup.py       # Logging configuration
│       ├── prompts/               # LLM prompt templates (30+ files)
│       ├── pydantic_models/       # Data schemas (33 files)
│       └── provider_functions/    # Post-processing & validation (30+ files)
├── requirements.txt               # Python dependencies
└── tests/                         # Test files (if any)
```

## How It Works

### 1. Provider Detection

When a PDF is uploaded, the system uses a lightweight LLM call to identify the utility provider:

```python
provider_name = detect_provider_from_file_id(file_id)
```

The LLM examines the bill header, logos, contact information, and formatting to determine which provider issued the bill. For providers with multiple formats (like Seattle City Light), it also detects the specific format variant.

### 2. Prompt Selection

Based on the detected provider, the system selects the appropriate prompt template:

```python
prompt_path = get_prompt_path_for_provider(project_root, provider_name)
prompt = load_prompt(prompt_path)
```

Each prompt contains detailed instructions for extracting data from that provider's specific bill format.

### 3. Data Extraction

The system uses OpenAI's structured output feature to extract data according to a Pydantic model:

```python
model_class = get_model_for_provider(provider_name)
extracted_data = extract_json_from_pdf(file_id, prompt, model_class)
```

This ensures the extracted data matches the expected schema and data types.

### 4. Post-Processing & Validation

After extraction, provider-specific functions validate and enhance the data:

```python
processed_data = postprocess_for_provider(provider_name, extracted_data)
validation_passed = check_validation_for_provider(provider_name, processed_data)
```

Common validations include:
- Line item charges sum to subtotals
- Subtotals plus balance equals total amount due
- Date range calculations
- Unit conversions

### 5. File Organization

Based on validation results:
- **Success**: JSON saved to `processed/json/`, PDF moved to `processed/pdf/`
- **Failure**: JSON saved to `unprocessed/json/`, PDF moved to `unprocessed/pdf/`

## Data Models

All extracted data follows a consistent three-level structure:

### Statement Level Data
Financial summary information:
- Bill date
- Previous balance
- Payments applied
- Current charges
- Total amount due
- Due date
- Late fee information

### Account Level Data
Account and provider information:
- Provider name, website, phone
- Account number
- Customer name and address
- Service address
- Account type

### Meter/Service Level Data
Detailed usage and charges:
- Service name (e.g., "Electric Service", "Water Service")
- Meter readings (previous, current)
- Usage amounts and units
- Line item charges
- Rate information
- Service dates

## Special Features

### Multi-Format Support

Some providers have multiple bill formats. For example, Seattle City Light has:

1. **Residential Format** (`scl.txt`)
   - Single service category (KWH) per meter
   - Simple charges: Base Service + Seasonal Energy
   - Uses `kWh Multiplier` column

2. **Commercial Format** (`scl_2.txt`)
   - Multiple service categories (KWH, KW, KVRH) per meter
   - Complex charges: Base Service + Small General Energy + Power Factor Penalty
   - Uses `Multiplier` column
   - Includes power factor calculations

The system automatically detects which format to use based on bill content.

### Validation System

Each provider can implement custom validation logic:

```python
# Example: Seattle City Light validation
def compute_line_item_charges_validation(utility_bill, tolerance=0.01):
    """Verify line items sum to service amount"""
    # ... validation logic ...

def compute_total_amount_validation(utility_bill, tolerance=0.01):
    """Verify balance + charges = total due"""
    # ... validation logic ...
```

Validation results are included in the output JSON for auditing.

## Configuration

### API Key Setup

The system uses the OpenAI Python client, which reads the API key from the environment variable:

```
OPENAI_API_KEY=your-api-key-here
```

Set this in your system environment variables (Windows 11) rather than using an `.env` file.

### Model Selection

- **Provider Detection**: Uses `gpt-4.1-mini` for cost efficiency
- **Data Extraction**: Uses `gpt-4o` for high accuracy structured output

## Adding a New Provider

To add support for a new utility provider:

### 1. Create the Prompt
Create `prompts/provider_name.txt` with extraction instructions:
```text
You are an information extraction system.

Goal: Extract the following JSON fields from the attached utility bill.
Output: Return ONLY a single JSON object matching the schema exactly.

Global rules:
- Use ONLY information present in the document.
- If a field is not present, return null.
...
```

### 2. Create the Pydantic Model
Create `pydantic_models/provider_name.py`:
```python
from pydantic import BaseModel, Field
from typing import Optional, List

class StatementLevelData(BaseModel):
    bill_date: Optional[str] = None
    # ... other fields ...

class ProviderNameBillExtract(BaseModel):
    statement_level_data: StatementLevelData
    # ... other sections ...
```

### 3. Create Provider Functions
Create `provider_functions/provider_name.py`:
```python
def postprocess_provider_name(utility_bill: dict) -> dict:
    """Post-processing and validation logic"""
    # ... custom logic ...
    return utility_bill

def check_validation_passed(utility_bill: dict) -> bool:
    """Check if validation passed"""
    # ... validation checks ...
    return True
```

### 4. Update Provider Router
Add entries to `provider_router.py`:
```python
# Import the modules
from provider_functions import provider_name
from pydantic_models import ProviderNameBillExtract

# Add to dictionaries
PROVIDER_PROMPTS = {
    # ...
    "provider display name": "provider_name.txt",
}

PROVIDER_POSTPROCESSORS = {
    # ...
    "provider display name": provider_name.postprocess_provider_name,
}

PROVIDER_VALIDATION_CHECKERS = {
    # ...
    "provider display name": provider_name.check_validation_passed,
}

PROVIDER_MODELS = {
    # ...
    "provider display name": ProviderNameBillExtract,
}
```

### 5. Update Detection Logic
If needed, add special detection logic in `detect_provider_from_file_id()`:
```python
"- For Provider Name bills, look for specific identifying text..."
```

## Usage Example

```python
from pathlib import Path
from extractor import Extractor

# Initialize extractor
extractor = Extractor(project_root=Path("path/to/project"))

# Process a single PDF
pdf_path = Path("path/to/bill.pdf")
result = extractor.process_pdf(pdf_path)

if result['success']:
    print(f"Extracted data saved to: {result['json_path']}")
else:
    print(f"Extraction failed: {result['error']}")

# Process all PDFs in inbox
results = extractor.process_inbox()
print(f"Processed {len(results)} bills")
```

## Logging

The system uses a comprehensive logging setup with:
- Console output (INFO level)
- File output with rotation (DEBUG level)
- Log files in `logs/utility_bills.log`
- Automatic rotation at 10MB, keeps 5 backups

Log entries include:
- Provider detection results
- Extraction success/failure
- Validation results
- Error details and stack traces
- File movement operations

## Dependencies

Key Python packages:
- `openai` - OpenAI API client
- `pydantic` - Data validation and schema definition
- `tqdm` - Progress bars
- Standard library: `pathlib`, `json`, `shutil`, `logging`

## Design Principles

1. **Open Source Only**: All dependencies are free and open source software
2. **Type Safety**: Extensive use of Pydantic for runtime type checking
3. **Provider Modularity**: Each provider's logic is isolated and independent
4. **Validation First**: All extracted data is validated before being marked as processed
5. **Explainability**: Validation results and intermediate steps are preserved
6. **Error Resilience**: Failed extractions are logged and saved for review
7. **Environment Variables**: API keys stored in system environment, not code

## Troubleshooting

### Common Issues

**Provider Not Detected**
- Check if provider is in the allowed list in `detect_provider_from_file_id()`
- Verify PDF is readable and not corrupted
- Check logs for LLM's detection response

**Validation Failures**
- Review the validation objects in the output JSON
- Check `difference` fields to see calculation mismatches
- Verify prompt instructions match actual bill format

**Missing Data (null values)**
- Check if field exists in the actual bill
- Review prompt instructions for that specific field
- Ensure LLM understands where to find the data

## Future Enhancements

Potential areas for expansion:
- Support for more utility providers
- OCR preprocessing for scanned bills
- Batch processing interface
- Web API for remote processing
- Database integration for historical data
- Analytics and reporting features
- Multi-language bill support

## License

This is a private utility project. All code is proprietary.

## Contact

For questions or issues, refer to the project repository or contact the project maintainer.

---

**Last Updated**: January 2026  
**Version**: 2.1  
**Python Version**: 3.10+
