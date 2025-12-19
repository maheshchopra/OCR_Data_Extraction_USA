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
    - Look for "Payments Applied", "Payment Received", "Payment History", "PAYMENT LOCKBOX"
    - Extract EACH payment separately with date and amount
    - Include all payments shown on the bill
    - Payments may appear as negative amounts in the line items table
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

RUBATINO_REFUSE_REMOVAL_SPECIFIC_INSTRUCTIONS = """

RUBATINO REFUSE REMOVAL SPECIFIC INSTRUCTIONS:

This template applies to bills with "Rubatino" text in the bill.

SECTION 1 - PROVIDER INFORMATION:
- Provider Name: "Rubatino Refuse Removal"
- Extract provider website, customer service phone, email, address, and remit address.

SECTION 2 - ACCOUNT INFORMATION:
- Account number, account type (Waste Management), bill number/type, customer name, service and billing addresses.

SECTION 3 - BILL DETAILS:
- Bill date, total amount due date, number of days, service days.

SECTION 4 - BILLING SUMMARY:
- Previous balance, current billing, current adjustments, total amount due, balance.
- Look for "PRIOR BALANCE" line in the table - this is the previous balance.

SECTION 5 - PAYMENT INFORMATION:
- payment_information object plus payments_applied array with all payments.
- Payments appear in the line items table with descriptions like "PAYMENT LOCKBOX" and negative amounts.
- Extract the date from the Date column and the amount from the Total column (which will be negative).

SECTION 6 - SERVICE CHARGES:
The bill uses a table format with columns: Date, Invoice #, Description, Quantity, Rate, Total.
- Extract each service line item from the table:
  * Date: Service date from the Date column
  * Description: Service description from the Description column
  * Quantity: Number of units from the Quantity column
  * Rate: Rate per unit from the Rate column
  * Total: Total amount from the Total column
- For line_item_charges:
  * category: Use the Description from the table
  * description: Same as category or more detailed if available
  * rate: Rate per unit from the Rate column
  * amount: Total amount from the Total column (this is the total for that line, NOT the rate)
  * usage: Quantity from the Quantity column
  * uom: Unit of measure if shown (e.g., "Unit", "Cart", "Dumpster")
- Group services by service type/description.
- DO NOT include payment entries (PAYMENT LOCKBOX) as services - these go in payments_applied.
- DO NOT include tax entries (CITY TAX, REFUSE TAX) as services - these go in taxes.
- DO NOT include PRIOR BALANCE as a service - this goes in previous_balance.

SECTION 7 - TAXES:
- Extract ALL tax entries from the table that have descriptions like "CITY TAX", "REFUSE TAX", etc.
- CRITICAL: Extract EVERY tax entry as a separate line item, even if multiple entries have the same tax name.
  * Example: If there are 3 "CITY TAX 6%" entries with amounts $1.77, $29.00, and $0.00, extract ALL THREE separately.
  * Do NOT combine or deduplicate tax entries - each row in the table is a separate tax entry.
- Extract tax name, rate (percentage shown in description like "CITY TAX 6%"), and amount (from Total column).
- These are typically global taxes applied to the entire bill.
- The tax name should include the percentage if shown (e.g., "CITY TAX 6%" not just "CITY TAX").

SECTION 8 - ADJUSTMENTS:
- Capture each adjustment with category and signed amount if present.

SPECIAL NOTES FOR RUBATINO REFUSE REMOVAL BILLS:
- Bills use a table format with Date, Invoice #, Description, Quantity, Rate, Total columns
- PRIOR BALANCE appears as a line item in the table
- Payments appear as negative amounts in the table
- Service charges have quantity, rate, and total columns
- Taxes are separate line items in the table with percentage rates in the description
- IMPORTANT: Extract EVERY tax entry from the table, even if there are multiple entries with the same tax name
- Each row in the table is a separate entry - do NOT combine or deduplicate entries
- The sum of all service charges plus ALL taxes should equal the PRIOR BALANCE amount

"""

RUBATINO_REFUSE_REMOVAL_JSON_FORMAT = """

Return in this exact JSON format for Rubatino Refuse Removal bills:
{
  "provider_name": "Rubatino Refuse Removal",
  "provider_website": "website_url_or_null",
  "provider_customer_service_phone": "phone_number_or_null",
  "provider_customer_service_email": "email_address_or_null",
  "provider_address": "complete_provider_address_or_null",
  "provider_return_address": "payment_return_address_or_null",
  "account_number": "numeric_digits_only_or_null",
  "account_type": "Waste Management",
  "bill_number": "bill_or_statement_number_or_null",
  "bill_type": "bill_type_like_Regular_Final_Estimated_or_null",
  "customer_name": "customer_name_or_null",
  "service_address": "service_address_or_null",
  "billing_address": "billing_address_or_null",
  "bill_date": "date_format_like_November_30_2025_or_null",
  "total_amount_due_date": "date_format_like_December_31_2025_or_null",
  "number_of_days": "numeric_days_or_null",
  "service_days": "numeric_days_same_as_number_of_days_or_null",
  "previous_balance": "dollar_amount_from_PRIOR_BALANCE_line_or_null",
  "current_billing": "dollar_amount_for_current_period",
  "current_adjustments": "dollar_amount_or_null",
  "total_amount_due": "final_dollar_amount_due",
  "balance": "current_outstanding_balance_or_null",
  
  "payment_information": {
    "payment_date": "date_format_like_November_28_2025_or_null",
    "payment_amount": "dollar_amount_or_null"
  },
  
  "payments_applied": [
    {
      "payment_date": "date_format_like_November_28_2025",
      "payment_amount": "dollar_amount_positive_value"
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
    "latefee_by_duedate_percentage": "percentage_like_1%_or_null",
    "latefee_by_duedate": "dollar_amount_of_late_fee_if_late_or_null",
    "total_amount_with_latefee_by_duedate": "total_including_late_fees_or_null"
  },
  
  "meters": [],
  
  "service_types": [
    {
      "service_name": "service_name_from_description_column",
      "current_service": "dollar_amount_sum_of_line_items_for_this_service",
      "service_from_date": "date_format_like_November_30_2025_or_null",
      "service_to_date": "date_format_like_November_30_2025_or_null",
      "previous_reading": null,
      "current_reading": null,
      "line_item_charges": [
        {
          "category": "description_from_table",
          "description": "description_from_table",
          "rate": "rate_per_unit_from_Rate_column",
          "amount": "total_amount_from_Total_column",
          "meter_number": null,
          "usage": "quantity_from_Quantity_column",
          "uom": "unit_of_measure_if_shown_or_null",
          "previous_reading": null,
          "previous_reading_type": null,
          "current_reading": null,
          "current_reading_type": null,
          "usage_multiplier": null
        }
      ]
    }
  ],
  
  "taxes": {
    "per_service_taxes": [],
    "global_taxes": [
      {
        "tax_name": "tax_type_like_CITY_TAX_or_REFUSE_TAX",
        "tax_rate": "percentage_like_6%_or_3.6%",
        "tax_amount": "dollar_amount_from_Total_column"
      }
    ]
  }
}

"""

RUBATINO_REFUSE_REMOVAL_PROMPT = f"""{BASE_EXTRACTION_FIELDS}

{RUBATINO_REFUSE_REMOVAL_SPECIFIC_INSTRUCTIONS}

{RUBATINO_REFUSE_REMOVAL_JSON_FORMAT}
"""


