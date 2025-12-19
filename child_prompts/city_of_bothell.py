BASE_EXTRACTION_FIELDS = """

Extract information from this utility bill and return ONLY valid JSON.

Find these fields:
1. ACCOUNT NUMBER - Look for "Account Number", "Account No", "Acct No" - extract digits only
2. CUSTOMER NAME - Find customer name, account holder, billing name, or property owner
3. SERVICE ADDRESS - Physical address where services are provided  
4. BILLING ADDRESS - Mailing address for billing (may be same as service address)
5. PREVIOUS BALANCE - Any previous balance carried forward from previous bill
6. CURRENT BILLING - Total dollar amount due for current period
7. CURRENT ADJUSTMENTS - **ONLY extract if there is an "Adjustments" section on the bill**
   - Look ONLY in sections explicitly labeled "Adjustments", "Account Adjustments", "Credits/Adjustments"
   - DO NOT extract adjustments from:
     * Payment sections
     * Balance calculations
     * Line item descriptions
   - If you find an "Adjustments" section, extract EACH adjustment with its category name and amount
   - If there is NO "Adjustments" section, leave adjustments array EMPTY and current_adjustments as null
   - Include both positive adjustments (credits) and negative adjustments (debits/fees)
8. DUE DATE - Payment due date (format like "March 03 2025")
9. BILL DATE - The date this bill was issued/generated
10. NUMBER OF DAYS - The number of days in this billing period (usually under "This Bill Period")
11. PAYMENT INFORMATION - Find ALL payments applied:
    - Look for "Payments Applied", "Payment Received", "Payment History"
    - Extract EACH payment separately with date and amount
    - Include all payments shown on the bill
12. TOTAL AMOUNT DUE - The final total amount due (look for "Total Amount Due", "Amount Due", "Balance Due", "Total Due")
    - This is typically: Previous Balance + Current Billing + Adjustments - Payments
13. TAXES - Find all tax information:
    - Per-service taxes (tied to specific services)
    - Global taxes (applied to entire bill)
14. SERVICES - Find each service (Water, Sewer, Garbage, etc.) with:
    - Current service charge amount
    - Line item charges with descriptions, amounts, meter numbers, CCF usage, readings
    - Service From Date and Service To Date

"""

# Standard JSON output format
BASE_JSON_FORMAT = """

Return in this exact JSON format:
{
  "provider_name": "provider_name_from_bill_or_null",
  "account_number": "numeric_digits_only_or_null",
  "account_type": "account_type_like_Water_Electric_Waste_Management_or_null",
  "customer_name": "customer_name_or_null",
  "service_address": "service_address_or_null",
  "billing_address": "billing_address_or_null",
  "previous_balance": "dollar_amount_or_null",
  "current_billing": "dollar_amount_or_null",
  "current_adjustments": "dollar_amount_or_null",
  "total_amount_due": "dollar_amount_or_null",
  "total_amount_due_date": "date_format_like_March_03_2025_or_null",
  "bill_date": "date_format_like_March_03_2025_or_null",
  "number_of_days": "numeric_days_or_null",
  "payment_information": {
    "payment_date": "date_format_like_March_03_2025_or_null",
    "payment_amount": "dollar_amount_or_null"
  },
  "payments_applied": [
    {
      "payment_date": "date_format_like_March_03_2025_or_null",
      "payment_amount": "dollar_amount"
    }
  ],
  "adjustments": [
    {
      "category": "adjustment_category_description",
      "amount": "dollar_amount_with_sign"
    }
  ],
  "taxes": {
    "per_service_taxes": [
      {
        "service_name": "service_name_as_shown_on_bill",
        "tax_name": "tax_type_name",
        "tax_rate": "percentage_or_null",
        "tax_amount": "dollar_amount"
      }
    ],
    "global_taxes": [
      {
        "tax_name": "tax_type_name",
        "tax_rate": "percentage_or_null",
        "tax_amount": "dollar_amount"
      }
    ]
  },
  "service_types": [
    {
      "service_name": "service_name_as_shown_on_bill",
      "current_service": "dollar_amount_or_null",
      "service_from_date": "date_format_like_March_03_2025_or_null",
      "service_to_date": "date_format_like_March_03_2025_or_null",
      "previous_reading": "reading_value_or_null",
      "current_reading": "reading_value_or_null",
      "line_item_charges": [
        {
          "category": "category_description_as_shown_on_bill",
          "description": "detailed_description_or_null",
          "rate": "rate_per_unit_or_null",
          "amount": "dollar_amount",
          "meter_number": "meter_id_or_null",
          "usage": "numeric_value_or_null",
          "uom": "unit_like_CCF_or_kWh_or_null",
          "previous_reading": "reading_value_or_null",
          "previous_reading_type": "Actual_or_Estimated_or_null",
          "current_reading": "reading_value_or_null",
          "current_reading_type": "Actual_or_Estimated_or_null",
          "usage_multiplier": "numeric_multiplier_value_or_null"
        }
      ]
    }
  ]
}

"""

