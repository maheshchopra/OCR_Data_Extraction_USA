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

SAMMAMISH_PLATEAU_WATER_SPECIFIC_INSTRUCTIONS = """

SAMMAMISH PLATEAU WATER SPECIFIC INSTRUCTIONS:

This template applies to bills with "Sammamish Plateau Water" or "SPW" text.

SECTION 1 - CONTACT INFORMATION:
**CRITICAL**: Extract Sammamish Plateau Water contact information
- Phone Number: Look for phone number in format like "425.392.6256" or "(425) 392-6256"
  * Common location: header, footer, or contact section
  * Extract exactly as shown
- Email: Look for billing email address
  * Example: "billing@spwater.org"
  * Extract complete email address

SECTION 2 - ACCOUNT INFORMATION:
- Account Number: Unique account identifier
- Customer Name: Account holder name
- Service Address: Physical location where water services are provided
- Billing Address: Mailing address for billing

SECTION 3 - BILL DETAILS:
- Bill Date: Date the bill was issued
- Due Date: Payment due date
- Previous Balance: Balance from previous bill
- Current Billing: Current period charges
- Total Amount Due: Final amount due
- Number of Days: Billing period length

SECTION 4 - METER INFORMATION (MOST CRITICAL):
**IMPORTANT**: Extract meter data into a SEPARATE dedicated section
- DO NOT mix meter data with service line items
- Create a dedicated meter object with these fields:

  1. Meter Number: The unique meter identifier (e.g., "68566030")
  2. Read Dates: The date range for meter readings
     * Start date and end date of reading period
  3. Billing Days: Number of days in the billing period
  4. Meter Readings:
     * Previous Reading: Meter value at start (e.g., "0820413")
     * Present Reading: Meter value at end (e.g., "0828725")
  5. Usage:
     * Cubic Feet: Usage in cubic feet (CF)
     * Gallons: Usage in gallons (calculated or shown)

**IMPORTANT**: This meter information should be SEPARATE from service_types line items

SECTION 5 - SERVICE CHARGES (DETAILED):
- Extract all service line items with COMPLETE details for each charge
- Each line item must include ALL of these fields:
  1. Category: The service/charge description (e.g., "WATER BLOCK 1")
  2. Rate/CF: The rate per cubic foot (e.g., "$0.0283/CF", "$2.83/100 CF")
  3. Cubic Feet: The cubic feet usage for this specific charge
  4. Gallons: The gallon usage for this specific charge (may be calculated)
  5. Charge: The dollar amount for this line item

- Common charge categories:
  * Water Block charges (with tiered rates)
  * Multi-Family Water Per Unit
  * Multi-Family Sewer Per Unit
  * Other fees and charges

- **IMPORTANT**: Extract rate, usage (CF and gallons), and charge for EACH line item
- DO NOT include meter_number in line_item_charges (meter info is separate)
- If rate or usage not applicable for a charge (like flat fees), use null

SPECIAL NOTES FOR SAMMAMISH PLATEAU WATER BILLS:
- Meter information is displayed separately from service charges
- One meter may service multiple charge categories
- Billing days typically match the meter read period
- Usage is calculated from meter readings (present - previous)
- Line items show detailed breakdown: rate, usage in CF and gallons, and charge
- Contact information typically includes phone and email
- Some charges are usage-based (with rates), others are flat fees

"""

