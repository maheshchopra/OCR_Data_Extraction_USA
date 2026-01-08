# Provider-Specific Notes

This document contains special considerations, quirks, and implementation details for specific utility providers.

## Table of Contents

- [Seattle City Light](#seattle-city-light)
- [Seattle Public Utilities](#seattle-public-utilities)
- [Puget Sound Energy](#puget-sound-energy)
- [Common Issues](#common-issues)

---

## Seattle City Light

### Overview
Electric utility serving Seattle and some surrounding areas.

### Bill Formats

Seattle City Light has **two distinct bill formats** that require different processing:

#### 1. Residential Format (`scl.txt`)

**Characteristics:**
- Single service category (KWH) per meter
- Column header: "kWh Multiplier"
- Subtotal format: "Current Electric Service: [amount]"
- Line items: "Base Service Charge" + "Winter Residential Energy" (or other seasonal)
- Simple structure, typically for residential customers

**Pydantic Model:** `SeattleCityLightBillExtract`
- Uses field: `kwh_multiplier`

**Example addresses:**
- Single-family homes
- Individual apartment units
- Small businesses

#### 2. Commercial Format (`scl_2.txt`)

**Characteristics:**
- Multiple service categories per meter: KWH, KW, KVRH
- Column header: "Multiplier" (not "kWh Multiplier")
- Subtotal format: "Total for: [address] [amount]"
- Line items: "Base Service Charge" + "Small General Energy" + "Power Factor Penalty"
- Includes "Power Factor" column in meter readings
- May include "Your Net Meter kWh Statement" sections
- Complex structure with power factor calculations

**Pydantic Model:** `SeattleCityLightCommercialBillExtract`
- Uses field: `multiplier` (not `kwh_multiplier`)

**Example addresses:**
- Commercial buildings
- Multi-tenant properties
- Industrial facilities

### Automatic Format Detection

The system automatically detects which format to use by looking for:
- "Power Factor Penalty" line items
- "Small General Energy" charges
- Service categories "KVRH" or "KW"
- Total format "Total for: [address]"

If any of these indicators are found → Commercial format
Otherwise → Residential format

### Special Considerations

**Power Factor Penalties:**
- Only in commercial bills
- Calculated from KVRH readings
- May have null amounts if no penalty applies
- Uses different meter reading row than energy charges

**Multiple Service Addresses:**
- Commercial bills often have multiple service addresses (e.g., different floors/suites)
- Each address gets a separate entry in `meter_level_data`
- Each has its own subtotal

**Multiplier Values:**
- Residential: Typically 1
- Commercial: Often 40, 100, or other values
- Critical for calculating actual usage from meter readings

### Validation

Both formats use the same validation logic:

```python
# Line items should sum to service amount
sum(line_item_charges) ≈ current_service_amount

# Total should equal balance + all service amounts
balance + sum(current_service_amounts) ≈ total_amount_due
```

Tolerance: 0.01 (1 cent)

---

## Seattle Public Utilities

### Overview
Combined water, sewer, and drainage utility for Seattle.

### Bill Structure

**Services typically included:**
- Water (metered usage)
- Sewer (based on water usage)
- Drainage (flat rate based on property)
- Solid waste (if applicable)

### Special Considerations

**Multiple Service Types:**
- Each service (water, sewer, drainage) is a separate entry in `meter_level_data`
- Not all customers have all services

**Tiered Pricing:**
- Water rates vary by usage tier
- First X CCF at rate 1, next Y CCF at rate 2, etc.
- Line items will have multiple entries for the same service at different rates

**Adjustments:**
- Common to have credits, adjustments, or prior period corrections
- These affect the total amount validation calculation

**Usage Units:**
- Water/Sewer: CCF (hundred cubic feet) or gallons
- May need conversion for analysis

### Validation

SPU validation is more complex due to adjustments:

```python
balance + sum(current_service_amounts) + adjustments ≈ total_amount_due
```

---

## Puget Sound Energy

### Overview
Major utility providing electric and natural gas service across Washington state.

### Bill Variants

PSE has **three bill types**:
1. **Electric Only** (`pse_electric.txt`)
2. **Gas Only** (`pse_gas.txt`)
3. **Combined Gas and Electric** (`pse_gas_and_electric.txt`)

The system automatically detects which type based on services present on the bill.

### Special Considerations

**Dual Fuel Bills:**
- Combined bills have separate sections for electric and gas
- Each gets its own entry in `meter_level_data`
- Separate meter numbers and usage units

**Rate Components:**
- Electric charges split into: Generation, Transmission, Distribution
- Gas charges split into: Commodity, Transportation
- Each component is a separate line item

**Budget Billing:**
- Some customers on budget billing plans
- May show actual usage vs. budget amount
- Could have adjustments if usage diverges from budget

**Seasonal Rates:**
- Different rates for winter vs. summer
- Affects line item names and rates

### Usage Units

- Electric: kWh (kilowatt-hours)
- Gas: Therms

---

## Waste Management Companies

### Overview
Includes: Waste Management of Washington, Republic Services, Rubatino, Recology

### Common Characteristics

**Simple Bill Structure:**
- Typically flat-rate charges
- No meter readings
- Few line items (usually just service type and amount)

**Service Types:**
- Residential: Garbage, recycling, yard waste
- Commercial: Container sizes, pickup frequency

**Less Validation Needed:**
- No complex calculations
- No usage multipliers
- Straightforward totals

### Special Considerations

**Rubatino Detection:**
- Special check for "rubatino.onlineportal.us.com" in bill footer
- Without this, might be misidentified as another provider

---

## Water Districts

### Overview
Includes: Water District 20, Sammamish Plateau, Alderwood, various cities

### Common Characteristics

**Usage-Based Billing:**
- Meter readings for water consumption
- May include sewer based on water usage or flat rate
- Drainage or stormwater fees common

**Tiered Rates:**
- Many have conservation-based tier pricing
- Usage in tiers gets progressively more expensive

**Seasonal Variations:**
- Summer usage often higher (outdoor watering)
- Some have seasonal rate adjustments

### Special Considerations

**Service Address vs. Billing Address:**
- Often different for rental properties
- System extracts the service address (where water is used)

**Multiple Meters:**
- Commercial properties may have multiple water meters
- Each meter is a separate entry

---

## Common Issues

### Issue: Provider Misidentification

**Symptoms:** LLM returns wrong provider or "Unknown provider" error

**Common Causes:**
- Bill is a scanned image without text layer (needs OCR)
- Non-standard bill format or template
- Multiple providers on one document (e.g., consolidated bill)

**Solutions:**
- Ensure PDF has selectable text
- Check if provider is in supported list
- Review logs for what the LLM detected
- Add special detection logic if needed

### Issue: Validation Failures

**Symptoms:** Bill processed but moved to `unprocessed/` folder

**Common Causes:**
- Rounding differences in calculations
- Adjustments or credits not captured
- Multi-page bills with subtotals
- Missing or null values in critical fields

**Solutions:**
1. Check validation objects in JSON:
   ```json
   "line_item_charges_validation": {
       "is_match": false,
       "difference": 0.9
   }
   ```
2. Review if difference is significant or just rounding
3. Check if prompt needs adjustment for this provider
4. Verify all charges were extracted

### Issue: Null Values in Critical Fields

**Symptoms:** Important fields like `total_amount_due` are null

**Common Causes:**
- Field not present on this bill type
- Field in unusual location on bill
- LLM couldn't find or interpret the field

**Solutions:**
1. Verify field actually exists on the PDF
2. Check prompt instructions for that field
3. Review if field has unusual formatting
4. Consider if field is truly required or can be calculated

### Issue: Date Format Inconsistencies

**Symptoms:** Dates returned in various formats

**Why:** System intentionally preserves original date format from bill

**Handling in Code:**
```python
from dateutil.parser import parse

date_str = data['statement_level_data']['bill_date']
if date_str:
    date_obj = parse(date_str)  # Handles most formats
```

### Issue: Multiple Accounts on One Bill

**Symptoms:** Bill contains multiple account numbers or addresses

**Solutions:**
- Current system extracts primary account only
- For bills with truly multiple accounts, may need manual splitting
- Consider extracting to multiple JSON files if common

---

## Adding a New Provider

When adding a new provider, consider documenting:

1. **Bill Format Characteristics**
   - What makes this bill unique?
   - Any special formatting or terminology?

2. **Common Variations**
   - Does this provider have multiple bill formats?
   - Residential vs. commercial differences?

3. **Validation Rules**
   - How should totals be calculated?
   - What tolerance for rounding?

4. **Special Fields**
   - Any provider-specific fields needed?
   - Unusual data that needs capturing?

5. **Known Issues**
   - Any quirks or edge cases?
   - Common extraction errors?

---

## Testing New Providers

### Checklist

- [ ] Test with at least 3 different bills from the provider
- [ ] Verify provider detection works consistently
- [ ] Check all required fields are extracted
- [ ] Validate calculations match bill totals
- [ ] Test with different bill formats (if multiple exist)
- [ ] Verify handling of null/missing values
- [ ] Check meter reading calculations (if applicable)
- [ ] Test multi-page bills
- [ ] Verify date formats are preserved correctly
- [ ] Review validation pass rate

### Sample Test Script

```python
from pathlib import Path
from src.utility_bills.extractor import Extractor
import json

def test_provider(provider_name, pdf_paths):
    """Test extraction for a specific provider."""
    extractor = Extractor(project_root=Path.cwd())
    
    for pdf_path in pdf_paths:
        print(f"\nTesting: {pdf_path.name}")
        result = extractor.process_pdf(pdf_path)
        
        if result['success']:
            # Load and inspect JSON
            with open(result['json_path']) as f:
                data = json.load(f)
            
            # Check key fields
            stmt = data['statement_level_data']
            acct = data['account_level_data']
            
            print(f"  Provider: {acct['provider']}")
            print(f"  Account: {acct['account_number']}")
            print(f"  Total Due: ${stmt['total_amount_due']}")
            print(f"  Validation: {result['validation_passed']}")
            
            # Check validation details
            if not result['validation_passed']:
                total_val = stmt.get('total_amount_validation', {})
                print(f"  Difference: ${total_val.get('difference')}")
        else:
            print(f"  ERROR: {result['error']}")

# Usage
pdfs = [
    Path("tests/provider_bills/bill1.pdf"),
    Path("tests/provider_bills/bill2.pdf"),
    Path("tests/provider_bills/bill3.pdf"),
]
test_provider("provider name", pdfs)
```

---

**Last Updated**: January 2026  
**Maintainer**: Add your name/contact when you make significant updates
