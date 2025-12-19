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

KING_COUNTY_WATER_DISTRICT_SPECIFIC_INSTRUCTIONS = """

KING COUNTY WATER DISTRICT TWENTY SPECIFIC INSTRUCTIONS:

This template applies to bills with "King County Water District" or "KCWD" text.

SECTION 1 - PROVIDER INFORMATION:
- Provider Name: "King County Water District" (use exact district name printed)
- Extract provider website, customer service phone, email, provider address, and remit address.

SECTION 2 - ACCOUNT INFORMATION:
- Account number, account type (Water or Water & Sewer), bill number/type, customer name, service and billing addresses.

SECTION 3 - BILL DETAILS:
- Bill date, total amount due date, number of days, service days.

SECTION 4 - BILLING SUMMARY:
- previous_balance, current_billing, current_adjustments, total_amount_due, balance.

SECTION 5 - PAYMENT INFORMATION:
- payment_information (latest payment) and payments_applied array with all payments.

SECTION 6 - LATE FEE INFORMATION:
- Populate late_fee_info with late fee status, dates, amounts, percentage, projected totals.

SECTION 7 - METER INFORMATION (CRITICAL):
- KCWD bills list at least one water meter. For EACH meter capture:
  * meter_number, meter_location (if shown), service_type (Water), read_date, start/end dates,
  * previous/current readings, reading types, usage, uom (gallons, CCF, etc.), multiplier, read_type.
- Store each meter in the meters array.

SECTION 8 - SERVICE TYPES / CHARGES:
- For each service (Water Base, Consumption, Sewer, etc.) extract:
  * service_name, current_service amount, service_from/service_to dates.
  * `line_item_charges` entries with category, description, rate, amount, meter_number, usage, uom, readings (if supplied), and usage_multiplier.
- The sum of `current_service` values must equal current_billing.


SECTION 9 - TAXES (CRITICAL):
**CRITICAL**: King County Water District bills show taxes in a specific format that you MUST extract.

1) TAX FORMAT ON THE BILL:
The bill shows taxes in lines like:
- "City of Burien Utility Tax - 10%  0.00"

2) EXTRACTION RULES:
- For each tax line that shows a tax name, percentage, and amount:
  * Extract the tax name (e.g., "City of Burien Utility Tax")
  * Extract the tax rate/percentage (e.g., "10%")
  * Extract the tax amount (e.g., "0.00")
  * Put these in the `global_taxes` array (unless clearly tied to a specific service, then use `per_service_taxes`)

3) TAX EXAMPLES:
If the bill shows:
"City of Burien Utility Tax - 10%  0.00"

Extract as:
{
  "tax_name": "City of Burien Utility Tax",
  "tax_rate": "10%",
  "tax_amount": "0.00"
}

Place this in `taxes.global_taxes` array.

4) IMPORTANT:
- Extract ALL tax lines, even if the amount is 0.00
- If a line has a tax name and percentage but no amount shown, set tax_amount to null
- DO NOT include "Non-taxable Government Services" items in the taxes arrays - they go in a separate section (see SECTION 11)

SECTION 10 - ADJUSTMENTS:
- Capture every adjustment with category and signed amount (credits positive, debits negative).

SECTION 11 - NON-TAXABLE GOVERNMENT SERVICES (CRITICAL):
**CRITICAL**: King County Water District bills have a separate "Non-taxable Government Services" section that MUST be extracted separately from taxes and service charges.

1) SECTION FORMAT ON THE BILL:
The bill shows a section like:
- "Non-taxable Government Services:" (this is a header/group label)
  - "Streetlights 25.70"
  - "Fire Service Cost Allocation  69.6"

2) EXTRACTION RULES:
- Look for the header "Non-taxable Government Services:" or similar wording
- For EACH line item listed under this header:
  * Extract the service name/description (e.g., "Streetlights", "Fire Service Cost Allocation")
  * Extract the amount (e.g., "25.70", "69.6")
  * Create an entry in the `non_taxable_government_services` array

3) EXAMPLES:
If the bill shows:
"Non-taxable Government Services:
Streetlights 25.70
Fire Service Cost Allocation  69.6"

Extract as:
"non_taxable_government_services": [
  {
    "service_name": "Streetlights",
    "amount": "25.70"
  },
  {
    "service_name": "Fire Service Cost Allocation",
    "amount": "69.6"
  }
]

"""

