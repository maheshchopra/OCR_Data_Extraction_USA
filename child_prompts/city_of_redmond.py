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

CITY_OF_REDMOND_SPECIFIC_INSTRUCTIONS = """
CITY OF REDMOND SPECIFIC INSTRUCTIONS:

This template applies to bills with "City of Redmond" text or "Redmond Washington" logo.

SECTION 1 - AGENCY INFORMATION:
- Look for agency/city information (typically the City of Redmond's name and mailing address)
- This may be in the header or top left of the bill
- Extract as a single text string with the complete information

SECTION 2 - ACCOUNT INFORMATION:
- Account Number: Look for "Account Number", "Account No", or similar label
- Customer Name: Look for "Name", "Account Holder", or "Customer Name"
- Service Address: The physical location where utility services are provided
- Billing Address: The mailing address (if different from service address)
- Extract all four pieces of information from this section

SECTION 3 - BILL DETAILS:
- Service Period: CRITICAL - Look for the billing period dates
  * Common locations: "Bill Details" section, 
  * Common formats:
    - "9/3/2025 to 10/7/2025 (35 days)"
    - "September 3, 2025 - October 7, 2025 (35 days)"
  * Extract as a SINGLE TEXT STRING exactly as shown, including the number of days if present
  * Look for labels like "Service Period", with a date below it.
  * This field is REQUIRED - search thoroughly if not immediately visible
  * Example extraction: "9/3/2025 to 10/7/2025 (35 days)"
- Billing Date: Look for "Billing Date"
- Due Date: Look for "Due Date"

SECTION 4 - CURRENT CHARGES (MOST CRITICAL):
- Look for a section labeled "Current Charges" or "Charges This Period"
- This section will have a table or list with "Type" and "Amount" columns
- **YOU MUST EXTRACT SERVICES FROM THIS SECTION TO POPULATE service_types ARRAY**
- For EACH line item in the Current Charges section, create TWO entries:
  
  A) An entry in "current_charges" array:
     - type: The service type exactly as labeled on the bill
     - amount: The dollar amount for that charge
  
  B) An entry in "service_types" array:
     - service_name: Same as the type from current_charges
     - current_service: Same as the amount from current_charges
     - service_from_date: If shown, otherwise null
     - service_to_date: If shown, otherwise null
     - previous_reading: null (unless meter reading is shown)
     - current_reading: null (unless meter reading is shown)
     - line_item_charges: [] (empty array)

- Example: If Current Charges shows:
  * Type: "Water Service", Amount: "$45.50"
  * Type: "Sewer Service", Amount: "$16.61"
  
  Then create:
  - current_charges: [{"type": "Water Service", "amount": "$45.50"}, {"type": "Sewer Service", "amount": "$16.61"}]
  - service_types: [{"service_name": "Water Service", "current_service": "$45.50", ...}, {"service_name": "Sewer Service", "current_service": "$16.61", ...}]

- Extract ALL charges listed - scan the entire Current Charges section
- The sum of all current_service amounts must equal current_billing

SECTION 5 - BILL SUMMARY:
- Look for "Bill Summary", "Account Summary", or "Summary of Charges"
- Extract these specific fields:
  - Previous Balance (amount carried forward from last bill)
  - Current Charges (total of all current service charges)
  - Adjustments (any credits or debits applied)
  - Payments Received (look carefully for "Payment", "Payment Received", "Payments Applied" - may be shown as negative)
  - Total Amount Due (final balance)

SECTION 6 - TOTAL AMOUNT DUE:
- This is included in the bill_summary section
- Should be prominently displayed, often in a box or highlighted section

SECTION 7 - PROVIDER INFORMATION:
**CRITICAL**: Extract City of Redmond provider contact and address information
- Provider Address: Look for the City of Redmond's main address (typically in header)
  * Format example: "City of Redmond, 15670 NE 85th St, Redmond, WA 98052"
  * Extract complete address including street, city, state, zip
- Provider Return Address: Look for "Remit Payment To" or return address for payments
  * This is where customers mail their payments
  * May be a PO Box or different from main address
  * Format example: "City of Redmond, PO Box 97010, Redmond, WA 98073-9710"

SECTION 8 - BILL NUMBER AND TYPE:
**CRITICAL**: Extract bill identification information
- Bill Number: Look for "Bill Number", "Statement Number", "Invoice Number"
  * Extract the complete bill identifier
  * Format example: "12345678" or "BILL-2025-001234"
- Bill Type: Identify the type of bill
  * Common types: "Regular", "Final", "Estimated", "Adjusted"
  * Look for indicators like "Final Bill", "Estimated Reading", etc.

SECTION 9 - LATE FEE INFORMATION (MOST CRITICAL):
**CRITICAL**: Extract all late fee and penalty information
- Late Fee Applied: Check if a late fee has been applied to this bill
  * Look in charges, adjustments, or penalty sections
  * Extract the date when late fee was applied
  * Extract the amount of the late fee applied
  * Format:
    - late_fee_date: "date_format_like_March_03_2025"
    - late_fee_amount: "$dollar_amount"
- Late Fee by Due Date Percentage: Look for late payment charge rate
  * Common format: "1%", "1.5%", "1 percent per month"
  * Look for terms like "late payment charge", "late fee", "penalty rate"
  * Usually in payment terms, fine print, or important notice section
- Total Amount of Late Fees by Due Date: Calculate or extract total late fees
  * This is the amount that will be charged if payment is late
  * May be shown as "Late fee if paid after [date]: $XX.XX"

SECTION 10 - BALANCE INFORMATION:
- Current Balance: The outstanding balance on the account
  * This may be different from Total Amount Due
  * Look for "Current Balance", "Account Balance"
- Balance After Due Date: The balance including late fees if paid after due date
  * Calculate: Current Balance + Late Fees

SECTION 11 - METER INFORMATION (CRITICAL):
**IMPORTANT**: Extract detailed meter data for each service
- For EACH meter on the bill, extract:
  1. Meter Number: The unique meter identifier
  2. Meter Location: Where the meter is located (if shown)
  3. Service Type: The service this meter measures (Water, Sewer, etc.)
  4. Read Date: When the meter was read
  5. Previous Reading: Meter reading at start of period
  6. Current Reading: Meter reading at end of period
  7. Usage: Consumption amount (numeric value only)
  8. Unit of Measurement (UOM): The unit (CCF, gallons, kWh, etc.)
  9. Multiplier: Any multiplier applied to calculate actual usage
     * Common values: "1", "10", "100", "0.1"
     * Actual usage = (Current Reading - Previous Reading) × Multiplier
  10. Read Type: How reading was obtained ("Actual", "Estimated", "Customer")

- Store meter information in a dedicated "meters" array
- DO NOT mix this with line_item_charges in service_types

SPECIAL NOTES FOR REDMOND BILLS:
- **CRITICAL**: You MUST populate BOTH current_charges AND service_types from the Current Charges section
- Each service in Current Charges must appear in BOTH arrays
- Redmond bills typically separate different service types clearly in the "Current Charges" section
- The Current Charges section is usually a table with "Type" and "Amount" columns
- Extract ALL service charges listed - there may be multiple different types
- Payment information may be shown as "Payment Received", "Payment", or as a credit (negative amount)
- Look carefully in the bill summary section for all payment-related fields
- Service period should be extracted as displayed - don't split into separate start/end dates
- **VALIDATION**: The sum of all current_service amounts in service_types MUST equal current_billing
"""

