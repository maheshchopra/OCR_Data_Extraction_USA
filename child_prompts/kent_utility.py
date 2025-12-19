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

KENT_UTILITY_SPECIFIC_INSTRUCTIONS = """

KENT UTILITY CONTACT INFORMATION:
- Extract the "Remit Payment To" address exactly as shown on the bill
- This is typically the payment mailing address displayed prominently on the bill
- Format as a single text string including all address lines

KENT UTILITY PAYMENT WEBSITE:
- Extract the website URL for online payments
- Common format: Pay.KentWA.gov or similar Kent utility payment website
- This is usually displayed in the payment instructions or bill header section
- Include the exact URL as shown on the bill

KENT UTILITY ACCOUNT INFORMATION:
- Account Number: The unique account identifier
- Customer Name: Name on the account
- Service Address: The physical address where services are provided

KENT UTILITY BILL DETAILS:
- Bill Date: When the bill was issued
- Due Date: When payment is due

KENT UTILITY CURRENT CHARGES - EXTREMELY CRITICAL:
- **MOST IMPORTANT**: Kent Utility bills have multiple SEPARATE services that must each be extracted as INDIVIDUAL entries
- Common services include but are not limited to:
  * Water (water usage charge)
  * Sewer (sewer service charge)
  * Access (separate access fee - DO NOT nest this under Water!)
  * Technology Fee (technology service fee)
  * Stormwater Management
  * Surface Water
  * Any other service charges listed
- Each service MUST be its own entry with its own type and amount
- **DO NOT nest "Access" charges under "Water"** - they are SEPARATE services
- **DO NOT nest any service under another** - each charge type is completely independent
- Extract EVERY service charge exactly as labeled on the bill
- Each entry should have:
  * type: The exact service name as shown (e.g., "Water", "Sewer", "Access", "Technology Fee")
  * amount: The charge amount for that specific service (e.g., "$130.01", "$55.17")
- The sum of ALL individual service charges must equal the total current charges/current billing amount
- Scan the entire charges section carefully - there may be 3, 4, 5, or more different services
- If you see "Access" as a separate line item, it MUST be its own entry, not grouped with Water
- Missing even one service will cause validation failures

KENT UTILITY TOTALS:
- Total Current Charges: Sum of all current service charges this billing period (should equal current_billing)
- Total Due: Final amount due 

KENT UTILITY BILL SUMMARY (CRITICAL):
- Look for a "Bill Summary" or "Account Summary" section on the bill
- Extract these specific fields:
  * Previous Amount Due: The balance from the previous billing period
  * Payments: Any payments received (look for "Payments", "Payment Received", "Amount Paid")
  * Current Charges: Total of current period charges
  * Total Amount Due: Final balance after payments and current charges
- Create entries in the payments_applied array for each payment found
- Set previous_balance to the "Previous Amount Due" value

KENT UTILITY PREVIOUS AMOUNT DUE (CRITICAL):
- Look for "Bill Summary" or "Account Summary" section
- Extract "Previous Amount Due" or "Previous Balance"
- This is the balance carried forward from the last billing period
- Store in previous_amount_due field
- Example: If bill shows "Previous Amount Due: $430.13"
- Extract: "previous_amount_due": "$430.13"

KENT UTILITY CURRENT USAGE (CRITICAL):
- Look for "Current Usage" section on the bill
- This section shows water meter readings and consumption
- Extract THREE specific values:
  1. Previous Reading: The meter reading at the start of the billing period
  2. Current Reading: The meter reading at the end of the billing period
  3. Usage: The consumption amount (usually in CCF)
- Store in current_usage object, NOT in service_types
- Example: If Current Usage shows:
  * Previous Reading: 483
  * Current Reading: 508
  * Usage: 25 CCF
- Extract:
  "current_usage": {
    "previous_reading": "483",
    "current_reading": "508",
    "usage": "25 CCF"
  }
- DO NOT put this data in service_types line_item_charges

LATE FEE INFORMATION:
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

BALANCE INFORMATION:
- Current Balance: The outstanding balance on the account
  * Look for "Current Balance", "Account Balance"
  * This is typically the amount currently owed
- Balance After Due Date: The balance including late fees if paid after due date

METER INFORMATION (CRITICAL):
**IMPORTANT**: Extract detailed meter data for each service
- Kent bills may have one or more meters for different services
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

SPECIAL NOTES FOR KENT UTILITY BILLS:
- Kent bills have a distinctive format with "Remit Payment To" address and Pay.KentWA.gov website
- The "Access" charge is ALWAYS a SEPARATE service - never combine it with Water
- Each distinct service type listed on the bill must have its own entry in current_charges
- Do not combine, merge, or nest services together
- Every line item in the charges section should be captured
- If the bill shows 4 separate charges, your JSON must show 4 separate entries in current_charges
- The validation will sum up all service amounts - missing even one service will cause a mismatch

"""

