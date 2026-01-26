# Data Structure Reference

This document describes the JSON output structure for extracted utility bill data.

## Overview

All extracted utility bill data follows a consistent three-level hierarchical structure, regardless of the provider. This standardization makes it easy to process bills from different utilities using the same code.

## Top-Level Structure

```json
{
    "statement_level_data": { ... },
    "account_level_data": { ... },
    "meter_level_data": [ ... ]
}
```

## Statement Level Data

Financial and billing period information.

### Fields

| Field | Type | Description | Example |
|-------|------|-------------|---------|
| `bill_date` | string | Date the bill was issued | "December 30, 2025" |
| `previous_balance` | float | Balance from previous billing period | 2313.23 |
| `payments_applied` | float | Payments made during period (negative if credit) | -2313.23 |
| `payment_date` | string | Date of last payment | "December 18, 2025" |
| `late_fee_applied` | float | Late fee charged this period | null |
| `late_fee_date` | string | Date late fee was applied | null |
| `balance` | float | Current balance before new charges | 0.0 |
| `current_billing` | float | New charges for this period | 3094.65 |
| `total_amount_due` | float | Total amount owed | 3094.65 |
| `total_amount_due_date` | string | Payment due date | "January 20, 2026" |
| `late_fee_by_duedate_percentage` | float | Late fee percentage rate | 1.0 |
| `late_fee_by_duedate` | string | Late fee policy text | "A late payment charge..." |
| `payment_amount` | float | Amount to be paid (e.g., autopay) | 3094.65 |
| `total_amount_validation` | object | Validation calculations | See below |

### Total Amount Validation Object

```json
{
    "balance": 0.0,
    "sum_current_service_amounts": 3094.65,
    "calculated_total": 3094.65,
    "total_amount_due": 3094.65,
    "difference": 0.0,
    "is_match": true
}
```

- `is_match`: `true` if calculated total matches bill total (within tolerance)
- `difference`: Discrepancy between calculated and stated total
- Used to verify bill calculations are correct

## Account Level Data

Customer and provider information.

### Fields

| Field | Type | Description | Example |
|-------|------|-------------|---------|
| `provider` | string | Utility company name | "CITY OF SEATTLE" |
| `provider_website` | string | Provider's website URL | "myutilities.seattle.gov" |
| `provider_customer_service_phone` | string | Customer service phone number(s) | "206-684-3000 or 1-800-862-1181" |
| `provider_customer_service_email` | string | Customer service email | null |
| `provider_address` | string | Provider's mailing address | "P.O. Box 35178, Seattle, WA..." |
| `account_number` | string | Customer's account number | "4606830970" |
| `account_type` | string | Type of service | "Electric" |
| `customer_name` | string | Name on account | "BLANTON TURNER" |
| `service_address` | string | Service location address | "308 OCCIDENTAL AVE S SUITE 500..." |
| `service_days` | int | Number of days in billing period | 34 |

## Meter Level Data

Detailed usage and charges for each meter or service point. This is an array that can contain multiple entries for different meters or service addresses.

### Structure

```json
"meter_level_data": [
    {
        "service_name": "Electric Service",
        "current_service_amount": 46.0,
        "line_item_charges": [ ... ],
        "line_item_charges_validation": { ... }
    },
    // ... more meters ...
]
```

### Fields

| Field | Type | Description |
|-------|------|-------------|
| `service_name` | string | Type of service (e.g., "Electric Service", "Water Service") |
| `current_service_amount` | float | Total charges for this meter/service |
| `line_item_charges` | array | Individual charge items (see below) |
| `line_item_charges_validation` | object | Validation for this meter's charges |

### Line Item Charge Object

Each line item represents an individual charge within a meter/service.

```json
{
    "line_item_charge_name": "Base Service Charge",
    "line_item_charge_amount": 21.76,
    "rate": null,
    "service_from_date": "Nov 26, 2025",
    "service_through_date": "Dec 30, 2025",
    "usage": 195.32,
    "usage_unit_of_measurement": "kWh",
    "previous_reading": 711.23,
    "current_reading": 716.12,
    "multiplier": 40.0,
    "meter_number": "2208428",
    "service_category": "KWH"
}
```

#### Line Item Fields

| Field | Type | Description |
|-------|------|-------------|
| `line_item_charge_name` | string | Description of the charge |
| `line_item_charge_amount` | float | Dollar amount of the charge |
| `rate` | string | Unit rate (e.g., "$0.1375 per KWH") |
| `service_from_date` | string | Start date of service period |
| `service_through_date` | string | End date of service period |
| `usage` | float | Amount of resource used |
| `usage_unit_of_measurement` | string | Unit of measurement (kWh, CCF, etc.) |
| `previous_reading` | float | Meter reading at period start |
| `current_reading` | float | Meter reading at period end |
| `multiplier` | float | Multiplier applied to readings |
| `meter_number` | string | Physical meter identifier |
| `service_category` | string | Category of service (KWH, KVRH, etc.) |

### Line Item Charges Validation Object

```json
{
    "sum_line_item_charges": 46.9,
    "current_service_amount": 46.0,
    "difference": 0.9,
    "is_match": false
}
```

- Verifies that individual charges sum to the stated service total
- `is_match`: `true` if sum matches (within tolerance)
- `difference`: Discrepancy between sum and stated total

## Provider-Specific Variations

While the structure is consistent, some fields may be more relevant for certain providers:

