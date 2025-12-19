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

REPUBLIC_SERVICES_SPECIFIC_INSTRUCTIONS = """

REPUBLIC SERVICES SPECIFIC INSTRUCTIONS:

This template applies to bills with "Republic Services" text.

SECTION 1 - COMPANY ADDRESS:
**CRITICAL**: Extract Republic Services company address
- Look for the company address (typically in header or company information section)
- Format example: "1600 127th Avenue NE, Bellevue WA 98005-213636"
- Extract complete address including street, city, state, zip
- This is different from service_address (customer's location)

SECTION 2 - ACCOUNT INFORMATION:
- Account Number: Unique account identifier
- Customer Name: Account holder name
- Service Address: Physical location where waste services are provided
- Billing Address: Mailing address for billing

SECTION 3 - BILL DETAILS:
- Bill Date: Date the bill was issued
- Due Date: Payment due date
- Previous Balance: Balance from previous bill
- Current Billing: Current period charges
- Total Amount Due: Final amount due

SECTION 4 - CONTACT INFORMATION:
**CRITICAL**: Extract Republic Services contact information
- Customer Service Phone: Look for phone number format like "(206) 682-3037"
  * Common location: contact section, header, or footer
  * Extract exactly as shown
- Customer Service Website: Look for support website
  * Format example: "RepublicServices.com/Support"
  * May appear with or without "https://" or "www."
  * Extract the complete URL/domain

SECTION 5 - PAYMENT WEBSITE:
**CRITICAL**: Extract the online bill payment website
- Look for "Pay Online" or "MyBill" website
- Format example: "RepublicServices.com/MyBill"
- This is different from the support website
- Extract exactly as shown on the bill

SECTION 6 - LATE FEE INFORMATION:
**CRITICAL**: Look for late payment fee or penalty information
- Percentage: Extract the late fee percentage rate
  * Look for terms like "late fee", "late charge", "penalty", "interest"
  * Common format: "1.5%", "2%", "1.5 percent per month"
  * Usually in payment terms or fine print section
- Description: Extract complete late fee policy text if available

SECTION 7 - SERVICE CHARGES:
**CRITICAL**: Extract ALL line items from the "CURRENT INVOICE CHARGES" section
- Look for the table with columns: Description, Reference, Quantity, Unit Price, Amount
- Extract EVERY row that has an amount in the "Amount" column
- Include ALL line items, whether positive or negative:
  * Value Of Recyclables Sold (if present, will be negative)
  * Pull-Out Charge entries (can be positive or negative)
  * Pickup Service entries (can be positive or negative)
  * Rental entries (can be positive or negative)
  * ALL tax entries (Total City Utility Tax, Total City Sales Tax, etc.)
- For each line item:
  * category: Use the EXACT text from the "Description" column (e.g., "Value Of Recyclables Sold 10/31", "Pull-Out Charge 10/25-10/31")
  * amount: Extract the EXACT amount from the "Amount" column, including the negative sign if present (e.g., "-$4.44", "-$2.16", "-$78.99", "-$3.66")
  * Preserve negative signs - they represent credits/adjustments
- DO NOT include header text like "1 Waste Container 4 Cu Yd, 1 Lift Per Week Multi-Family" as a line item - this is just descriptive text
- The sum of ALL line item amounts (including taxes) should equal the "CURRENT INVOICE CHARGES" total
- Extract service period dates (from/to dates) if shown

SECTION 8 - TAXES:
- Extract all taxes from the "Amount" column in the charges table
- These should also be included in line_item_charges (see SECTION 7)
- Additionally extract them in the taxes section for reference:
  * Total City Utility Tax
  * Total City Sales Tax
  * Total State Sales Tax
  * Total State Refuse Tax
- Include tax name and amount (rate if shown)

SPECIAL NOTES FOR REPUBLIC SERVICES BILLS:
- Republic Services bills have distinct company branding
- Contact information typically in header or footer
- Service charges may be itemized with container sizes and pickup frequency
- Payment websites are usually prominently displayed
- Late fee information may be in fine print or payment instructions

"""

