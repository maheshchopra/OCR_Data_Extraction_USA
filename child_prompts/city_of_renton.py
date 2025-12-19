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

CITY_OF_RENTON_SPECIFIC_INSTRUCTIONS = """

CITY OF RENTON SPECIFIC INSTRUCTIONS:

This template applies to bills with "City of Renton" or "Renton" text.

SECTION 1 - PROVIDER INFORMATION:
**CRITICAL**: Extract City of Renton provider information
- Provider Name: "City of Renton"
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
- Extract ALL services (Water, Sewer, Wastewater, etc.) with complete details
- For EACH service, extract:
  - Service Name: The service type exactly as labeled on the bill
  - Current Service: Total dollar amount for this service
    * This should be the sum of all line item charges for THIS specific service
  - Service From Date: Service period start date
    * Look for "Service From", "From Date", "Period Start"
  - Service To Date: Service period end date
    * Look for "Service Through", "Through Date", "To Date", "Period End"
  - Previous Reading: Meter reading at start (if applicable)
  - Current Reading: Meter reading at end (if applicable)
  - Line Item Charges: Extract EVERY line item for this service
    * Each line item must include:
      - Category: The charge category/description
      - Description: Detailed description (if different from category)
      - Rate: Rate per unit (if applicable)
      - Amount: Dollar amount for this line item
      - Meter Number: Associated meter identifier (if applicable)
      - Usage: Consumption amount for this line item (numeric value)
      - UOM: Unit of measurement (CCF, gallons, etc.)
      - Previous Reading: Meter reading at start for this line item
      - Previous Reading Type: "Actual", "Estimated", or "Customer"
      - Current Reading: Meter reading at end for this line item
      - Current Reading Type: "Actual", "Estimated", or "Customer"
      - Usage Multiplier: Multiplier applied to calculate usage

- **IMPORTANT**: Group all meters/services of the same type together into ONE service entry
- The sum of all current_service amounts must equal current_billing

SECTION 9 - TAXES:
- Extract all tax information:
  - Per-service taxes (tied to specific services)
    * Extract tax name, rate (percentage), and amount for each service
  - Global taxes (applied to entire bill)
    * Extract tax name, rate (percentage), and amount
    * Common taxes: Sales Tax, Utility Tax, etc.

SECTION 10 - ADJUSTMENTS:
- Extract ALL adjustments separately with their category names and amounts
- Look for "Adjustments", "Account Adjustments", "Credits/Adjustments" sections
- Include both positive adjustments (credits) and negative adjustments (debits/fees)
- Use positive amounts for credits (e.g., "$50.00" for a credit)
- Use negative amounts for debits/fees (e.g., "-$10.00" for a late fee)

"""

CITY_OF_RENTON_JSON_FORMAT = """

Return in this exact JSON format. ALL FIELDS MUST BE INCLUDED for City of Renton bills:
{
  "provider_name": "City of Renton",
  "provider_website": "website_url_or_null",
  "provider_customer_service_phone": "phone_number_or_null",
  "provider_customer_service_email": "email_address_or_null",
  "provider_address": "complete_provider_address_or_null",
  "provider_return_address": "payment_return_address_or_null",
  "account_number": "numeric_digits_only_or_null",
  "account_type": "Water & Sewer",
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
      "service_type": "service_type_like_Water_or_Sewer",
      "read_date": "date_format_like_March_03_2025_or_null",
      "previous_reading": "reading_value_at_start",
      "previous_reading_type": "Actual_or_Estimated_or_Customer_or_null",
      "current_reading": "reading_value_at_end",
      "current_reading_type": "Actual_or_Estimated_or_Customer_or_null",
      "usage": "numeric_usage_value",
      "uom": "unit_like_CCF_or_gallons",
      "multiplier": "numeric_multiplier_like_1_or_10_or_null",
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

CITY_OF_RENTON_PROMPT = f"""{BASE_EXTRACTION_FIELDS}

{CITY_OF_RENTON_SPECIFIC_INSTRUCTIONS}

{CITY_OF_RENTON_JSON_FORMAT}
"""