SAMMAMISH_PLATEAU_WATER_JSON_FORMAT = """

Return in this exact JSON format for Sammamish Plateau Water bills:
{
  "provider_name": "Sammamish Plateau Water",
  "provider_website": "website_url_or_null",
  "provider_customer_service_phone": "phone_number_or_null",
  "provider_customer_service_email": "email_address_or_null",
  "provider_address": "provider_physical_address_or_null",
  "provider_return_address": "provider_return_address_or_null",
  "account_number": "numeric_account_number",
  "account_type": "Water",
  "bill_number": "bill_or_statement_number_or_null",
  "bill_type": "bill_type_like_Regular_Final_Estimated_or_null",
  "customer_name": "customer_name_as_shown",
  "service_address": "customer_physical_service_address",
  "billing_address": "customer_mailing_billing_address",
  "bill_date": "date_format_like_October_05_2025",
  "total_amount_due_date": "date_format_like_October_25_2025",
  "number_of_days": "numeric_days_in_billing_period",
  "service_days": "numeric_days_same_as_number_of_days_or_null",
  "previous_balance": "dollar_amount_or_null",
  "current_billing": "dollar_amount_for_current_period",
  "total_amount_due": "final_dollar_amount_due",
  "balance": "current_outstanding_balance_or_null",
  
  "payments_applied": [
    {
      "payment_date": "date_format_like_October_15_2025",
      "payment_amount": "dollar_amount"
    }
  ],

  "late_fee_info": {
    "latefee_applied": "yes_or_no_or_null",
    "latefee_date": "date_when_late_fee_was_applied_or_null",
    "latefee_amount": "dollar_amount_of_late_fee_or_null",
    "latefee_by_duedate_percentage": "percentage_like_1%_or_null",
    "latefee_by_duedate": "dollar_amount_of_late_fee_if_late_or_null",
    "total_amount_with_latefee_by_duedate": "total_including_late_fees_or_null"
  },
  
  "contact_info": {
    "phone_number": "phone_like_425.392.6256",
    "email": "email_like_billing@spwater.org"
  },
  
  "meter": {
    "meter_number": "meter_id_like_68566030",
    "read_dates": {
      "start_date": "date_format_like_August_31_2025",
      "end_date": "date_format_like_September_30_2025"
    },
    "billing_days": "numeric_days_like_30",
    "meter_readings": {
      "previous_reading": "reading_value_like_0820413",
      "present_reading": "reading_value_like_0828725"
    },
    "usage": {
      "cubic_feet": {
        "usage": "numeric_value",
        "uom": "unit_like_CF_or_CCF"
      },
      "gallons": {
        "usage": "numeric_value_or_null",
        "uom": "gallons"
      }
    }
  },
  
  "service_types": [
    {
      "service_name": "service_name_like_Water",
      "current_service": "total_dollar_amount_for_all_charges",
      "service_from_date": "date_format_like_August_31_2025",
      "service_to_date": "date_format_like_September_30_2025",
      "line_item_charges": [
        {
          "category": "charge_description_like_WATER_BLOCK_1",
          "description": "detailed_charge_description_or_null",
          "rate": "rate_per_unit_or_null",
          "rate_per_cf": "rate_like_$0.0283/CF_or_null_if_flat_fee",
          "cubic_feet": "CF_usage_for_this_charge_or_null",
          "gallons": "gallon_usage_for_this_charge_or_null",
          "charge": "dollar_amount",
          "meter_number": null,
          "usage": "numeric_usage_value_or_null",
          "uom": "unit_like_CF_or_gallons_or_null",
          "previous_reading": null,
          "previous_reading_type": null,
          "current_reading": null,
          "current_reading_type": null,
          "usage_multiplier": "numeric_multiplier_like_1_or_null"
        },
        {
          "category": "another_charge_like_MULTI-FAMILY_WTR_PER_UNIT",
          "description": "detailed_charge_description_or_null",
          "rate": "rate_per_unit_or_null",
          "rate_per_cf": null,
          "cubic_feet": null,
          "gallons": null,
          "charge": "dollar_amount_for_flat_fee",
          "meter_number": null,
          "usage": null,
          "uom": null,
          "previous_reading": null,
          "previous_reading_type": null,
          "current_reading": null,
          "current_reading_type": null,
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
- Extract contact info: phone (425.392.6256) and email (billing@spwater.org)
- Create dedicated meter object with ALL meter details
- DO NOT put meter_number in line_item_charges
- DO NOT put meter readings in line_item_charges
- Keep meter information SEPARATE from service charges
- line_item_charges should only have category and amount (no meter data)
- Extract usage in both cubic feet and gallons if shown
- If gallons not shown, calculate or leave null

"""

SAMMAMISH_PLATEAU_WATER_PROMPT = f"""{BASE_EXTRACTION_FIELDS}

{SAMMAMISH_PLATEAU_WATER_SPECIFIC_INSTRUCTIONS}

{SAMMAMISH_PLATEAU_WATER_JSON_FORMAT}
"""