CITY_OF_REDMOND_JSON_FORMAT = """
Return in this exact JSON format. ALL FIELDS MUST BE INCLUDED, including the Redmond-specific fields below:
{
  "provider_name": "City of Redmond",
  "provider_website": "website_url_or_null",
  "provider_customer_service_phone": "phone_number_or_null",
  "provider_customer_service_email": "email_address_or_null",
  "provider_address": "complete_provider_address_like_City_of_Redmond_15670_NE_85th_St_Redmond_WA_98052",
  "provider_return_address": "payment_return_address_like_PO_Box_97010_Redmond_WA_98073",
  "account_number": "numeric_digits_only_or_null",
  "account_type": "Water & Sewer",
  "bill_number": "bill_or_statement_number_or_null",
  "bill_type": "bill_type_like_Regular_Final_Estimated_or_null",
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
  "service_days": "numeric_days_same_as_number_of_days_or_null",
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

   "provider_info": {
    "provider_address": "complete_provider_address_like_City_of_Redmond_15670_NE_85th_St_Redmond_WA_98052",
    "provider_return_address": "payment_return_address_like_PO_Box_97010_Redmond_WA_98073"
  },

  "bill_info": {
    "bill_number": "bill_or_statement_number_or_null",
    "bill_type": "bill_type_like_Regular_Final_Estimated_or_null"
  },

  "late_fee_info": {
    "latefee_applied": "yes_or_no_or_null",
    "latefee_date": "date_when_late_fee_was_applied_or_null",
    "latefee_amount": "dollar_amount_of_late_fee_or_null",
    "latefee_by_duedate_percentage": "percentage_like_1%_or_1.5%_or_null",
    "latefee_by_duedate": "dollar_amount_of_late_fee_if_late_or_null",
    "total_amount_with_latefee_by_duedate": "total_including_late_fees_or_null"
  },

  "balance_info": {
    "current_balance": "current_outstanding_balance_or_null",
    "balance_after_due_date": "balance_including_late_fees_or_null"
  },

  "meters": [
    {
      "meter_number": "meter_identifier_like_12345678",
      "meter_location": "meter_location_description_or_null",
      "service_type": "service_type_like_Water_or_Sewer",
      "read_date": "date_format_like_March_03_2025_or_null",
      "previous_reading": "reading_value_at_start",
      "previous_reading_type": "Actual_or_Estimated_or_Customer_or_null",
      "current_reading_type": "Actual_or_Estimated_or_Customer_or_null"
      "current_reading": "reading_value_at_end",
      "usage": "numeric_usage_value",
      "uom": "unit_like_CCF_or_gallons",
      "multiplier": "numeric_multiplier_like_1_or_10_or_100",
      "read_type": "Actual_or_Estimated_or_Customer_or_null"
    }
  ],

  "agency_information": "complete_text_with_agency_name_and_address",
  "account_information": {
    "account_number": "account_number",
    "customer_name": "customer_or_account_holder_name",
    "service_address": "physical_service_address",
    "billing_address": "mailing_billing_address"
  },
  "bill_details": {
    "service_period": "EXTRACT_DATE_RANGE_LIKE_9/3/2025_to_10/7/2025_(35_days)",
    "billing_date": "date_format_like_March_03_2025_or_null",
    "due_date": "date_format_like_March_03_2025_or_null"
  },
  "current_charges": [
    {
      "type": "service_or_charge_type_as_shown_on_bill",
      "amount": "dollar_amount"
    }
  ],
  "bill_summary": {
    "previous_balance": "dollar_amount_or_null",
    "current_charges": "dollar_amount_or_null",
    "adjustments": "dollar_amount_or_null",
    "payments_received": "dollar_amount_or_null",
    "total_amount_due": "dollar_amount_or_null"
  },
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
      "description": "description_of_service",
      "current_service": "dollar_amount_or_null",
      "service_from_date": "date_format_like_March_03_2025_or_null",
      "service_to_date": "date_format_like_March_03_2025_or_null",
      "previous_reading": "reading_value_or_null",
      "current_reading": "reading_value_or_null",
      "line_item_charges": [
        {
          "category": "category_description_as_shown_on_bill",
          "description": "detailed_description_as_shown_on_bill",
          "amount": "dollar_amount",
          "rate": "rate_per_unit_or_null",
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
  ]
}
"""

CITY_OF_REDMOND_PROMPT = f"""{BASE_EXTRACTION_FIELDS}

{CITY_OF_REDMOND_SPECIFIC_INSTRUCTIONS}

{CITY_OF_REDMOND_JSON_FORMAT}
"""