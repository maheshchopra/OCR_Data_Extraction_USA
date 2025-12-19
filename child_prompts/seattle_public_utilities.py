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

SEATTLE_PUBLIC_UTILITIES_SPECIFIC_INSTRUCTIONS = """

SEATTLE PUBLIC UTILITIES SPECIFIC INSTRUCTIONS:

This template applies to bills with "Seattle Public Utilities" or "SPU" text.

SECTION 1 - CONTACT INFORMATION:
**CRITICAL**: Extract Seattle Public Utilities contact information
- Website: Look for the SPU website
  * Common format: "seattle.gov/utilities" or similar
  * Extract complete URL or domain as shown
- Phone Number: Look for customer service phone number
  * Common format: "(206) XXX-XXXX"
  * Usually in header, footer, or contact section
  * Extract exactly as shown
- Email: Look for customer service email address
  * Common format: "customerservice@seattle.gov" or similar SPU email
  * Extract complete email address

SECTION 2 - LATE PAYMENT FEE:
**CRITICAL**: Look for late payment fee or penalty information
- Percentage: Extract the late payment fee percentage rate
  * Look for terms like "late payment fee", "late charge", "penalty", "interest"
  * Common format: "1%", "1.5%", "1 percent"
  * Usually in payment terms or notice section
- Description: Extract complete late payment policy text if available

SECTION 3 - CONSUMPTION INFORMATION:
**CRITICAL**: Extract water consumption data
- CCF (Hundred Cubic Feet): Total water consumption in CCF
  * Look for consumption values in CCF units
  * May be shown in meter reading sections or usage summary
- Gallons: Total water consumption in gallons
  * Look for gallon equivalents
  * May be calculated from CCF
- CCF to Gallons Conversion Rate: The conversion factor used
  * Look for text like "1 CCF = XXX gallons" or "748 gallons per CCF"
  * Common standard: 1 CCF = 748 gallons
  * Extract the exact conversion rate shown on the bill

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
- Number of Days: Billing period length

SECTION 6 - SERVICES:
- Seattle Public Utilities typically provides Water, Sewer, and Solid Waste services
- Each service has its own charges and line items
- Extract meter numbers, readings, and CCF usage for water service
- Extract all line item charges with categories and amounts

**WATER SERVICE TABLES (CRITICAL)**
- Water Service shows a header row with: Service From, Service Through, CCF Usage, Previous Reading, Current Reading (and sometimes Multiplier, Rate Code).
- Immediately under each header row are the charge line items (e.g., Base service charge, Winter Commercial, Summer Commercial).
- For each header row block:
  - Copy the header values (Service From, Service Through, CCF Usage, Previous Reading, Current Reading, Multiplier, Rate Code) into EVERY line item charge that belongs to that block.
  - meter_number: use the meter number shown next to the header (e.g., PRE-P0029155-1, HER-09015946-1).
  - service_category: extract the service category classification if shown on the bill (e.g., "Commercial", "Residential", "Multi-Family", or any service category label that appears in the bill for that meter/header block). Look for service category information near the meter number, in the header section, or in the service description area. If not present, use null.
  - usage: CCF Usage from the header row (e.g., 80.00).
  - uom: "CCF".
  - previous_reading/current_reading: from the header row (e.g., 9569.00 / 9649.00).
  - usage_multiplier: from header if shown, else "1.00".
  - service_from_date / service_to_date: from the header row (e.g., Nov 06, 2025 to Dec 04, 2025).
- Do NOT leave usage, uom, previous_reading, current_reading null for these water line items; populate them from the associated header row.

CRITICAL: HOW TO EXTRACT SERVICE TYPE LINE ITEM CHARGES (category vs description)

1) GENERAL RULES FOR LINE ITEM CHARGES
- For each service type (e.g., "Water Service", "Sewer Service", "Solid Waste Service"), the bill lists line items under that service.
- Each **line item charge** must appear in `service_types[n].line_item_charges` as a separate object.
- A **category** is the main charge name exactly as it appears on the bill for that specific charge line.
- A **description** is optional and is only for additional explanatory text that does NOT itself represent a separate billable category.

2) LINES WITH AMOUNTS
- When a line under a service ends with a dollar amount, treat that entire line as **one line item charge**.
- The text **up to** the first quantity/rate/usage (like `75.00`, `CCF`, `@`, `$7.60`, `1X Weekly`) is the `category`.
- The usage and rate information (`75.00 CCF @ $7.60 per CCF`, etc.) should go into:
  - `usage`
  - `uom`
  - `rate`
- Do NOT move another category name into the `description` field just because it is on a neighboring line.

EXAMPLE – WATER SERVICE:
Bill text (under "Water Service"):
- "Base service charge 38.60"
- "Summer Commercial 75.00 CCF @ $7.60 per CCF 570.00"

Correct JSON mapping:
- First line item:
  - category: "Base service charge"
  - description: null
  - amount: "38.60"
  - usage: null
  - uom: null
  - rate: null
- Second line item:
  - category: "Summer Commercial"
  - description: null
  - usage: "75.00"
  - uom: "CCF"
  - rate: "$7.60 per CCF"
  - amount: "570.00"

INCORRECT MAPPING (DO NOT DO THIS):
- Do NOT set:
  - category: "Base service charge"
  - description: "Summer Commercial"
  - amount: "38.60"
  - usage: "75.00"
  - uom: "CCF"
  - rate: "$7.60 per CCF"

In other words: "Summer Commercial" is its **own** category with its **own** amount and should be a separate entry in `line_item_charges`.

3) SEWER SERVICE EXAMPLE
Bill text (under "Sewer Service"):
- "Commercial Service 75.00 CCF @ $19.21 per CCF 1,440.75"

Correct JSON mapping:
- category: "Commercial Service"
- description: null
- usage: "75.00"
- uom: "CCF"
- rate: "$19.21 per CCF"
- amount: "1440.75"

4) SOLID WASTE SERVICE EXAMPLE AND CATEGORY-ONLY LINES
Bill text (under "Solid Waste Service"):
- "5-Garbage 90 Gal 1X Weekly 675.25"
- "5-Garbage 90 Gal 1X Weekly 270.25"
- "Backyard Pick-up"
- "7-Recycle 90 Gal 1X Weekly 0.00"
- "1-Food/Yard Waste/Liner 90 Gal 14.30"
- "1X Weekly"
- "2025 1-Food/Yard Waste/Liner 90 Gal 80.95"
- "1X Weekly Onsite Pick-up"

Rules:
- Lines that **end with an amount** (e.g., "675.25", "270.25", "0.00", "14.30", "80.95") are **line item charges**.
- For those, the category is the charge label text, not the frequency or pickup text.
- Frequency or pickup text like "1X Weekly", "Backyard Pick-up", "1X Weekly Onsite Pick-up" is **additional description** unless it clearly appears together with the amount on the same line.

Examples:
- "5-Garbage 90 Gal 1X Weekly 675.25"
  - category: "5-Garbage 90 Gal 1X Weekly"
  - description: "Backyard Pick-up" (if this appears as a standalone line right after and is clearly describing this charge)
  - amount: "675.25"
- "5-Garbage 90 Gal 1X Weekly 270.25"
  - category: "5-Garbage 90 Gal 1X Weekly"
  - description: "Backyard Pick-up"
  - amount: "270.25"
- "7-Recycle 90 Gal 1X Weekly 0.00"
  - category: "7-Recycle 90 Gal 1X Weekly"
  - description: "1X Weekly Onsite Pick-up" (if present and clearly describing this line)
  - amount: "0.00"
- "1-Food/Yard Waste/Liner 90 Gal 14.30"
  - category: "1-Food/Yard Waste/Liner 90 Gal"
  - description: "1X Weekly" (if present and clearly describing this line)
  - amount: "14.30"
- "2025 1-Food/Yard Waste/Liner 90 Gal 80.95"
  - category: "1-Food/Yard Waste/Liner 90 Gal"
  - description: "1X Weekly Onsite Pick-up" (if present and clearly describing this line)
  - amount: "80.95"

5) CATEGORY-ONLY LINES (NO AMOUNT)
- Sometimes a category or descriptor appears **without** an amount (e.g., "Backyard Pick-up", "1X Weekly", "1X Weekly Onsite Pick-up").
- These lines:
  - MUST NOT be treated as the main category for a different line’s amount.
  - Are supplemental descriptors:
    - If they clearly modify the immediately preceding line item, put them into that line item’s `description`.
    - If they represent a separate service or sub-category but no amount is shown for them on the bill, you may:
      - Either leave them out of `line_item_charges` (preferred), OR
      - Represent them as a line item with `amount`: "0.00" and `description`: null, but only if that reflects the bill layout.
- Never move a category name that has its own dollar amount into `description` of another line item.

6) SUMMARY OF CATEGORY VS DESCRIPTION FOR SEATTLE PUBLIC UTILITIES
- category: The charge label as printed near its own amount on the bill line (e.g., "Base service charge", "Summer Commercial", "Commercial Service", "5-Garbage 90 Gal 1X Weekly", "7-Recycle 90 Gal 1X Weekly", "1-Food/Yard Waste/Liner 90 Gal").
- description: Only additional explanatory text that does not itself introduce a separate billable charge with its own amount (e.g., "Backyard Pick-up", "1X Weekly", "1X Weekly Onsite Pick-up") and is clearly modifying a specific line item.

SPECIAL NOTES FOR SEATTLE PUBLIC UTILITIES BILLS:
- SPU bills have a distinctive Seattle city government format
- Water consumption is measured in CCF (hundred cubic feet)
- 1 CCF typically equals 748 gallons (verify on the bill)
- Services are clearly separated: Water, Sewer, Solid Waste
- Contact information is usually prominently displayed
- Late payment fee information may be in fine print or payment instructions

"""