CITY_OF_BOTHELL_SPECIFIC_INSTRUCTIONS = """

CITY OF BOTHELL SPECIFIC INSTRUCTIONS:

This template applies to bills with "City of Bothell" or "Bothell" text.

SECTION 1 - PROVIDER INFORMATION:
**CRITICAL**: Extract City of Bothell provider information
- Provider Name: "City of Bothell"
- Provider Website: Look for website URL (may appear in header, footer, or contact section)
  * Extract complete URL or domain as shown
- Provider Customer Service Phone: Look for customer service phone number
  * Common format: "(XXX) XXX-XXXX" or "XXX.XXX.XXXX"
  * Usually in header, footer, or contact section
  * Extract exactly as shown
- Provider Customer Service Email: Look for customer service email address
  * Extract complete email address if shown
- Provider Address: Look for the main business address
  * Typically in header or footer of the bill
  * Extract complete address including street, city, state, zip
- Provider Return Address: Look for payment return address or "Remit Payment To"
  * This is where customers mail their payments
  * May be a PO Box or different from main address
  * Extract complete address

SECTION 2 - ACCOUNT INFORMATION:
- Account Number: Look for "Account Number", "Account No", or similar label
  * Extract digits only
- Account Type: Typically "Water & Sewer" or "Water & Wastewater"
- Bill Number: Look for "Bill Number", "Statement Number", "Invoice Number"
  * Extract the complete bill identifier
- Bill Type: Identify the type of bill
  * Common types: "Regular", "Final", "Estimated", "Adjusted"
  * Look for indicators like "Final Bill", "Estimated Reading", etc.
- Customer Name: Look for customer name, account holder, billing name, or property owner
- Service Address: Physical address where services are provided
- Billing Address: Mailing address for billing (may be same as service address)

SECTION 3 - BILL DETAILS:
- Bill Date: The date this bill was issued/generated
  * Format like "March 03 2025" or "Mar 3 2025"
- Total Amount Due Date: Payment due date
  * Format like "March 03 2025" or "Mar 3 2025"
- Number of Days: The number of days in this billing period
  * Usually under "This Bill Period", "Billing Period", or "Days"
- Service Days: Same as number_of_days typically
  * Number of days in the service period

SECTION 4 - BILLING SUMMARY:
- Previous Balance: Any previous balance carried forward from previous bill
  * Look for "Previous Balance", "Balance Forward", "Carried Forward"
- Current Billing: Total dollar amount due for current period
  * Sum of all current service charges
- Current Adjustments: Any adjustment amount
  * Look for "Current Adjustments", "Adjustments", "Credits", or similar
  * Extract EACH adjustment separately with its category name and amount
  * Include both positive adjustments (credits) and negative adjustments (debits/fees)
- Total Amount Due: The final total amount due
  * Look for "Total Amount Due", "Amount Due", "Balance Due", "Total Due"
  * This is typically: Previous Balance + Current Billing + Adjustments - Payments
- Balance: Current outstanding balance on the account
  * May be different from Total Amount Due
  * Look for "Current Balance", "Account Balance"

SECTION 5 - PAYMENT INFORMATION:
**CRITICAL**: Extract ALL payment information
- Payment Information: Find payment date and amount
  * Look for most recent payment or payment confirmation
- Payments Applied: Find ALL payments applied
  * Look for "Payments Applied", "Payment Received", "Payment History"
  * Extract EACH payment separately with date and amount
  * Include all payments shown on the bill
  * Create one entry per payment in the payments_applied array

SECTION 6 - LATE FEE INFORMATION:
**CRITICAL**: Extract all late fee and penalty information
- Late Fee Applied: Check if a late fee has been applied to this bill
  * Look in charges, adjustments, or penalty sections
  * Extract as "yes" or "no" or null
  * Extract the date when late fee was applied
  * Extract the amount of the late fee applied
- Late Fee by Due Date Percentage: Look for late payment charge rate
  * Common format: "1%", "1.5%", "1 percent per month"
  * Look for terms like "late payment charge", "late fee", "penalty rate"
  * Usually in payment terms, fine print, or important notice section
- Late Fee by Due Date: Calculate or extract total late fees
  * This is the amount that will be charged if payment is late
  * May be shown as "Late fee if paid after [date]: $XX.XX"
- Total Amount with Late Fee by Due Date: The balance including late fees if paid after due date
  * Calculate: Current Balance + Late Fees

SECTION 7 - METER INFORMATION (CRITICAL):
**IMPORTANT**: Extract detailed meter data for each service
- For EACH meter on the bill, extract:
  1. Meter Number: The unique meter identifier
  2. Meter Location: Where the meter is located (if shown)
  3. Service Type: The service this meter measures (Water, Sewer, Wastewater, etc.)
  4. Read Date: When the meter was read
  5. Previous Reading: Meter reading at start of period
  6. Previous Reading Type: How previous reading was obtained ("Actual", "Estimated", "Customer")
  7. Current Reading: Meter reading at end of period
  8. Current Reading Type: How current reading was obtained ("Actual", "Estimated", "Customer")
  9. Usage: Consumption amount (numeric value only)
  10. Unit of Measurement (UOM): The unit (CCF, gallons, etc.)
  11. Multiplier: Any multiplier applied to calculate actual usage
     * Common values: "1", "10", "100", "0.1"
     * Actual usage = (Current Reading - Previous Reading) × Multiplier
     * Look for "Multiplier", "Mult", "Factor" labels near meter readings
  12. Read Type: How reading was obtained ("Actual", "Estimated", "Customer")

- Store meter information in a dedicated "meters" array
- DO NOT mix this with line_item_charges in service_types
- Each meter should have ALL fields even if some are null

SECTION 8 - SERVICE CHARGES (MOST CRITICAL):
**CRITICAL FOR CITY OF BOTHELL**: Extract EVERY row from the service charges table as a separate service_type entry

- Look for the service charges table with columns: SERVICE, METER NO., CURRENT READ DATE, PREVIOUS READ, CURRENT READ, USAGE, CURRENT CHARGES
- Extract EACH row from this table as a SEPARATE service_type entry, even if:
  * The row has no meter number
  * The row has no previous/current readings
  * The row is a tax (e.g., "WATER TAX MULTI-FAMILY (6%)")
  * The row is a per-unit charge (e.g., "PER UNIT CHARGE MULTI-FAMILY")

- For EACH row/service, extract:
  - Service Name: The service name EXACTLY as shown in the SERVICE column
    * Examples: "2\" WATER MULTI-FAMILY", "PER UNIT CHARGE MULTI-FAMILY", "SEWER MULTI-FAMILY", "WATER TAX MULTI-FAMILY (6%)", "SEWER TAX MULTI-FAMILY (6%)"
  - Current Service: The dollar amount from CURRENT CHARGES column
    * This is the amount for THIS specific service/tax entry
  - Service From Date: Service period start date (if shown)
  - Service To Date: Service period end date (if shown)
  - Previous Reading: Meter reading from PREVIOUS READ column (if present, otherwise null)
  - Current Reading: Meter reading from CURRENT READ column (if present, otherwise null)
  - Line Item Charges: Create ONE line item entry with:
    * Category: Same as service_name (the service name from SERVICE column)
    * Description: null (unless additional description is provided)
    * Rate: null (unless rate is explicitly shown)
    * Amount: Same as current_service (the amount from CURRENT CHARGES column)
    * Meter Number: Meter number from METER NO. column (if present, otherwise null)
    * Usage: Usage value from USAGE column (if present, otherwise null)
    * UOM: Unit of measurement (if usage is present, typically "CCF" or similar)
    * Previous Reading: Same as service-level previous_reading
    * Previous Reading Type: "Actual", "Estimated", or "Customer" (if reading present)
    * Current Reading: Same as service-level current_reading
    * Current Reading Type: "Actual", "Estimated", or "Customer" (if reading present)
    * Usage Multiplier: Multiplier if shown (otherwise null)

- **IMPORTANT**: 
  * DO NOT group services together - each row in the table is a separate service_type entry
  * Taxes (like "WATER TAX MULTI-FAMILY (6%)") should be extracted as service_type entries, NOT in the taxes section
  * The sum of ALL current_service amounts (including taxes) must equal current_billing
  * If a row has no meter number, readings, or usage, still extract it as a service_type entry with null values for those fields

SECTION 9 - TAXES:
**IMPORTANT FOR CITY OF BOTHELL**: Taxes are extracted as service_type entries (see Section 8 above)
- Do NOT extract taxes in a separate taxes section
- All tax rows from the service charges table should be in service_types array
- The taxes object should have empty arrays: {"per_service_taxes": [], "global_taxes": []}

SECTION 10 - ADJUSTMENTS:
- Extract ALL adjustments separately with their category names and amounts
- Look for "Adjustments", "Account Adjustments", "Credits/Adjustments" sections
- Include both positive adjustments (credits) and negative adjustments (debits/fees)
- Use positive amounts for credits (e.g., "$50.00" for a credit)
- Use negative amounts for debits/fees (e.g., "-$10.00" for a late fee)


"""

