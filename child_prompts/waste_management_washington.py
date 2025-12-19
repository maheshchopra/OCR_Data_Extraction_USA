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

WASTE_MANAGEMENT_SPECIFIC_INSTRUCTIONS = """

WASTE MANAGEMENT OF WASHINGTON SPECIFIC INSTRUCTIONS:

This template applies to bills with "Waste Management" or "WM" text.

SECTION 1 - SERVICE PERIOD:
Extract the service period date range
- Look for service period or billing period dates
- Format is typically: "07/01/25-07/31/25" or similar date range
- Extract exactly as shown on the bill
- This may be shown near the top of the bill or in the service details section

SECTION 2 - CONTACT INFORMATION:
Extract Waste Management contact information
- Website: Look for the WM website
  * Common format: "wm.com" or "wm.com/customer-service"
  * Extract complete URL or domain as shown
- Phone Number: Look for customer service phone number
  * Common format: "(XXX) XXX-XXXX" or "1-800-XXX-XXXX"
  * Usually in header, footer, or contact section
  * Extract exactly as shown

SECTION 3 - LATE PAYMENT FEE:
Look for late payment fee or penalty information
- Percentage: Extract the late payment fee percentage rate
  * Look for terms like "late payment fee", "late charge", "penalty", "interest", "finance charge"
  * Common format: "1.5%", "1%", "1.5 percent per month"
  * Usually in payment terms, fine print, or notice section
- Description: Extract complete late payment policy text if available

SECTION 4 - ACCOUNT AND BILLING:
- Account Number: Unique account identifier
- Customer Name: Account holder name
- Service Address: Physical location where services are provided
- Billing Address: Mailing address for billing

SECTION 5 - BILL DETAILS:
- Bill Date: Date the bill was issued
- Due Date: Payment due date
- Previous Balance: Balance from previous bill
- Current Billing: Current period charges
- Total Amount Due: Final amount due

SECTION 6 - SERVICES AND CHARGES:
- Extract all service line items with descriptions and amounts
- Common services include:
  * Container services (dumpster rentals, pickups)
  * Administrative fees
  * Environmental fees
  * Gate fees
  * Rebates or credits (may be negative amounts)
  * Refuse taxes (may be listed as a service charge)
- Include service dates where applicable

SECTION 7 - TAXES:
Extract ALL taxes separately from service charges
- Common taxes include:
  * Utility Tax
  * Sales Tax
  * Refuse Tax (if listed separately from service charges)
  * Municipal taxes
- Extract tax name, rate (percentage), and amount
- Taxes may be shown in a separate tax summary section
- Some taxes may be per-service, others may be global

SPECIAL NOTES FOR WASTE MANAGEMENT BILLS:
- Waste Management bills have distinctive WM branding
- Service period is typically shown as a date range (MM/DD/YY-MM/DD/YY)
- Taxes are often listed separately and must be included in total billing calculations
- Some charges like "Refuse Tax" may appear as service charges
- Rebates or credits are shown as negative amounts
- Contact information is usually in footer or header section

"""

WASTE_MANAGEMENT_JSON_FORMAT = """

Return in this exact JSON format for Waste Management bills:
{
  "provider_name": "Waste Management of Washington",
  "provider_website": "website_url_or_null",
  "provider_customer_service_phone": "phone_number_or_null",
  "provider_customer_service_email": "email_address_or_null",
  "provider_address": "provider_physical_address_or_null",
  "provider_return_address": "provider_return_address_or_null",
  "account_number": "numeric_account_number",
  "account_type": "Waste Management",
  "bill_number": "bill_or_statement_number_or_null",
  "bill_type": "bill_type_like_Regular_Final_Estimated_or_null",
  "customer_name": "customer_name_as_shown",
  "service_address": "customer_physical_service_address",
  "billing_address": "customer_mailing_billing_address",
  "bill_date": "date_format_like_August_01_2025",
  "total_amount_due_date": "date_format_like_August_31_2025",
  "number_of_days": "numeric_days_or_null",
  "service_days": "numeric_days_same_as_number_of_days_or_null",
  "previous_balance": "dollar_amount_or_null",
  "current_billing": "dollar_amount_for_current_period",
  "current_adjustments": "dollar_amount_or_null",
  "total_amount_due": "final_dollar_amount_due",
  "balance": "current_outstanding_balance_or_null",
  
  "payment_information": {
    "payment_date": "date_format_like_July_15_2025_or_null",
    "payment_amount": "dollar_amount_or_null"
  },
  
  "payments_applied": [
    {
      "payment_date": "date_format_like_July_15_2025",
      "payment_amount": "dollar_amount"
    }
  ],
  
  "adjustments": [
    {
      "category": "adjustment_category_description",
      "amount": "dollar_amount_with_sign"
    }
  ],
  
  "service_period": "service_period_like_07/01/25-07/31/25",
  
  "contact_info": {
    "website": "website_like_wm.com",
    "phone_number": "phone_like_(XXX)_XXX-XXXX_or_1-800-XXX-XXXX"
  },
  
  "late_payment_fee": {
    "percentage": "percentage_like_1.5%_or_null",
    "description": "late_payment_policy_description_or_null"
  },
  
  "late_fee_info": {
    "latefee_applied": "yes_or_no_or_null",
    "latefee_date": "date_when_late_fee_was_applied_or_null",
    "latefee_amount": "dollar_amount_of_late_fee_or_null",
    "latefee_by_duedate_percentage": "percentage_like_1.5%_or_null",
    "latefee_by_duedate": "dollar_amount_of_late_fee_if_late_or_null",
    "total_amount_with_latefee_by_duedate": "total_including_late_fees_or_null"
  },
  
  "service_types": [
    {
      "service_name": "service_name_like_Administrative_Fee",
      "current_service": "dollar_amount",
      "service_from_date": "date_format_like_July_01_2025_or_null",
      "service_to_date": "date_format_like_July_31_2025_or_null",
      "previous_reading": null,
      "current_reading": null,
      "line_item_charges": [
        {
          "category": "detailed_charge_description",
          "description": "detailed_charge_description",
          "rate": "rate_per_unit_or_null",
          "amount": "dollar_amount",
          "meter_number": null,
          "usage": null,
          "uom": null,
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
    "per_service_taxes": [
      {
        "service_name": "service_name_if_applicable",
        "tax_name": "tax_type_like_Utility_Tax",
        "tax_rate": "percentage_like_6.38%",
        "tax_amount": "dollar_amount"
      }
    ],
    "global_taxes": [
      {
        "tax_name": "tax_type_like_Sales_Tax",
        "tax_rate": "percentage_like_10.6%",
        "tax_amount": "dollar_amount"
      }
    ]
  }
}

"""

WASTE_MANAGEMENT_PROMPT = f"""{BASE_EXTRACTION_FIELDS}

{WASTE_MANAGEMENT_SPECIFIC_INSTRUCTIONS}

{WASTE_MANAGEMENT_JSON_FORMAT}
"""
