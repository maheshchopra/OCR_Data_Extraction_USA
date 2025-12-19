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

SEATTLE_CITY_LIGHT_SPECIFIC_INSTRUCTIONS = """

SEATTLE CITY LIGHT SPECIFIC INSTRUCTIONS:

This template applies to bills with "Seattle City Light" or "City Light" text.

SECTION 1 - CONTACT INFORMATION:
**CRITICAL**: Extract Seattle City Light contact information
- Website: Look for the City Light website
  * Common format: "seattle.gov/light" or "www.seattle.gov/city-light"
  * May appear with or without "https://" or "www."
  * Extract complete URL or domain
- Phone Number: Look for customer service phone number
  * Common format: "(206) 684-3000" or "206-684-3000"
  * Usually in header, footer, or contact section
  * Extract exactly as shown

SECTION 2 - LATE PAYMENT CHARGE:
**CRITICAL**: Look for late payment charge or penalty information
- Percentage: Extract the late payment charge rate
  * Common format: "1%", "1.5%", "1 percent per month"
  * Look for terms like "late payment charge", "late fee", "penalty", "interest"
  * Usually in payment terms or notice section
- Description: Extract complete late payment policy text
  * Example: "A 1% late payment charge will be applied to past due amounts"

SECTION 3 - ACCOUNT INFORMATION:
- Account Number: Unique account identifier
- Customer Name: Account holder name
- Service Address: Physical location where electric service is provided
- Billing Address: Mailing address for billing

SECTION 4 - BILL DETAILS:
- Bill Date: Date the bill was issued
- Due Date: Payment due date
- Previous Balance: Balance from previous bill
- Current Billing: Current period charges
- Total Amount Due: Final amount due
- Number of Days: Billing period length

SECTION 5 - METER INFORMATION AND CHARGES:
- Seattle City Light bills may have multiple meters
- Each meter has its own charges and readings
- Extract meter number, readings, and usage for each meter
- Group charges by meter if applicable

SECTION 6 - SERVICE CHARGES:
- Extract all electric service charges
- Common charges:
  * Base Service Charge
  * Energy charges (kWh based)
  * Demand charges
  * Power Factor penalties
  * Other fees
- Each charge may be associated with a specific meter
- Include meter readings and usage data where applicable

SECTION 7 - DETAILED BILLING INFORMATION (MOST CRITICAL):

You MUST treat each "DETAILED BILLING INFORMATION" section as a structured table and extract it ROW BY ROW.

1) TABLE STRUCTURE
Each table has column headers similar to:
- "Meter Number"
- "Service Category"
- "Service From"
- "Service Through"
- "Previous Reading"
- "Current Reading"
- "Multiplier"
- "Consumption/Units"
- "Power Factor"
- "Rate Code"
- "Unit Charge"
- "Amount"

The exact wording may vary slightly, but the columns are always in this general order.

2) ROW-BY-ROW EXTRACTION
For EVERY row in EVERY "DETAILED BILLING INFORMATION" table:
- Create one entry in the `detailed_billing_rows` array.
- Copy each column into the corresponding JSON field for that row.
- If a cell is visually blank on the bill, set the JSON field to null for that row (do NOT invent values).

Example numeric row from the bill:

Meter Number | Service Category | Service From   | Service Through | Previous Reading | Current Reading | Multiplier | Consumption/Units | Power Factor | Rate Code | Unit Charge | Amount
2207880      | KWH              | Jul 03, 2025   | Sep 03, 2025    | 875.55          | 976.18          | 20         | 2012.62           | (blank)     | (blank)   | (blank)     | (blank)

Must become:

{
  "meter_number": "2207880",
  "service_category": "KWH",
  "service_from_date": "July 03, 2025",
  "service_through_date": "September 03, 2025",
  "previous_reading": "875.55",
  "current_reading": "976.18",
  "multiplier": "20",
  "consumption_units": "2012.62",
  "power_factor": null,
  "rate_code": null,
  "unit_charge": null,
  "amount": null
}

Now consider a DESCRIPTION + AMOUNT row directly beneath those numeric rows, like in your bill image:

Meter Number | Service Category | Service From | Service Through       | Previous Reading | Current Reading | Multiplier | Consumption/Units | Power Factor | Rate Code | Unit Charge | Amount
(blank)      | (blank)          | (blank)      | Base Service Charge   | (blank)         | (blank)         | (blank)    | (blank)          | (blank)     | ESMCM     | (blank)     | 39.68

You MUST still create a row for this, with all the blanks preserved:

{
  "meter_number": null,
  "service_category": null,
  "service_from_date": null,
  "service_through_date": "Base Service Charge",
  "previous_reading": null,
  "current_reading": null,
  "multiplier": null,
  "consumption_units": null,
  "power_factor": null,
  "rate_code": "ESMCM",
  "unit_charge": null,
  "amount": "39.68"
}

Similarly, a "Small General Energy" row with only an amount:

Meter Number | Service Category | Service From | Service Through       | Previous Reading | Current Reading | Multiplier | Consumption/Units | Power Factor | Rate Code | Unit Charge | Amount
(blank)      | (blank)          | (blank)      | Small General Energy  | (blank)         | (blank)         | (blank)    | (blank)          | (blank)     | ESMCM     | 0.1241      | 249.77

Must become:

{
  "meter_number": null,
  "service_category": null,
  "service_from_date": null,
  "service_through_date": "Small General Energy",
  "previous_reading": null,
  "current_reading": null,
  "multiplier": null,
  "consumption_units": null,
  "power_factor": null,
  "rate_code": "ESMCM",
  "unit_charge": "0.1241",
  "amount": "249.77"
}

Use the visible context in the table:
- If a cell is visibly blank and there is NO value shown in that cell for this row, keep it null.
- Do NOT move the amount or description up into a numeric row.
- If the meter number is visually blank, you MAY copy down the most recent non-blank meter number above in the same block, but leave all other unreadable cells as null.

3) BUILDING LINE ITEM CHARGES FROM THE TABLE
After you build `detailed_billing_rows`, use those rows to populate `service_types[0].line_item_charges`:

**CRITICAL RULE**: ONLY create `line_item_charges` entries for rows where the Amount column has a value (is NOT null, NOT blank, NOT empty).

- For every row where `amount` is NOT null AND NOT empty:
  - Treat that row as a BILLING LINE ITEM, even if most other columns are blank.
  - Determine the category/description:
    * If `service_through_date` contains text like "Base Service Charge", "Small General Energy", "Power Factor Penalty", use that text as the `category`.
    * If `service_through_date` looks like a date and the description appears in another column, use that other column.
  - `meter_number`: use this row's `meter_number` if present; otherwise, use the most recent non-null `meter_number` from a numeric row above in the same table block.
  - `usage`: use the most relevant `consumption_units` from a numeric row above with the same meter (e.g., KWH usage for energy charges, KVRH usage for power factor charges). Do NOT modify `detailed_billing_rows` when you do this; just set the `usage` field in `line_item_charges`.
  - `uom`: "kWh" for energy rows, "kW" for demand rows, or null if not clear.
  - `previous_reading`, `current_reading`, `usage_multiplier`: similarly, take them from the most relevant numeric row above with the same meter and service category, if available.
  - `rate`: build from this row's `rate_code` and `unit_charge` when they are present (e.g., "ESMCM 0.1241"), otherwise null.
  - `amount`: copy directly from this row's `amount`.

**DO NOT** create `line_item_charges` entries for:
- Rows where the Amount column is blank, empty, or null
- Rows that only have consumption/usage data but no amount
- Rows that only have meter readings but no amount
- Example: If "Power Factor Penalty" row has NO value in the Amount column, do NOT create a line_item_charges entry for it

IMPORTANT:
- Do NOT attach an amount to numeric rows that have blank Amount cells in the PDF.
- Every physical row that shows a number in the Amount column must appear as a separate object in `detailed_billing_rows` with that `amount` value.
- Every such row (with a non-null amount) must also produce a corresponding `line_item_charges` entry.
- Rows with blank/empty Amount columns should still appear in `detailed_billing_rows` (with amount: null), but should NOT appear in `line_item_charges`.


4) RELATIONSHIP TO consumption_units AND amounts ARRAYS
- `consumption_units` array MUST be the list of all non-null `consumption_units` values from ALL `detailed_billing_rows`, in the exact order they appear in the tables.
- `amounts` array MUST be the list of all non-null `amount` values from ALL `detailed_billing_rows`, in the exact order they appear in the tables.

"""

