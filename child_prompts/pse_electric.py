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

PSE_ELECTRIC_SPECIFIC_INSTRUCTIONS = """

PUGET SOUND ENERGY (PSE) ELECTRIC BILL SPECIFIC INSTRUCTIONS:

This template applies to bills with "Puget Sound Energy" or "PSE" text.

CRITICAL STRUCTURE:
- PSE bills organize charges BY METER NUMBER
- Each meter has its own section with meter details and associated charges
- You MUST extract ALL meters shown on the bill
- Each meter section is completely independent

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

1. Meter Number: The unique meter identifier (e.g., "P147430234")
2. Start Date: Beginning of billing period for this meter
3. Start Read: Meter reading at start of period
4. End Date: End of billing period for this meter
5. End Read: Meter reading at end of period
6. Multiplier:
   - The multiplier value shown in the Electric Detail Information table (for that meter’s row).
   - Copy this value EXACTLY as printed (for example "80", "40", "1") without changing it.
   - Validate using the formula: Kilowatt Hours (kWh) ≈ (End Read − Start Read) × Multiplier.
   - If the printed table for a meter row shows:
     - Start Read = 1352, End Read = 1366, Multiplier = 80, Kilowatt Hours (kWh) = 1,120
     then you MUST return:
     - "start_read": "1352", "end_read": "1366", "multiplier": "80", "usage": "1120".
   - Do NOT divide or adjust the multiplier (for example, do NOT change 80 to 40).
7. Kilowatt Hours (kWh): Total energy consumption for this meter as shown in the kWh column.
8. Meter Read Type: How the reading was obtained (e.g., "Actual", "Estimated", "Customer Read")

SECTION 6 - CHARGE DETAILS (BY METER):
**CRITICAL WARNING: EXTRACT EXACT VALUES, DO NOT CALCULATE**
- Always extract dollar amounts EXACTLY as printed in the "Charge" column
- DO NOT calculate amounts from rate × usage - this will give WRONG results
- The printed dollar amount in the Charge column is ALWAYS correct - use it exactly
- Even if rate × usage gives a slightly different result, use the printed amount
- Example: If Charge column shows "$13.42", extract "13.42" (not 13.40 or 13.41)
- Example: If Charge column shows "$5.40", extract "5.40" (not 5.39 or 5.41)
- READ THE CHARGE COLUMN DIGIT BY DIGIT - do not trust calculations

For each meter, extract charges from TWO separate sections:

A. MAIN CHARGES TABLE:
   The bill shows charges in columns:
   - Column 1: "Your electric charge details" (the description/category)
   - Column 2: "Rate x Unit" (the rate calculation, e.g., "3,240 kWh x $0.14760")
   - Column 3: "Charge" (the dollar amount)
   
   Extract EVERY charge line item into charge_details array:
   - Basic Charge
   - Electric Energy Charge
   - Conservation Program Charge (also called "Electric Cons. Program Charge")
   - Power Cost Adjustment
   - Energy Exchange Credit (may be negative)
   - Any other line items shown in the main table
   
   **CRITICAL EXTRACTION RULES - READ CAREFULLY**:
   
   1. DOLLAR AMOUNTS - EXTRACT EXACTLY AS SHOWN:
      - Look at the "Charge" column (Column 3) on the bill
      - COPY the dollar amount EXACTLY as printed (e.g., "23.55", "478.28", "24.69")
      - DO NOT calculate the amount from rate × usage
      - DO NOT round or adjust the amount
      - If the bill shows "$23.55", extract it as "23.55" (exactly)
      - If the bill shows "$23.54", extract it as "23.54" (exactly)
      - The printed dollar amount on the bill is ALWAYS correct - use it exactly
      
      **STEP-BY-STEP PROCESS FOR READING AMOUNTS**:
      Step 1: Locate the "Charge" column (the rightmost column with dollar amounts)
      Step 2: For each charge line, read the amount digit by digit from left to right
      Step 3: Write down each digit exactly as you see it
      Step 4: Verify the last two digits (cents) are correct - these are most commonly misread
      Step 5: Do NOT perform any calculations - only copy what you see
      
      **SPECIFIC EXAMPLES OF COMMON ERRORS TO AVOID**:
      - If the bill shows "13.42" in the Charge column, extract "13.42" 
        * WRONG: "13.40" (misreading the 2 as 0)
        * WRONG: "13.41" (misreading the 2 as 1)
        * CORRECT: "13.42" (exactly as printed)
      - If the bill shows "5.40" in the Charge column, extract "5.40"
        * WRONG: "5.39" (misreading the 0 as 9)
        * WRONG: "5.41" (misreading the 0 as 1)
        * CORRECT: "5.40" (exactly as printed)
      - If the bill shows "23.55" in the Charge column, extract "23.55"
        * WRONG: "23.54" (misreading the 5 as 4)
        * WRONG: "23.56" (misreading the 5 as 6)
        * CORRECT: "23.55" (exactly as printed)
      
      **CRITICAL: READ THE CHARGE COLUMN, NOT THE CALCULATION**:
      - The bill shows: "1,847 kWh x $0.007268" in one column and "$13.42" in the Charge column
      - You MUST extract "13.42" from the Charge column
      - DO NOT calculate 1847 × 0.007268 and use that result (which might give 13.40 or 13.41)
      - The printed "$13.42" in the Charge column is the source of truth
      
      **PAY SPECIAL ATTENTION TO THE LAST DIGIT**: 
        * If you see "13.42", extract "13.42" (not "13.40" or "13.41")
        * If you see "5.40", extract "5.40" (not "5.39" or "5.41")
        * Read the cents portion (last two digits) very carefully
        * Common OCR errors: 0 vs 2, 9 vs 0, 4 vs 1 - double-check these digits
        * Look at the shape of the digit: "2" has a curve at the bottom, "0" is a circle
        * Look at the shape of the digit: "0" is a circle, "9" has a hook at the top
      
      **VERIFY EACH AMOUNT**: Before extracting, visually confirm:
        * The tens digit (e.g., "1" in "13.42")
        * The ones digit (e.g., "3" in "13.42")
        * The decimal point
        * The tenths digit (e.g., "4" in "13.42")
        * The hundredths digit (e.g., "2" in "13.42") - THIS IS CRITICAL
        * Count the digits: "13.42" has 5 characters (1, 3, ., 4, 2) - verify all are present
      
   2. RATES - EXTRACT EXACTLY AS SHOWN:
      - Read the rate value carefully from the bill (e.g., 0.007268, not 0.007626)
      - Do NOT round or approximate rate values
      - If the bill shows "0.007268" extract it as "0.007268", not "0.007626"
      - Extract rates exactly as printed, even if they seem unusual
      
   3. VERIFICATION:
      - The rate × usage may not exactly equal the charge amount due to rounding
      - THIS IS NORMAL - always use the printed charge amount, not a calculated one
      - Example: If bill shows "1,847 kWh x $0.007268" and Charge column shows "$13.42", extract:
        * rate: "0.007268" (exactly as shown)
        * amount: "13.42" (exactly as shown in Charge column - NOT calculated)
        * Do NOT calculate 1847 × 0.007268 and use that result
      - Another example: If bill shows "1,847 kWh x $0.002921" and Charge column shows "$5.40", extract:
        * rate: "0.002921" (exactly as shown)
        * amount: "5.40" (exactly as shown in Charge column - NOT calculated)
        * Do NOT calculate 1847 × 0.002921 and use that result
      
   4. EXACT MATCHING REQUIRED:
      - Every dollar amount must match EXACTLY what is printed on the bill
      - If you see "$23.55" on the bill, extract "23.55" (not "23.54" or "23.56")
      - If you see "$13.42" on the bill, extract "13.42" (not "13.40" or "13.41")
      - If you see "$5.40" on the bill, extract "5.40" (not "5.39" or "5.41")
      - Double-check each amount against the printed bill before extracting
      - Read each amount THREE times to ensure accuracy

B. OTHER ELECTRIC CHARGES & CREDITS SECTION (SEPARATE):
   Look for a section labeled "Other Electric Charges & Credits"
   - This is a SEPARATE section from the main charges
   - Extract ALL items and put them in other_charges_and_credits array
   - **IMPORTANT**: Include items EVEN IF the charge is $0.00
   - Format is same: Description, Rate x Unit, Charge
   - **CRITICAL**: Extract the dollar amount EXACTLY as shown in the Charge column
   - Do NOT calculate amounts - use the printed value exactly
   - Common items may include:
     * Green Power Program
     * Energy Efficiency Programs
     * Renewable Energy Credits
     * Special programs or adjustments
   - If this section doesn't exist, use empty array []
   - If items show $0.00, still include them with "0.00" or "$0.00"

**IMPORTANT**: Keep these TWO arrays SEPARATE
- charge_details: Main charges from the charges table
- other_charges_and_credits: Items from "Other Electric Charges & Credits" section

SECTION 7 - TAXES (BY METER):
After the charge details, extract tax information:
- Tax Description (e.g., "State Utility Tax", "City Tax")
- Tax Rate (e.g., "3.873%", "5.517%")
- Tax Amount (dollar amount)

**CRITICAL TAX EXTRACTION RULES**:
1. If a tax shows text like "(XX.XX included in above charges)" or "(included in above charges)" or similar wording indicating the tax is already included in the subtotal:
   - Extract the tax description and rate as shown
   - Set the charge/amount to "0.00" or null (NOT a calculated amount)
   - The tax is informational only - it's already part of the subtotal
   - Example: "State Utility Tax (20.96 included in above charges) 3.873%" should have charge = "0.00"

2. If a tax shows a separate dollar amount (not included in above charges):
   - Extract the tax description, rate, and charge amount as shown
   - Example: "Effect of Bellevue City Tax 5.517% $28.29" should have charge = "28.29"

3. The "Subtotal of Electric Charges" is the sum BEFORE taxes that are separately listed
4. The "Current Electric Charges" (total) is the sum AFTER all taxes (both included and separately listed)

SECTION 8 - TOTAL CURRENT ELECTRIC CHARGES (BY METER):
- Extract the subtotal for THIS specific meter
- This is the sum of all charge details + taxes for this meter
- Label: "Total current electric charges" or "Current Electric Charges"
- This should match: Subtotal of Electric Charges + Separately Listed Taxes

SPECIAL NOTES FOR PSE BILLS:
- **CRITICAL**: Process EACH meter separately - do NOT combine meters
- If there are 2 meters, create 2 complete meter entries in meters array
- Each meter has its own charges, taxes, and total
- The sum of all meter totals should equal the total amount due
- Negative charges (credits) should be preserved with negative sign
- Extract Rate x Unit exactly as shown (includes both the calculation and units)
- Meter read type is important - look for "Actual", "Estimated", or "Customer" labels

"""