REPUBLIC_SERVICES_JSON_FORMAT = """

Return in this exact JSON format for Republic Services bills:
{
  "provider_name": "Republic Services",
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
  "bill_date": "date_format_like_May_31_2025",
  "total_amount_due_date": "date_format_like_June_18_2025",
  "number_of_days": "numeric_days_or_null",
  "service_days": "numeric_days_same_as_number_of_days_or_null",
  "previous_balance": "dollar_amount_or_null",
  "current_billing": "dollar_amount_for_current_period",
  "total_amount_due": "final_dollar_amount_due",
  "balance": "current_outstanding_balance_or_null",
  
  "payments_applied": [
    {
      "payment_date": "date_format_like_May_19_2025",
      "payment_amount": "dollar_amount"
    }
  ],
  
  "company_address": "company_address_like_1600_127th_Avenue_NE_Bellevue_WA_98005",
  
  "contact_info": {
    "phone_number": "phone_like_(206)_682-3037",
    "support_website": "website_like_RepublicServices.com/Support"
  },
  
  "payment_website": "website_like_RepublicServices.com/MyBill",
  
  "late_fee": {
    "percentage": "percentage_like_1.5%_or_null",
    "description": "late_fee_policy_description_or_null"
  },

  "late_fee_info": {
    "latefee_applied": "yes_or_no_or_null",
    "latefee_date": "date_when_late_fee_was_applied_or_null",
    "latefee_amount": "dollar_amount_of_late_fee_or_null",
    "latefee_by_duedate_percentage": "percentage_like_1.5%_or_null",
    "latefee_by_duedate": "dollar_amount_of_late_fee_if_late_or_null",
    "total_amount_with_latefee_by_duedate": "total_including_late_fees_or_null"
  },
  
  "taxes": {
    "per_service_taxes": [
      {
        "service_name": "service_name",
        "tax_name": "tax_type_name",
        "tax_rate": "percentage_or_null",
        "tax_amount": "dollar_amount"
      }
    ],
    "global_taxes": [
      {
        "tax_name": "tax_type_name_like_City_Utility_Tax",
        "tax_rate": "percentage_or_null",
        "tax_amount": "dollar_amount"
      }
    ]
  },
  
  "service_types": [
    {
      "service_name": "service_name_like_Waste_Container",
      "current_service": "total_dollar_amount_for_this_service",
      "service_from_date": "date_format_like_May_1_2025",
      "service_to_date": "date_format_like_May_31_2025",
      "previous_reading": null,
      "current_reading": null,
      "line_item_charges": [
        {
          "category": "exact_description_from_bill_like_Value_Of_Recyclables_Sold_10/31",
          "description": null,
          "rate": null,
          "amount": "dollar_amount_with_sign_like_-$4.44_or_$9.40",
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
  ]
}

CRITICAL INSTRUCTIONS:
- Extract provider website, customer service phone, and email (top level fields)
- Extract provider address and return address (top level fields)
- Extract bill number and bill type
- Extract balance (current outstanding balance, different from previous_balance)
- Extract service_days (same as number_of_days typically)
- Extract company address (Republic Services location, NOT customer address)
- Extract contact info: phone number and support website
- Extract payment website (RepublicServices.com/MyBill or similar)
- Extract late fee information in both late_fee and late_fee_info sections:
  * late_fee: percentage and description
  * late_fee_info: latefee_applied, latefee_date, latefee_amount, latefee_by_duedate_percentage, latefee_by_duedate, total_amount_with_latefee_by_duedate
- Include ALL base fields (account_number, customer_name, etc.)
- Extract all service charges with detailed descriptions
- In line_item_charges, include: category, description, rate, amount, and all meter-related fields (even if null)
- Extract all taxes (both per-service and global)
- If any field info not found, use null values

"""

REPUBLIC_SERVICES_PROMPT = f"""{BASE_EXTRACTION_FIELDS}

{REPUBLIC_SERVICES_SPECIFIC_INSTRUCTIONS}

{REPUBLIC_SERVICES_JSON_FORMAT}
"""
