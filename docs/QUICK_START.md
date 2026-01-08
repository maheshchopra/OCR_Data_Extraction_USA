# Quick Start Guide

Get up and running with the Utility Bills Data Extraction System in minutes.

## Prerequisites

- Python 3.10 or higher
- OpenAI API key
- Windows 11 (or other OS with appropriate path adjustments)

## Installation

### 1. Install Python Dependencies

Navigate to the project root and install required packages:

```powershell
cd C:\Users\tejas\Documents\utility_bills_project\phase_2\version_1
pip install -r requirements.txt
```

### 2. Set Up OpenAI API Key

Add your OpenAI API key to system environment variables:

**Windows 11:**
1. Press `Win + X` and select "System"
2. Click "Advanced system settings"
3. Click "Environment Variables"
4. Under "User variables", click "New"
5. Variable name: `OPENAI_API_KEY`
6. Variable value: Your OpenAI API key
7. Click OK to save

**Verify it's set:**
```powershell
echo $env:OPENAI_API_KEY
```

### 3. Verify Installation

```python
python -c "import openai; print('OpenAI library installed successfully')"
```

## Basic Usage

### Process a Single PDF

```python
from pathlib import Path
from src.utility_bills.extractor import Extractor

# Initialize the extractor
extractor = Extractor(project_root=Path.cwd())

# Process a PDF file
pdf_path = Path("path/to/your/utility_bill.pdf")
result = extractor.process_pdf(pdf_path)

# Check results
if result['success']:
    print(f"Success! JSON saved to: {result['json_path']}")
    print(f"Provider: {result['provider']}")
    print(f"Validation passed: {result['validation_passed']}")
else:
    print(f"Failed: {result['error']}")
```

### Process Multiple PDFs from Inbox

1. Place PDF bills in the `src/data/inbox/` folder

2. Run the processor:

```python
from pathlib import Path
from src.utility_bills.extractor import Extractor

extractor = Extractor(project_root=Path.cwd())
results = extractor.process_inbox()

# Print summary
for result in results:
    status = "✓" if result['success'] else "✗"
    print(f"{status} {result['filename']} - {result.get('provider', 'Unknown')}")
```

### Check Results

After processing:
- **Successful extractions**: 
  - JSON in `src/data/processed/json/`
  - PDF in `src/data/processed/pdf/`
- **Failed extractions**: 
  - JSON in `src/data/unprocessed/json/` (if extracted but validation failed)
  - PDF in `src/data/unprocessed/pdf/`
- **Logs**: `logs/utility_bills.log`

## Example Script

Save this as `process_bills.py` in the project root:

```python
#!/usr/bin/env python3
"""
Simple script to process all utility bills in the inbox folder.
"""

from pathlib import Path
from src.utility_bills.extractor import Extractor


def main():
    # Initialize extractor
    project_root = Path(__file__).parent
    extractor = Extractor(project_root=project_root)
    
    # Process all PDFs in inbox
    print("Processing bills from inbox...")
    results = extractor.process_inbox()
    
    # Print summary
    print("\n" + "="*60)
    print("PROCESSING SUMMARY")
    print("="*60)
    
    success_count = sum(1 for r in results if r['success'])
    fail_count = len(results) - success_count
    
    print(f"\nTotal bills processed: {len(results)}")
    print(f"Successful: {success_count}")
    print(f"Failed: {fail_count}")
    
    if results:
        print("\nDetails:")
        print("-" * 60)
        for result in results:
            status = "✓ SUCCESS" if result['success'] else "✗ FAILED"
            provider = result.get('provider', 'Unknown')
            validation = result.get('validation_passed', False)
            
            print(f"\n{status}: {result['filename']}")
            print(f"  Provider: {provider}")
            
            if result['success']:
                print(f"  Validation: {'Passed' if validation else 'Failed'}")
                print(f"  JSON: {result.get('json_path', 'N/A')}")
            else:
                print(f"  Error: {result.get('error', 'Unknown error')}")
    
    print("\n" + "="*60)
    print("Check logs/utility_bills.log for detailed information")
    print("="*60 + "\n")


if __name__ == "__main__":
    main()
```

Run it:
```powershell
python process_bills.py
```

## Understanding Output

### JSON Structure

Each extracted bill produces a JSON file with three main sections:

```json
{
    "statement_level_data": {
        "bill_date": "December 30, 2025",
        "total_amount_due": 3094.65,
        "total_amount_due_date": "January 20, 2026",
        ...
    },
    "account_level_data": {
        "provider": "CITY OF SEATTLE",
        "account_number": "4606830970",
        "customer_name": "BLANTON TURNER",
        ...
    },
    "meter_level_data": [
        {
            "service_name": "Electric Service",
            "current_service_amount": 46.0,
            "line_item_charges": [ ... ]
        }
    ]
}
```

See [DATA_STRUCTURE.md](DATA_STRUCTURE.md) for complete details.

### Validation Objects

Each JSON includes validation calculations:

```json
"total_amount_validation": {
    "calculated_total": 3094.65,
    "total_amount_due": 3094.65,
    "difference": 0.0,
    "is_match": true
}
```

- `is_match: true` → Bill calculations verified correctly
- `is_match: false` → Discrepancy detected, review manually

## Common Workflows