CITY_OF_BOTHELL_JSON_FORMAT = """

Return in this exact JSON format. ALL FIELDS MUST BE INCLUDED for City of Bothell bills:

For City of Bothell, extract EVERY row from the service charges table as a separate service_type entry, including taxes. Taxes should NOT be in the taxes section.

{
  "provider_name": "City of Bothell",
  // ... other fields ...
  
  "service_types": [
    {
      "service_name": "2\" WATER MULTI-FAMILY",
      "current_service": "$1,488.98",
      "service_from_date": "date_or_null",
      "service_to_date": "date_or_null",
      "previous_reading": "8699",
      "current_reading": "8886",
      "line_item_charges": [
        {
          "category": "2\" WATER MULTI-FAMILY",
          "description": null,
          "rate": null,
          "amount": "$1,488.98",
          "meter_number": "45665188",
          "usage": "187",
          "uom": "CCF",
          "previous_reading": "8699",
          "previous_reading_type": "Actual",
          "current_reading": "8886",
          "current_reading_type": "Actual",
          "usage_multiplier": "1"
        }
      ]
    },
    {
      "service_name": "PER UNIT CHARGE MULTI-FAMILY",
      "current_service": "$238.26",
      "service_from_date": null,
      "service_to_date": null,
      "previous_reading": null,
      "current_reading": null,
      "line_item_charges": [
        {
          "category": "PER UNIT CHARGE MULTI-FAMILY",
          "description": null,
          "rate": null,
          "amount": "$238.26",
          "meter_number": null,
          "usage": "38",
          "uom": null,
          "previous_reading": null,
          "previous_reading_type": null,
          "current_reading": null,
          "current_reading_type": null,
          "usage_multiplier": null
        }
      ]
    },
    {
      "service_name": "SEWER MULTI-FAMILY",
      "current_service": "$2,459.66",
      "service_from_date": null,
      "service_to_date": null,
      "previous_reading": null,
      "current_reading": null,
      "line_item_charges": [
        {
          "category": "SEWER MULTI-FAMILY",
          "description": null,
          "rate": null,
          "amount": "$2,459.66",
          "meter_number": "45665188",
          "usage": null,
          "uom": null,
          "previous_reading": null,
          "previous_reading_type": null,
          "current_reading": null,
          "current_reading_type": null,
          "usage_multiplier": null
        }
      ]
    },
    {
      "service_name": "WATER TAX MULTI-FAMILY (6%)",
      "current_service": "$103.63",
      "service_from_date": null,
      "service_to_date": null,
      "previous_reading": null,
      "current_reading": null,
      "line_item_charges": [
        {
          "category": "WATER TAX MULTI-FAMILY (6%)",
          "description": null,
          "rate": "6%",
          "amount": "$103.63",
          "meter_number": null,
          "usage": null,
          "uom": null,
          "previous_reading": null,
          "previous_reading_type": null,
          "current_reading": null,
          "current_reading_type": null,
          "usage_multiplier": null
        }
      ]
    },
    {
      "service_name": "SEWER TAX MULTI-FAMILY (6%)",
      "current_service": "$147.58",
      "service_from_date": null,
      "service_to_date": null,
      "previous_reading": null,
      "current_reading": null,
      "line_item_charges": [
        {
          "category": "SEWER TAX MULTI-FAMILY (6%)",
          "description": null,
          "rate": "6%",
          "amount": "$147.58",
          "meter_number": null,
          "usage": null,
          "uom": null,
          "previous_reading": null,
          "previous_reading_type": null,
          "current_reading": null,
          "current_reading_type": null,
          "usage_multiplier": null
        }
      ]
    }
  ],
  
  "taxes": {
    "per_service_taxes": [],
    "global_taxes": []
  }
}

"""

CITY_OF_BOTHELL_PROMPT = f"""{BASE_EXTRACTION_FIELDS}

{CITY_OF_BOTHELL_SPECIFIC_INSTRUCTIONS}

{CITY_OF_BOTHELL_JSON_FORMAT}
"""
