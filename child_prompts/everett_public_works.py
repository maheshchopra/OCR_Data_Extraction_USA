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


EVERETT_PUBLIC_WORKS_SPECIFIC_INSTRUCTIONS = """
EVERETT PUBLIC WORKS SPECIFIC INSTRUCTIONS:

This template applies to bills with "Everett" text or "Everett Public Works" on the PDF.

SECTION 1 - CONTACT INFORMATION:
- Phone Number: Look for phone number in the format (XXX) XXX-XXXX OR XXX.XXX.XXXX
  * Pattern with parentheses: (425) 257-8999
  * Pattern with dots: 425.257.8999
  * Search for patterns with area code followed by 7 digits
  * Extract exactly as shown on the bill
- Website: Look for the Everett utility billing website
  * Common format: everettwa.gov/ub
  * May appear with or without "https://" or "www."
  * Look in header, footer, or contact information section
  * Extract the complete URL or domain

SECTION 2 - ACCOUNT INFORMATION:
- Account Number: Look for "Account Number", "Account No", or similar label
- Service Address: The physical location where utility services are provided

SECTION 3 - BILL DETAILS:
- Date Billed: The date when the bill was issued
- Due Date: The date when payment is due

SECTION 4 - CURRENT CHARGES:
- Extract EVERY SINGLE charge listed on the bill with type and amount
- Extract whatever service types/charges are shown on THIS specific bill
- Look for ALL line items in the charges section - do NOT skip any charges
- Each service/charge should have a type (as labeled on the bill) and an amount
- Keep extracting until you've found every charge on the bill

SECTION 5 - TOTALS:
- Total Current Charges: The sum of all current charges
- Total Due: The final amount due (may include previous balance)

SECTION 6 - CONSUMPTION:
- Look for "Current Consumption" label on the bill
- The value is typically displayed to the RIGHT of the "Current Consumption" text
- Format is usually a number followed by "CCF" (e.g., "134 CCF", "150 CCF")
- Extract the complete text including the unit, e.g.: "134 CCF"
- This field is REQUIRED - search the entire bill if needed
- Common locations: Near water service details, in a consumption summary section, or near meter readings

SECTION 7 - PROVIDER ADDRESS:
**CRITICAL**: Extract Everett Public Works address information
- Provider Address: Look for the Everett Public Works main address
  * Typically in header or footer of the bill
  * Format example: "Everett Public Works, 3200 Cedar Street, Everett, WA 98201"
  * Extract complete address including street, city, state, zip

SECTION 8 - LATE FEE INFORMATION:
**CRITICAL**: Extract all late fee and penalty information
- Late Fee Applied: Check if a late fee has been applied to this bill
  * Look in charges, adjustments, or penalty sections
  * Extract the date when late fee was applied
  * Extract the amount of the late fee applied
  * Format:
    - late_fee_date: "date_format_like_March_03_2025"
    - late_fee_amount: "$dollar_amount"
- Late Fee Percentage: Look for late payment charge rate
  * Common format: "1%", "1.5%", "1 percent per month"
  * Look for terms like "late payment charge", "late fee", "penalty rate"
  * Usually in payment terms or fine print section

SECTION 9 - BALANCE INFORMATION:
- Current Balance: The outstanding balance on the account
  * Look for "Current Balance", "Account Balance"
  * This is typically the amount currently owed
- Balance After Due Date: The balance including late fees if paid after due date

SECTION 10 - METER INFORMATION (CRITICAL):
**IMPORTANT**: Extract detailed meter data for each service
- For EACH meter on the bill, extract:
  1. Meter Number: The unique meter identifier
  2. Meter Location: Where the meter is located (if shown)
  3. Service Type: The service this meter measures (Water, Sewer, etc.)
  4. Read Date: When the meter was read
  5. Previous Reading: Meter reading at start of period
  6. Current Reading: Meter reading at end of period
  7. Usage: Consumption amount (numeric value only)
  8. Unit of Measurement (UOM): The unit (CCF, gallons, etc.)
  9. Multiplier: Any multiplier applied to calculate actual usage
     * Common values: "1", "10", "100", "0.1"
     * Actual usage = (Current Reading - Previous Reading) × Multiplier
     * Look for "Multiplier", "Mult", "Factor" labels near meter readings
  10. Read Type: How reading was obtained ("Actual", "Estimated", "Customer")

- Store meter information in a dedicated "meters" array
- DO NOT mix this with line_item_charges in service_types
- Each meter should have ALL fields even if some are null

SPECIAL NOTES FOR EVERETT BILLS:
- Everett bills have a distinct layout with contact information prominently displayed
- Phone numbers are in standard US format: (XXX) XXX-XXXX with area code in parentheses
- The phone number is ALWAYS present - look carefully at the top, header, or contact section of the bill
- **VERY IMPORTANT**: Everett bills typically have 4 OR MORE charges listed (e.g., Water, Sewer, Filtration, Solid Waste Program)
- DO NOT STOP after extracting just Water and Sewer - there are MORE charges below them
- Extract ALL charges exactly as labeled on the bill - missing even one charge will cause incorrect totals
- Read through the ENTIRE charges section before finishing
- The sum of all individual charges should equal the total current charges amount
"""

EVERETT_PUBLIC_WORKS_JSON_FORMAT = """
Return in this exact JSON format. ALL FIELDS MUST BE INCLUDED for Everett bills:
{
  "provider_name": "Everett Public Works",
  "provider_website": "website_url_or_null",
  "provider_customer_service_phone": "phone_number_or_null",
  "provider_customer_service_email": "email_address_or_null",
  "provider_address": "complete_provider_address_like_Everett_Public_Works_3200_Cedar_Street_Everett_WA_98201",
  "provider_return_address": "payment_return_address_like_PO_Box_or_null",
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
      "meter_number": "meter_identifier",
      "meter_location": "meter_location_description_or_null",
      "service_type": "service_type_like_Water_or_Sewer",
      "read_date": "date_format_like_March_03_2025_or_null",
      "previous_reading": "reading_value_at_start",
      "current_reading": "reading_value_at_end",
      "usage": "numeric_usage_value",
      "uom": "unit_like_CCF",
      "multiplier": "numeric_multiplier_like_1_or_10_or_null",
      "read_type": "Actual_or_Estimated_or_Customer_or_null"
    }
  ],

  "contact_info": {
  "phone_number": "phone_number_like_425.257.8999_or_(425)_257-8999",
  "website": "website_like_everettwa.gov/ub"
  },
  "account_info": {
    "account_number": "account_number",
    "service_address": "physical_service_address"
  },
  "bill_details": {
    "date_billed": "date_format_like_March_03_2025_or_null",
    "due_date": "date_format_like_March_03_2025_or_null"
  },
  "current_charges": [
    {
      "type": "service_or_charge_type_as_shown_on_bill",
      "amount": "dollar_amount"
    },
    {
      "type": "another_service_or_charge_type",
      "amount": "dollar_amount"
    },
    {
      "type": "keep_adding_all_charges_from_bill",
      "amount": "dollar_amount"
    }
  ],
  "totals": {
    "total_current_charges": "dollar_amount",
    "total_due": "dollar_amount"
  },
  "consumption": {
    "current_consumption": "REQUIRED_extract_CCF_value_like_134_CCF_from_Current_Consumption_field"
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

EVERETT_PUBLIC_WORKS_PROMPT = f"""{BASE_EXTRACTION_FIELDS}

{EVERETT_PUBLIC_WORKS_SPECIFIC_INSTRUCTIONS}

{EVERETT_PUBLIC_WORKS_JSON_FORMAT}
"""