SEATTLE_CITY_LIGHT_JSON_FORMAT = """

Return in this exact JSON format for Seattle City Light bills:
{
  "provider_name": "Seattle City Light",
  "provider_website": "website_url_or_null",
  "provider_customer_service_phone": "phone_number_or_null",
  "provider_customer_service_email": "email_address_or_null",
  "provider_address": "provider_physical_address_or_null",
  "provider_return_address": "provider_return_address_or_null",
  "account_number": "numeric_account_number",
  "account_type": "Electric",
  "bill_number": "bill_or_statement_number_or_null",
  "bill_type": "bill_type_like_Regular_Final_Estimated_or_null",
  "customer_name": "customer_name_as_shown",
  "service_address": "customer_physical_service_address",
  "billing_address": "customer_mailing_billing_address",
  "bill_date": "date_format_like_September_12_2025",
  "total_amount_due_date": "date_format_like_October_03_2025",
  "number_of_days": "numeric_days_in_billing_period",
  "service_days": "numeric_days_same_as_number_of_days_or_null",
  "previous_balance": "dollar_amount_or_null",
  "current_billing": "dollar_amount_for_current_period",
  "total_amount_due": "final_dollar_amount_due",
  "balance": "current_outstanding_balance_or_null",
  
  "payments_applied": [
    {
      "payment_date": "date_format_like_July_29_2025",
      "payment_amount": "dollar_amount"
    }
  ],
  
  "contact_info": {
    "website": "website_like_seattle.gov/light",
    "phone_number": "phone_like_(206)_684-3000"
  },
  
  "late_payment_charge": {
    "percentage": "percentage_like_1%_or_null",
    "description": "late_payment_policy_description_or_null"
  },

  "late_fee_info": {
    "latefee_applied": "yes_or_no_or_null",
    "latefee_date": "date_when_late_fee_was_applied_or_null",
    "latefee_amount": "dollar_amount_of_late_fee_or_null",
    "latefee_by_duedate_percentage": "percentage_like_1%_or_null",
    "latefee_by_duedate": "dollar_amount_of_late_fee_if_late_or_null",
    "total_amount_with_latefee_by_duedate": "total_including_late_fees_or_null"
  },

  "consumption_units": [
    "numeric_value_from_consumption_column",
    "numeric_value_from_consumption_column"
  ],

  "amounts": [
    "dollar_amount_from_amount_column",
    "dollar_amount_from_amount_column"
  ],

  "detailed_billing_rows": [
    {
      "meter_number": "meter_number_from_table_or_null",
      "service_category": "service_category_from_table_or_null",
      "service_from_date": "service_from_date_from_table_or_null",
      "service_through_date": "service_through_date_from_table_or_null",
      "previous_reading": "previous_reading_from_table_or_null",
      "current_reading": "current_reading_from_table_or_null",
      "multiplier": "multiplier_from_table_or_null",
      "consumption_units": "consumption_units_value_or_null",
      "power_factor": "power_factor_value_or_null",
      "rate_code": "rate_code_value_or_null",
      "unit_charge": "unit_charge_value_or_null",
      "amount": "amount_value_or_null"
    }
  ],
  
  "service_types": [
    {
      "service_name": "service_name_like_Electric_Service",
      "current_service": "total_dollar_amount_for_all_charges",
      "service_from_date": "date_format_like_July_03_2025",
      "service_to_date": "date_format_like_September_03_2025",
      "line_item_charges": [
        {
          "category": "charge_description_like_Base_Service_Charge",
          "description": "detailed_charge_description_or_null",
          "amount": "dollar_amount",
          "rate": "rate_per_unit_or_null",
          "meter_number": "meter_id_or_null",
          "usage": "numeric_value_or_null",
          "uom": "kWh",
          "previous_reading": "reading_value_or_null",
          "previous_reading_type": "Actual_or_Estimated_or_null",
          "current_reading": "reading_value_or_null",
          "current_reading_type": "Actual_or_Estimated_or_null",
          "usage_multiplier": "numeric_multiplier_like_1_or_null"
        }
      ]
    }
  ],
  
  "taxes": {
    "per_service_taxes": [],
    "global_taxes": []
  }
}

CRITICAL INSTRUCTIONS:
- Extract contact info: website (seattle.gov/light) and phone number
- Extract late payment charge percentage and description
- **MOST IMPORTANT**: Extract the "DETAILED BILLING INFORMATION" tables into `detailed_billing_rows` row by row.
  * Every physical row in every detailed billing table must appear as one object in `detailed_billing_rows`.
  * Use column headers to map each cell into the correct field.
  * If a cell is blank, set that field to null unless the value is clearly carried down from above.
- From `detailed_billing_rows`, build:
  * `consumption_units`: all non-null `consumption_units` values in table order.
  * `amounts`: all non-null `amount` values in table order.
  * `service_types[0].line_item_charges`: **ONLY** create entries for rows where `amount` is NOT null and NOT empty. If the Amount column is blank/empty for a row, do NOT create a line_item_charges entry for that row, even if it has a description like "Power Factor Penalty".
- Include ALL base fields (account_number, customer_name, etc.)
- Extract all service charges with meter details (supplementary)
- If late payment info not found, use null values
- Sum of all amounts should equal current_billing

"""

SEATTLE_CITY_LIGHT_PROMPT = f"""{BASE_EXTRACTION_FIELDS}

{SEATTLE_CITY_LIGHT_SPECIFIC_INSTRUCTIONS}

{SEATTLE_CITY_LIGHT_JSON_FORMAT}
"""