PSE_ELECTRIC_JSON_FORMAT = """

Return in this exact JSON format for PSE Electric bills:
{
  "provider_name": "Puget Sound Energy",
  "provider_website": "website_url_or_null",
  "provider_customer_service_phone": "phone_number_or_null",
  "provider_customer_service_email": "email_address_or_null",
  "provider_address": "provider_physical_address_or_null",
  "provider_return_address": "provider_return_address_or_null",
  "account_number": "numeric_account_number",
  "account_type": "Electric",
  "customer_name": "customer_name_as_shown",
  "service_address": "physical_service_address",
  "billing_address": "mailing_billing_address",
  "bill_date": "date_format_like_July_24_2025",
  "bill_number": "bill_or_statement_number_or_null",
  "bill_type": "bill_type_like_Regular_Final_Estimated_or_null",
  "total_amount_due_date": "date_format_like_August_13_2025",
  "number_of_days": "numeric_days_in_billing_period",
  "service_days": "numeric_days_same_as_number_of_days_or_null",
  "description": "general_bill_description_or_null",
  "previous_balance": "dollar_amount_or_null",
  "current_billing": "dollar_amount_for_current_period",
  "total_amount_due": "final_dollar_amount_due",
  "balance": "current_outstanding_balance_or_null",
  
  "payments_applied": [
    {
      "payment_date": "date_format_like_July_13_2025",
      "payment_amount": "dollar_amount"
    }
  ],

  "contact_info": {
    "website": "website_like_pse.com",
    "email": "email_like_customercare@pse.com",
    "phone_number": "phone_like_1-888-225-5773"
  },
  
  "late_payment_fee": {
    "percentage": "percentage_like_1%_or_null",
    "description": "description_of_late_payment_terms_or_null"
  },

  "late_fee_info": {
    "latefee_applied": "yes_or_no_or_null",
    "latefee_date": "date_when_late_fee_was_applied_or_null",
    "latefee_amount": "dollar_amount_of_late_fee_or_null",
    "latefee_by_duedate_percentage": "percentage_like_1%_or_null",
    "latefee_by_duedate": "dollar_amount_of_late_fee_if_late_or_null",
    "total_amount_with_latefee_by_duedate": "total_including_late_fees_or_null"
  },
  
  "meters": [
    {
      "meter_number": "meter_identifier_like_P147430234",
      "service_type": "service_type_like_Electric",
      "start_date": "billing_period_start_date",
      "service_from_date": "billing_period_start_date",
      "start_read": "starting_meter_reading",
      "previous_reading": "starting_meter_reading",
      "previous_reading_type": "Actual_or_Estimated_or_Customer_Read",
      "end_date": "billing_period_end_date",
      "service_to_date": "billing_period_end_date",
      "end_read": "ending_meter_reading",
      "current_reading": "ending_meter_reading",
      "current_reading_type": "Actual_or_Estimated_or_Customer_Read",
      "multiplier": "numeric_multiplier_value",
      "usage": "numeric_kilowatt_hours_value",
      "uom": "kWh",
      "meter_read_type": "Actual_or_Estimated_or_Customer_Read",
      
      "charge_details": [
        {
          "category": "charge_category_name",
          "description": "charge_category_name",
          "rate": "rate_value_or_null",
          "rate_x_unit": "calculation_like_3240_kWh_x_$0.14760",
          "charge": "dollar_amount",
          "amount": "dollar_amount"
        }
      ],

      "other_charges_and_credits": [
        {
          "category": "item_from_Other_Electric_Charges_section",
          "description": "item_from_Other_Electric_Charges_section",
          "rate": "rate_value_or_null",
          "rate_x_unit": "rate_calculation_or_null_if_not_shown",
          "charge": "dollar_amount_or_0.00",
          "amount": "dollar_amount_or_0.00"
        }
      ],
      
      "taxes": [
        {
          "description": "tax_name",
          "rate": "percentage_like_3.873%",
          "charge": "dollar_amount_or_0.00_if_included_in_above_charges"
        }
      ],
      
      "total_current_electric_charges": "total_for_this_meter"
    }
  ],

  "service_types": [],
  "taxes": {
    "per_service_taxes": [],
    "global_taxes": []
  }
}

CRITICAL INSTRUCTIONS:
- Include ALL base fields (account_number, customer_name, etc.)
- Create ONE entry in meters array for EACH meter on the bill
- Each meter entry must have ALL fields listed above
- charge_details array: Extract EVERY line item from the main charges table
  * **MOST CRITICAL**: Extract dollar amounts EXACTLY as shown in the "Charge" column
  * DO NOT calculate amounts from rate × usage - use the printed dollar amount exactly
  * Extract rates EXACTLY as shown - do not round or approximate (e.g., 0.007268 not 0.007626)
  * Verify each extracted amount matches the printed bill exactly (e.g., 23.55 not 23.54)
  * The printed dollar amount on the bill is the source of truth - always use it exactly
- other_charges_and_credits array: Extract EVERY item from "Other Electric Charges & Credits" section
  * INCLUDE items even if the charge is $0.00
  * Extract dollar amounts EXACTLY as shown - do not calculate
  * Look for section header "Other Electric Charges & Credits"
  * Extract ALL items listed under this header
  * If this section doesn't exist on the bill, use empty array []
- taxes array: Extract ALL taxes for this meter
  * Extract dollar amounts EXACTLY as shown on the bill
  * If a tax shows "(XX.XX included in above charges)" or similar, set charge to "0.00"
  * Only extract a dollar amount for taxes that are separately listed (not included in subtotal)
  * Use the exact dollar amount printed, not a calculated value
- total_current_electric_charges: Extract EXACTLY as shown on the bill (e.g., "541.12")
  * Do NOT calculate this - use the printed total exactly
  * This should match the "Current Electric Charges" or "Total current electric charges" line
- If multiple meters exist, the sum of all meter totals should equal total_amount_due

"""

PSE_ELECTRIC_PROMPT = f"""{BASE_EXTRACTION_FIELDS}

{PSE_ELECTRIC_SPECIFIC_INSTRUCTIONS}

{PSE_ELECTRIC_JSON_FORMAT}
"""