KING_COUNTY_WATER_DISTRICT_JSON_FORMAT = """

{
  "provider_name": "King County Water District 20",
  "provider_website": "website_url_or_null",
  "provider_customer_service_phone": "phone_number_or_null",
  "provider_customer_service_email": "email_address_or_null",
  "provider_address": "complete_provider_address_or_null",
  "provider_return_address": "payment_return_address_or_null",
  "account_number": "numeric_digits_only_or_null",
  "account_type": "Water",
  "bill_number": "bill_or_statement_number_or_null",
  "bill_type": "bill_type_like_Regular_Final_Estimated_or_null",
  "customer_name": "customer_name_or_null",
  "service_address": "service_address_or_null",
  "billing_address": "billing_address_or_null",
  "bill_date": "date_format_like_March_03_2025_or_null",
  "total_amount_due_date": "date_format_like_March_03_2025_or_null",
  "number_of_days": "numeric_days_or_null",
  "service_days": "numeric_days_same_as_number_of_days_or_null",
  "previous_balance": "dollar_amount_or_null",
  "current_billing": "dollar_amount_or_null",
  "current_adjustments": "dollar_amount_or_null",
  "total_amount_due": "dollar_amount_or_null",
  "balance": "current_outstanding_balance_or_null",

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

  "late_fee_info": {
    "latefee_applied": "yes_or_no_or_null",
    "latefee_date": "date_when_late_fee_was_applied_or_null",
    "latefee_amount": "dollar_amount_of_late_fee_or_null",
    "latefee_by_duedate_percentage": "percentage_like_1%_or_1.5%_or_null",
    "latefee_by_duedate": "dollar_amount_of_late_fee_if_late_or_null",
    "total_amount_with_latefee_by_duedate": "total_including_late_fees_or_null"
  },

  "meters": [
    {
      "meter_number": "meter_identifier",
      "meter_location": "meter_location_description_or_null",
      "service_type": "Water",
      "read_date": "date_format_like_March_03_2025_or_null",
      "start_date": "billing_period_start_date_or_null",
      "service_from_date": "billing_period_start_date_or_null",
      "end_date": "billing_period_end_date_or_null",
      "service_to_date": "billing_period_end_date_or_null",
      "previous_reading": "reading_value_at_start_or_null",
      "previous_reading_type": "Actual_or_Estimated_or_Customer_or_null",
      "current_reading": "reading_value_at_end_or_null",
      "current_reading_type": "Actual_or_Estimated_or_Customer_or_null",
      "usage": "numeric_usage_value_or_null",
      "uom": "unit_like_CCF_gallons_or_null",
      "multiplier": "numeric_multiplier_like_1_or_null",
      "read_type": "Actual_or_Estimated_or_Customer_or_null",
      "total_current_electric_charges": null
    }
  ],

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
          "uom": "unit_like_CCF_or_gallons_or_null",
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
  }
}

    "non_taxable_government_services": [
        {
          "service_name": "service_name_like_Streetlights_or_Fire_Service_Cost_Allocation",
          "amount": "dollar_amount"
        }
      ]
    }

"""

KING_COUNTY_WATER_DISTRICT_PROMPT = f"""{BASE_EXTRACTION_FIELDS}

{KING_COUNTY_WATER_DISTRICT_SPECIFIC_INSTRUCTIONS}

{KING_COUNTY_WATER_DISTRICT_JSON_FORMAT}
"""
