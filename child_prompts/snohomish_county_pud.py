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

SNOHOMISH_COUNTY_PUD_SPECIFIC_INSTRUCTIONS = """

SNOHOMISH COUNTY PUD SPECIFIC INSTRUCTIONS:

This template applies to bills with "Snohomish County PUD" or "SnoPUD" text.

SECTION 1 - PROVIDER INFORMATION:
- Provider Name: "Snohomish County PUD"
- Extract website, customer service phone/email, provider and remit addresses.

SECTION 2 - ACCOUNT INFORMATION:
- Account number, account type (Electric), bill number/type, customer name, service/billing addresses.

SECTION 3 - BILL DETAILS:
- Bill date, total amount due date, number of days, service days.

SECTION 4 - BILLING SUMMARY:
- previous_balance, current_billing, current_adjustments, total_amount_due, balance.

SECTION 5 - PAYMENT INFORMATION:
- Latest payment info plus payments_applied array with all payments shown.

SECTION 6 - LATE FEE INFORMATION:
- Capture late fee applied (yes/no), date, amount, percentage, projected totals.

SECTION 7 - METER INFORMATION (CRITICAL):
- SnoPUD electric bills list each meter with:
  * meter_number, meter_location (if shown), service_type (Electric), read_date, start/end dates,
  * previous/current readings + types, usage, uom (kWh), multiplier, read_type, total meter charges.
- Store each meter in the meters array.

SECTION 8 - SERVICE TYPES / LINE ITEMS:
- For each service (e.g., Residential Electric, Delivery, Conservation) gather:
  * service_name, current_service amount, service date range.
  * `line_item_charges` entries include category, description, rate, rate_x_unit if shown, amount, meter_number, usage, uom, readings, usage_multiplier.
- Sum of all `current_service` values must equal current_billing.

SECTION 9 - TAXES:
- Populate per_service_taxes and global_taxes arrays with tax name, rate, amount, plus service_name when applicable.

SECTION 10 - ADJUSTMENTS:
- Capture each adjustment with category and signed amount (credits positive, debits negative).

SECTION 11 - CURRENT CHARGES BOX (CRITICAL):
**CRITICAL**: Use the "Current Charges" box to break down the total current billing.

1) BOX FORMAT:
The bill shows a "Current Charges" section with individual lines such as:
- "Late Payment Charge .......................... $5.00"
- "Transfer In .................................. $113.88"
- "Utility Charges ............................. $3,496.58"
- "Municipal Tax Electric ...................... $209.80"

2) EXTRACTION RULES:
- For EACH line in the "Current Charges" box:
  * Extract the charge description as `category` (e.g., "Late Payment Charge", "Transfer In", "Utility Charges", "Municipal Tax Electric").
  * Extract the dollar amount as `amount` (e.g., "5.00", "113.88", "3496.58", "209.80").
- Put all of these into a `current_charges` array.

3) VALIDATION RELATIONSHIP:
- The sum of all `current_charges[i].amount` MUST equal `current_billing`.
- This `current_charges` array will be used by the validation logic to verify that the bill’s `current_billing` is correct.

4) IMPORTANT:
- Include ALL lines in the "Current Charges" box, even if some amounts are $0.00.
- Do NOT mix these with line_item_charges or taxes; they are a separate summary section.

"""

SNOHOMISH_COUNTY_PUD_JSON_FORMAT = """

{
  "provider_name": "Snohomish County PUD",
  "provider_website": "website_url_or_null",
  "provider_customer_service_phone": "phone_number_or_null",
  "provider_customer_service_email": "email_address_or_null",
  "provider_address": "complete_provider_address_or_null",
  "provider_return_address": "payment_return_address_or_null",
  "account_number": "numeric_digits_only_or_null",
  "account_type": "Electric",
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

  "current_charges": [
    {
      "category": "description_from_Current_Charges_box_like_Late_Payment_Charge",
      "amount": "dollar_amount"
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
      "service_type": "Electric",
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
      "uom": "unit_like_kWh_or_null",
      "multiplier": "numeric_multiplier_like_1_or_null",
      "read_type": "Actual_or_Estimated_or_Customer_or_null",
      "total_current_electric_charges": "dollar_amount_or_null"
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
          "rate_x_unit": "calculation_like_150_kWh_x_$0.05_or_null",
          "amount": "dollar_amount",
          "meter_number": "meter_id_or_null",
          "usage": "numeric_value_or_null",
          "uom": "unit_like_kWh_or_null",
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

"""

SNOHOMISH_COUNTY_PUD_PROMPT = f"""{BASE_EXTRACTION_FIELDS}

{SNOHOMISH_COUNTY_PUD_SPECIFIC_INSTRUCTIONS}

{SNOHOMISH_COUNTY_PUD_JSON_FORMAT}
"""