### Electric Bills (e.g., Seattle City Light, PSE Electric)
- Heavy use of `meter_level_data`
- Multiple `service_category` values (KWH, KW, KVRH)
- `multiplier` field is important
- May include "Power Factor Penalty" charges

### Water Bills (e.g., SPU, City utilities)
- Usage typically in CCF (hundred cubic feet) or gallons
- May have separate water and sewer charges
- Tier-based pricing common (different rates for usage levels)

### Gas Bills (e.g., PSE Gas)
- Usage typically in therms
- Seasonal rate variations
- Transportation and commodity charges separated

### Waste Management Bills (e.g., WM, Republic Services)
- Typically simple flat-rate charges
- Service type variations (residential, commercial)
- Less complex meter reading data

## Null Value Handling

Fields that are not present on a bill or cannot be determined are set to `null`. This is important for data processing:

```json
{
    "late_fee_applied": null,        // No late fee on this bill
    "provider_email": null,          // Email not listed on bill
    "rate": null,                    // Fixed charge, no per-unit rate
    "multiplier": null               // Simple meter, no multiplier
}
```

When processing the data, always check for null values before performing calculations or string operations.

## Example: Complete Bill

Here's a simplified complete example for a Seattle City Light commercial bill:

```json
{
    "statement_level_data": {
        "bill_date": "December 30, 2025",
        "previous_balance": 2313.23,
        "payments_applied": -2313.23,
        "payment_date": "December 18, 2025",
        "balance": 0.0,
        "current_billing": 3094.65,
        "total_amount_due": 3094.65,
        "total_amount_due_date": "January 20, 2026",
        "late_fee_by_duedate_percentage": 1.0,
        "total_amount_validation": {
            "calculated_total": 3094.65,
            "total_amount_due": 3094.65,
            "difference": 0.0,
            "is_match": true
        }
    },
    "account_level_data": {
        "provider": "CITY OF SEATTLE",
        "provider_website": "myutilities.seattle.gov",
        "provider_customer_service_phone": "206-684-3000 or 1-800-862-1181",
        "account_number": "4606830970",
        "account_type": "Electric",
        "customer_name": "BLANTON TURNER",
        "service_address": "308 OCCIDENTAL AVE S SUITE 500 SEATTLE WA 98104"
    },
    "meter_level_data": [
        {
            "service_name": "Electric Service",
            "current_service_amount": 46.0,
            "line_item_charges": [
                {
                    "line_item_charge_name": "Base Service Charge",
                    "line_item_charge_amount": 21.76,
                    "rate": null,
                    "usage": 195.32,
                    "usage_unit_of_measurement": "kWh",
                    "meter_number": "2208428",
                    "service_category": "KWH"
                },
                {
                    "line_item_charge_name": "Small General Energy",
                    "line_item_charge_amount": 24.24,
                    "rate": "0.1241",
                    "usage": 195.32,
                    "usage_unit_of_measurement": "kWh",
                    "meter_number": "2208428",
                    "service_category": "KWH"
                }
            ],
            "line_item_charges_validation": {
                "sum_line_item_charges": 46.0,
                "current_service_amount": 46.0,
                "difference": 0.0,
                "is_match": true
            }
        }
    ]
}
```

## Working with the Data

### Python Example

```python
import json

# Load extracted data
with open('path/to/extracted_bill.json') as f:
    bill = json.load(f)

# Access statement data
total_due = bill['statement_level_data']['total_amount_due']
due_date = bill['statement_level_data']['total_amount_due_date']
print(f"Amount due: ${total_due} by {due_date}")

# Check validation
validation = bill['statement_level_data']['total_amount_validation']
if not validation['is_match']:
    print(f"Warning: Bill total discrepancy of ${validation['difference']}")

# Iterate through meters
for meter in bill['meter_level_data']:
    print(f"Service: {meter['service_name']}")
    print(f"Total: ${meter['current_service_amount']}")
    
    # Iterate through charges
    for charge in meter['line_item_charges']:
        name = charge['line_item_charge_name']
        amount = charge['line_item_charge_amount']
        usage = charge['usage']
        unit = charge['usage_unit_of_measurement']
        
        if usage and unit:
            print(f"  - {name}: ${amount} ({usage} {unit})")
        else:
            print(f"  - {name}: ${amount}")
```

### SQL Example

If loading into a database, you might create tables like:

```sql
CREATE TABLE statements (
    id INTEGER PRIMARY KEY,
    bill_date TEXT,
    previous_balance REAL,
    payments_applied REAL,
    balance REAL,
    current_billing REAL,
    total_amount_due REAL,
    total_amount_due_date TEXT
);

CREATE TABLE accounts (
    id INTEGER PRIMARY KEY,
    statement_id INTEGER,
    provider TEXT,
    account_number TEXT,
    customer_name TEXT,
    service_address TEXT,
    FOREIGN KEY (statement_id) REFERENCES statements(id)
);

CREATE TABLE line_items (
    id INTEGER PRIMARY KEY,
    statement_id INTEGER,
    meter_service_name TEXT,
    charge_name TEXT,
    charge_amount REAL,
    usage REAL,
    usage_unit TEXT,
    meter_number TEXT,
    FOREIGN KEY (statement_id) REFERENCES statements(id)
);
```

## Notes

- All monetary values are in USD
- Dates are stored as strings in their original format from the bill
- Validation objects are always present but may have null values if validation couldn't be performed
- The structure is designed to be forward-compatible: new fields can be added without breaking existing code

---

**Last Updated**: January 2026
