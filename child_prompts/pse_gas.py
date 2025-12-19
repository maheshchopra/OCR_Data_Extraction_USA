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

PSE_GAS_SPECIFIC_INSTRUCTIONS = """

PUGET SOUND ENERGY (PSE) GAS BILL SPECIFIC INSTRUCTIONS:

This template applies to bills with "Puget Sound Energy" or "PSE" text for GAS service.

CRITICAL STRUCTURE:
- PSE gas bills organize charges BY METER NUMBER
- Each meter has its own section with meter details and associated charges
- You MUST extract ALL meters shown on the bill
- Each meter section is completely independent
- Gas usage is typically measured in therms or CCF (hundred cubic feet)

SECTION 1 - ACCOUNT INFORMATION:
- Account Number: Look for "Account Number" or "Acct No"
- Customer Name: Account holder name
- Service Address: Physical location of service
- Billing Address: Mailing address for billing

SECTION 2 - BILL DETAILS:
- Bill Date: Date the bill was issued
- Due Date: Payment due date
- Number of Days: Billing period length
- Previous Balance: Balance from last bill
- Payments Applied: Any payments received (extract date and amount)
- Total Amount Due: Final balance due

SECTION 3 - CONTACT INFORMATION:
**CRITICAL**: Extract PSE contact information (usually found in header, footer, or payment section)
- Website: Look for "pse.com" or "www.pse.com"
  * May appear as full URL: https://www.pse.com or just pse.com
  * Extract as shown (with or without www/https)
- Email: Look for "customercare@pse.com" or similar PSE email address
  * Common format: customercare@pse.com, billing@pse.com
  * Extract the complete email address
- Phone Number: Look for customer service phone number
  * Common format: 1-888-225-5773 or (888) 225-5773
  * Extract as shown on bill
  * This is typically in the contact/customer service section

SECTION 4 - LATE PAYMENT FEE INFORMATION:
**CRITICAL**: Look for late payment fee or penalty information
- Percentage: Extract the late fee percentage rate
  * Common format: "1%", "1.0%", "1 percent"
  * Look for terms like "late payment fee", "late charge", "penalty rate", "interest on past due"
  * Usually appears in payment terms or important notice section
- Description: Extract the complete description of late payment terms
  * Example: "A late payment fee of 1% per month will be charged on past due amounts"
  * Extract full text explaining the late fee policy

SECTION 5 - METER INFORMATION (MOST CRITICAL):
For EACH meter on the bill, extract:
- Meter Number: Unique identifier for the meter
- Service Type: "Gas" or "Natural Gas"
- Read Date: Date the meter was read
- Start Date: Billing period start date
- End Date: Billing period end date
- Previous Reading: Meter reading at start of period
- Previous Reading Type: "Actual", "Estimated", or "Customer"
- Current Reading: Meter reading at end of period
- Current Reading Type: "Actual", "Estimated", or "Customer"
- Usage: Consumption amount in therms or CCF (numeric value only)
- UOM: Unit of measurement (therms, CCF, etc.)
- Multiplier: Any multiplier applied (typically 1 for gas meters)
- Read Type: How reading was obtained ("Actual", "Estimated", "Customer")
- Total Current Charges: Total dollar amount for this meter

SECTION 6 - SERVICE CHARGES:
- Extract ALL line item charges for each meter
- Common gas charges include:
  * Base charge (monthly service fee)
  * Delivery charges
  * Gas supply charges
  * Usage-based charges (per therm or CCF)
- For each line item, extract:
  * Category: Charge description
  * Description: Detailed description if available
  * Rate: Rate per unit (if applicable)
  * Amount: Dollar amount for this charge
  * Usage: Consumption amount if applicable
  * UOM: Unit of measurement

SECTION 7 - TAXES:
- Extract all tax information:
  * Per-service taxes (tied to specific services)
  * Global taxes (applied to entire bill)
  * Common taxes: Sales Tax, Utility Tax, etc.

SECTION 8 - ADJUSTMENTS:
- Extract ALL adjustments separately with their category names and amounts
- Include both positive adjustments (credits) and negative adjustments (debits/fees)
- Use positive amounts for credits (e.g., "$50.00" for a credit)
- Use negative amounts for debits/fees (e.g., "-$10.00" for a late fee)

"""

PSE_GAS_JSON_FORMAT = """

Return in this exact JSON format. ALL FIELDS MUST BE INCLUDED for PSE Gas bills:
{
  "provider_name": "Puget Sound Energy",
  "provider_website": "website_url_like_pse.com_or_null",
  "provider_customer_service_phone": "phone_number_or_null",
  "provider_customer_service_email": "email_address_or_null",
  "provider_address": "complete_provider_address_or_null",
  "provider_return_address": "payment_return_address_or_null",
  "account_number": "numeric_digits_only_or_null",
  "account_type": "Gas",
  "bill_number": "bill_or_statement_number_or_null",
  "bill_type": "bill_type_like_Regular_Final_Estimated_or_null",
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
      "meter_number": "meter_identifier",
      "meter_location": "meter_location_description_or_null",
      "service_type": "Gas",
      "read_date": "date_format_like_March_03_2025_or_null",
      "start_date": "billing_period_start_date_or_null",
      "service_from_date": "billing_period_start_date_or_null",
      "end_date": "billing_period_end_date_or_null",
      "service_to_date": "billing_period_end_date_or_null",
      "previous_reading": "reading_value_at_start",
      "previous_reading_type": "Actual_or_Estimated_or_Customer_or_null",
      "current_reading": "reading_value_at_end",
      "current_reading_type": "Actual_or_Estimated_or_Customer_or_null",
      "usage": "numeric_usage_value",
      "uom": "unit_like_therms_or_CCF",
      "multiplier": "numeric_multiplier_like_1_or_null",
      "read_type": "Actual_or_Estimated_or_Customer_or_null",
      "total_current_gas_charges": "dollar_amount_for_this_meter_or_null"
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
          "uom": "unit_like_therms_or_CCF_or_null",
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

PSE_GAS_PROMPT = f"""{BASE_EXTRACTION_FIELDS}

{PSE_GAS_SPECIFIC_INSTRUCTIONS}

{PSE_GAS_JSON_FORMAT}
"""