KENT_UTILITY_JSON_FORMAT = """

{
  "provider_name": "Kent Utility",
  "provider_website": "website_url_or_null",
  "provider_customer_service_phone": "phone_number_or_null",
  "provider_customer_service_email": "email_address_or_null",
  "provider_address": "provider_physical_address_or_null",
  "provider_return_address": "payment_return_address_or_null",
  "account_number": "account_number_from_bill",
  "account_type": "Water & Sewer",
  "bill_number": "bill_or_statement_number_or_null",
  "bill_type": "bill_type_like_Regular_Final_Estimated_or_null",
  "customer_name": "customer_name_from_bill",
  "service_address": "service_address_from_bill",
  "billing_address": "billing_address_from_bill",
  "previous_balance": "previous_balance_amount",
  "current_billing": "current_billing_amount",
  "current_adjustments": "total_adjustments_amount",
  "total_amount_due": "total_due_amount",
  "total_amount_due_date": "due_date",
  "bill_date": "bill_date",
  "number_of_days": "number_of_days_in_billing_period",
  "service_days": "numeric_days_same_as_number_of_days_or_null",
  "balance": "current_outstanding_balance_or_null",
  
  "payments_applied": [
    {
      "payment_date": "date_of_payment",
      "payment_amount": "amount_paid"
    }
  ],
  
  "adjustments": [
    {
      "category": "adjustment_category_as_shown",
      "amount": "adjustment_amount"
    }
  ],
  
  "taxes": {
    "per_service_taxes": [
      {
        "service_name": "service_type_name",
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
  ],
  
  // Kent Utility specific fields
  "remit_payment_to": "payment_mailing_address_as_shown_on_bill",
  
  "payment_website": "payment_website_url_exactly_as_shown",

  "previous_amount_due": "previous_amount_due_from_bill_summary",

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

  "current_usage": {
    "previous_reading": "483",
    "current_reading": "508",
    "usage": "25",
    "uom": "CCF"
  }
  
  "account_info": {
    "account_number": "account_number",
    "customer_name": "customer_name",
    "service_address": "service_address"
  },
  
  "bill_details": {
    "bill_date": "billing_date",
    "due_date": "payment_due_date"
  },
  
  "current_charges": [
    {
      "type": "Water",
      "amount": "dollar_amount"
    },
    {
      "type": "Sewer",
      "amount": "dollar_amount"
    },
    {
      "type": "Access",
      "amount": "dollar_amount"
    },
    {
      "type": "Technology Fee",
      "amount": "dollar_amount"
    },
    {
      "type": "any_other_service_from_bill",
      "amount": "dollar_amount"
    }
  ],
  
  "totals": {
    "total_current_charges": "total_charges_amount",
    "total_due": "total_amount_due"
  }
}

"""

KENT_UTILITY_PROMPT = f"""{BASE_EXTRACTION_FIELDS}

{KENT_UTILITY_SPECIFIC_INSTRUCTIONS}

{KENT_UTILITY_JSON_FORMAT}
"""
