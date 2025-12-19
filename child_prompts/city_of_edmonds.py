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

CITY_OF_EDMONDS_SPECIFIC_INSTRUCTIONS = """

CITY OF EDMONDS SPECIFIC INSTRUCTIONS:

This template applies to bills with "City of Edmonds" or "Edmonds" text.

SECTION 1 - PROVIDER INFORMATION:
**CRITICAL**: Extract City of Edmonds provider information
- Provider Name: "City of Edmonds"
- Provider Website: Look for website URL in header/footer/contact sections
- Provider Customer Service Phone: Extract phone number exactly as shown
- Provider Customer Service Email: Extract support/billing email if present
- Provider Address: Extract complete mailing/business address
- Provider Return Address: Extract remit/payment address (may be PO Box or same as provider address)

SECTION 2 - ACCOUNT INFORMATION:
- Account Number: Digits/letters from "Account Number" label
- Account Type: Typically "Water/Sewer/Stormwater" or similar service bundle
- Bill Number: Statement/Invoice/Bill number as shown
- Bill Type: Identify type (Regular, Final, Estimated, Adjusted) if indicated
- Customer Name: Account holder/property owner
- Service Address & Billing Address: Capture complete addresses

SECTION 3 - BILL DETAILS:
- Bill Date, Total Amount Due Date, Number of Days, Service Days
  * Use exact formatting like "March 03 2025" or "Mar 3 2025"

SECTION 4 - BILLING SUMMARY:
- Extract previous_balance, current_billing, current_adjustments, total_amount_due, balance
- Ensure all values include dollar signs and commas exactly as on bill

SECTION 5 - PAYMENT INFORMATION:
- payment_information: Most recent payment date & amount
- payments_applied array: EACH payment entry with date + amount

SECTION 6 - LATE FEE INFORMATION:
- Capture whether a late fee applied, dates, amounts, rate/percentage, and projected totals

SECTION 7 - METER INFORMATION:
- Edmonds bills typically list at least one water meter
- For EACH meter, extract meter_number, location (if stated), service_type, read_date, start/end dates, previous/current readings, reading types, usage, UOM, multiplier, and read_type
- Store all meters in meters array; include nulls if data missing

SECTION 8 - SERVICE CHARGES (CRITICAL):
- Extract EVERY service/charge row (Water base, Water consumption, Sewer, Stormwater, Surface Water, Recycling, etc.)
- For EACH service entry:
  - service_name: exact label from bill
  - current_service: dollar amount for that specific service
  - service_from_date / service_to_date: service period if shown
  - previous_reading / current_reading: include when provided
  - line_item_charges: capture ALL sub-charges for the service; at minimum create one entry mirroring the service row
    * Include category, description (if available), rate, amount, meter_number, usage, UOM, readings, reading types, usage_multiplier
- Taxes and franchise fees that appear alongside services should be captured as their own line items within the appropriate service (or dedicated service entry if shown separately)
- The sum of ALL current_service values must equal current_billing

SECTION 9 - TAXES:
- Capture municipal/franchise/state taxes in taxes object
  * per_service_taxes: taxes tied to individual services (include service_name, tax_name, tax_rate, tax_amount)
  * global_taxes: bill-wide taxes/fees

SECTION 10 - ADJUSTMENTS:
- Extract ALL adjustments/credits with category and signed amount
- Use positive values for credits and negative for debits/fees

GENERAL RULES:
- Extract EVERY field listed in field_names.txt
- Use null only when data is truly absent
- Preserve dollar signs, commas, and parentheses as shown
- Use empty arrays [] when no entries exist (payments_applied, adjustments, taxes, meters, service_types, line_item_charges)

"""

CITY_OF_EDMONDS_JSON_FORMAT = """

Return in this exact JSON format. ALL FIELDS MUST BE INCLUDED for City of Edmonds bills:
{
  "provider_name": "City of Edmonds",
  "provider_website": "website_url_or_null",
  "provider_customer_service_phone": "phone_number_or_null",
  "provider_customer_service_email": "email_address_or_null",
  "provider_address": "complete_provider_address_or_null",
  "provider_return_address": "payment_return_address_or_null",
  "account_number": "account_number_or_null",
  "account_type": "Water/Sewer/Stormwater_or_null",
  "bill_number": "bill_or_statement_number_or_null",
  "bill_type": "Regular_Final_Estimated_Adjusted_or_null",
  "customer_name": "customer_name_or_null",
  "service_address": "service_address_or_null",
  "billing_address": "billing_address_or_null",
  "bill_date": "date_format_like_March_03_2025_or_null",
  "total_amount_due_date": "date_format_like_March_03_2025_or_null",
  "number_of_days": "numeric_days_or_null",
  "service_days": "numeric_days_or_null",
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
      "meter_number": "meter_identifier_or_null",
      "meter_location": "meter_location_description_or_null",
      "service_type": "service_type_like_Water_or_null",
      "read_date": "date_format_like_March_03_2025_or_null",
      "start_date": "service_from_date_or_null",
      "service_from_date": "service_from_date_or_null",
      "end_date": "service_to_date_or_null",
      "service_to_date": "service_to_date_or_null",
      "previous_reading": "reading_value_or_null",
      "previous_reading_type": "Actual_or_Estimated_or_Customer_or_null",
      "current_reading": "reading_value_or_null",
      "current_reading_type": "Actual_or_Estimated_or_Customer_or_null",
      "usage": "numeric_usage_value_or_null",
      "uom": "unit_like_CCF_gallons_kgal_or_null",
      "multiplier": "numeric_multiplier_or_null",
      "read_type": "Actual_or_Estimated_or_Customer_or_null"
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
          "uom": "unit_like_CCF_or_null",
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

CITY_OF_EDMONDS_PROMPT = f"""{BASE_EXTRACTION_FIELDS}

{CITY_OF_EDMONDS_SPECIFIC_INSTRUCTIONS}

{CITY_OF_EDMONDS_JSON_FORMAT}
"""