SEATTLE_PUBLIC_UTILITIES_JSON_FORMAT = """

Return in this exact JSON format for Seattle Public Utilities bills:
{
  "provider_name": "Seattle Public Utilities",
  "provider_website": "website_url_or_null",
  "provider_customer_service_phone": "phone_number_or_null",
  "provider_customer_service_email": "email_address_or_null",
  "provider_address": "provider_physical_address_or_null",
  "provider_return_address": "provider_return_address_or_null",
  "account_number": "numeric_account_number",
  "account_type": "Water & Sewer & Solid Waste",
  "bill_number": "bill_or_statement_number_or_null",
  "bill_type": "bill_type_like_Regular_Final_Estimated_or_null",
  "customer_name": "customer_name_as_shown",
  "service_address": "customer_physical_service_address",
  "billing_address": "customer_mailing_billing_address",
  "bill_date": "date_format_like_July_22_2025",
  "total_amount_due_date": "date_format_like_August_12_2025",
  "number_of_days": "numeric_days_in_billing_period",
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
  
  "contact_info": {
    "website": "website_like_seattle.gov/utilities",
    "phone_number": "phone_like_(206)_XXX-XXXX",
    "email": "email_like_customerservice@seattle.gov"
  },
  
  "late_payment_fee": {
    "percentage": "percentage_like_1%_or_null",
    "description": "late_payment_policy_description_or_null"
  },

  "late_fee_info": {
    "latefee_applied": "yes_or_no_or_null",
    "latefee_date": "date_when_late_fee_was_applied_or_null",
    "latefee_amount": "dollar_amount_of_late_fee_or_null",
    "latefee_by_duedate_percentage": "percentage_like_1%_or_null",
    "latefee_by_duedate": "dollar_amount_of_late_fee_if_late_or_null",
    "total_amount_with_latefee_by_duedate": "total_including_late_fees_or_null"
  },
  
  "consumption": {
  "ccf": {
    "usage": "numeric_value_like_75.00",
    "uom": "CCF"
  },
  "gallons": {
    "usage": "numeric_value_like_56100",
    "uom": "gallons"
  },
  "ccf_to_gallons_conversion": "conversion_rate_like_1_CCF_equals_748_gallons"
  },
  
  "service_types": [
    {
      "service_name": "service_name_like_Water_Service",
      "current_service": "total_dollar_amount_for_this_service",
      "service_from_date": "date_format_like_June_15_2025",
      "service_to_date": "date_format_like_July_16_2025",
      "previous_reading": "meter_reading_at_start_or_null",
      "current_reading": "meter_reading_at_end_or_null",
      "line_item_charges": [
        {
          "category": "charge_description_like_Base_service_charge",
          "description": "detailed_charge_description_or_null",
          "amount": "dollar_amount",
          "rate": "rate_per_unit_or_null",
          "meter_number": "meter_id_or_null",
          "service_category": "service_category_classification_or_null",
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
        "service_name": "service_name_like_Water_Service",
        "tax_name": "tax_type_like_City_taxes",
        "tax_rate": "percentage_like_15.5%",
        "tax_amount": "dollar_amount_or_null"
      }
    ],
    "global_taxes": []
  }
}

"""

SEATTLE_PUBLIC_UTILITIES_PROMPT = f"""{BASE_EXTRACTION_FIELDS}

{SEATTLE_PUBLIC_UTILITIES_SPECIFIC_INSTRUCTIONS}

{SEATTLE_PUBLIC_UTILITIES_JSON_FORMAT}
"""