### 1. Monthly Bill Processing

```python
from pathlib import Path
from src.utility_bills.extractor import Extractor
import json

def process_monthly_bills():
    """Process all new bills and generate a summary report."""
    extractor = Extractor(project_root=Path.cwd())
    results = extractor.process_inbox()
    
    # Generate summary
    total_due = 0
    by_provider = {}
    
    for result in results:
        if result['success']:
            json_path = Path(result['json_path'])
            with open(json_path) as f:
                data = json.load(f)
                amount = data['statement_level_data']['total_amount_due']
                provider = data['account_level_data']['provider']
                
                total_due += amount or 0
                by_provider[provider] = by_provider.get(provider, 0) + (amount or 0)
    
    print(f"\nTotal amount due: ${total_due:.2f}")
    print("\nBy provider:")
    for provider, amount in sorted(by_provider.items()):
        print(f"  {provider}: ${amount:.2f}")

process_monthly_bills()
```

### 2. Validate Existing JSON Files

```python
from pathlib import Path
from src.utility_bills.provider_router import check_validation_for_provider
import json

def validate_all_processed():
    """Check validation status of all processed bills."""
    processed_dir = Path("src/data/processed/json")
    
    for json_file in processed_dir.glob("*.json"):
        with open(json_file) as f:
            data = json.load(f)
        
        provider = data['account_level_data']['provider'].lower()
        passed = check_validation_for_provider(provider, data)
        
        status = "✓" if passed else "✗"
        print(f"{status} {json_file.name}")

validate_all_processed()
```

### 3. Export to CSV

```python
import json
import csv
from pathlib import Path

def export_to_csv(output_file="bills_summary.csv"):
    """Export all processed bills to a CSV file."""
    processed_dir = Path("src/data/processed/json")
    
    with open(output_file, 'w', newline='', encoding='utf-8') as csvfile:
        writer = csv.writer(csvfile)
        writer.writerow([
            'Filename', 'Provider', 'Account Number', 'Bill Date',
            'Previous Balance', 'Current Charges', 'Total Due', 'Due Date'
        ])
        
        for json_file in processed_dir.glob("*.json"):
            with open(json_file) as f:
                data = json.load(f)
            
            stmt = data['statement_level_data']
            acct = data['account_level_data']
            
            writer.writerow([
                json_file.name,
                acct.get('provider'),
                acct.get('account_number'),
                stmt.get('bill_date'),
                stmt.get('previous_balance'),
                stmt.get('current_billing'),
                stmt.get('total_amount_due'),
                stmt.get('total_amount_due_date')
            ])
    
    print(f"Exported to {output_file}")

export_to_csv()
```

## Troubleshooting

### API Key Not Found

**Error**: `openai.OpenAIError: The api_key client option must be set`

**Solution**: Ensure OPENAI_API_KEY is set in environment variables and restart your terminal/IDE.

### Import Errors

**Error**: `ModuleNotFoundError: No module named 'openai'`

**Solution**: Install dependencies:
```powershell
pip install -r requirements.txt
```

### Provider Not Detected

**Error**: `ValueError: Model returned unknown provider`

**Solution**: 
1. Check if the provider is supported (see README.md for list)
2. Verify the PDF is readable (not a scanned image without OCR)
3. Check logs for what the LLM detected

### Validation Failures

Bills are moved to `unprocessed/` if validation fails. To investigate:

1. Check the JSON in `src/data/unprocessed/json/`
2. Look at validation objects (search for `"is_match": false`)
3. Review the `difference` field to see the discrepancy
4. Check logs for detailed error messages

Common causes:
- Bill has unusual formatting
- Multiple pages with subtotals
- Rounding differences in calculations
- Missing or null values in critical fields

### File Not Found

**Error**: `FileNotFoundError: [path] does not exist`

**Solution**: Ensure you're running from the project root and paths are correct:
```python
from pathlib import Path
project_root = Path(__file__).parent  # If in a script
# or
project_root = Path.cwd()  # If running interactively
```

## Best Practices

1. **Start Small**: Test with 1-2 PDFs before batch processing
2. **Check Logs**: Always review logs after processing for errors
3. **Validate Output**: Spot-check a few JSON files manually
4. **Keep Originals**: Never delete the original PDF bills
5. **Regular Backups**: Back up the `processed/` folder regularly
6. **Monitor Costs**: Track OpenAI API usage for budgeting

## Next Steps

- Read [README.md](README.md) for comprehensive system documentation
- Review [DATA_STRUCTURE.md](DATA_STRUCTURE.md) to understand output format
- Check example processed JSON files in `src/data/processed/json/`
- Review logs in `logs/utility_bills.log` to understand processing flow

## Getting Help

If you encounter issues:

1. Check the logs: `logs/utility_bills.log`
2. Review error messages carefully
3. Verify your setup (API key, dependencies, paths)
4. Test with a known-good PDF from a supported provider
5. Check if the issue is provider-specific

## API Costs

Approximate costs per bill (as of January 2026):
- Provider detection: ~$0.001 (gpt-4.1-mini)
- Data extraction: ~$0.02-0.05 (gpt-4o, depends on bill complexity)
- **Total per bill**: ~$0.02-0.05

For 30 bills per month: ~$0.60-$1.50/month

---

**Last Updated**: January 2026
