"""
Prompt templates for different utility bill formats.

Each template is designed for a specific company/municipality's bill format.
Templates include instructions for extracting all relevant billing information.
"""

import child_prompts

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


# =============================================================================
# TEMPLATE REGISTRY
# =============================================================================

PROMPT_TEMPLATES = {
    "city_of_redmond": {
        "name": "City of Redmond",
        "prompt": child_prompts.city_of_redmond.CITY_OF_REDMOND_PROMPT,
        "identifiers": [
            "city of redmond",
            "redmond washington",
            "redmond",
            "redmond utilities"
        ]
    },
    "everett_public_works": {
        "name": "Everett Public Works",
        "prompt": child_prompts.everett_public_works.EVERETT_PUBLIC_WORKS_PROMPT,
        "identifiers": [
            "everett",
            "everett public works",
            "city of everett",
            "everettwa"
        ]
    },
    "kent_utility": {
        "name": "Kent Utility",
        "prompt": child_prompts.kent_utility.KENT_UTILITY_PROMPT,
        "identifiers": [
            "kent",
            "kent utility",
            "city of kent",
            "kentwa"
        ]
    },
    "pse_electric": {
        "name": "Puget Sound Energy",
        "prompt": child_prompts.pse_electric.PSE_ELECTRIC_PROMPT,
        "identifiers": [
            "puget sound energy",
            "pse",
            "puget sound",
            "pugetsound"
        ]
    },
    "pse_gas": {
        "name": "Puget Sound Energy - Gas",
        "prompt": child_prompts.pse_gas.PSE_GAS_PROMPT,
        "identifiers": [
            "pse gas",
            "puget sound energy gas",
            "pse natural gas",
            "puget sound gas"
        ]
    },
    "recology_waste_services": {
        "name": "Recology Waste Services",
        "prompt": child_prompts.recology_waste_services.RECOLOGY_WASTE_SERVICES_PROMPT,
        "identifiers": [
            "recology waste services",
            "recology",
            "recology waste",
            "recology recycling"
        ]
    },
    "southwest_suburban_sewer_district": {
        "name": "Southwest Suburban Sewer District",
        "prompt": child_prompts.southwest_suburban_sewer.SOUTHWEST_SUBURBAN_SEWER_DISTRICT_PROMPT,
        "identifiers": [
            "southwest suburban sewer district",
            "swssd",
            "southwest sewer district",
            "suburban sewer district"
        ]
    },
    "valley_view_sewer_district": {
        "name": "Valley View Sewer District",
        "prompt": child_prompts.valley_view_sewer.VALLEY_VIEW_SEWER_DISTRICT_PROMPT,
        "identifiers": [
            "valley view sewer district",
            "valley view sewer",
            "valley view district",
            "valley view sewer bill"
        ]
    },
    "king_county_water_district_twenty": {
        "name": "King County Water District Twenty",
        "prompt": child_prompts.king_county_water_district_twenty.KING_COUNTY_WATER_DISTRICT_PROMPT,
        "identifiers": [
            "king county water district 20",
            "king county water district twenty",
            "king county water district",
        ]
    },
    "snohomish_county_pud": {
        "name": "Snohomish County PUD",
        "prompt": child_prompts.snohomish_county_pud.SNOHOMISH_COUNTY_PUD_PROMPT,
        "identifiers": [
            "snohomish county pud",
            "snopud",
            "snohomish pud",
            "snopud bill"
        ]
    },
    "republic_services": {
        "name": "Republic Services",
        "prompt": child_prompts.republic_services.REPUBLIC_SERVICES_PROMPT,
        "identifiers": [
            "republic services",
            "republic",
            "republicservices"
        ]
    },
    "sammamish_plateau_water": {
        "name": "Sammamish Plateau Water",
        "prompt": child_prompts.sammamish_plateau_water.SAMMAMISH_PLATEAU_WATER_PROMPT,
        "identifiers": [
            "sammamish plateau water",
            "sammamish plateau",
            "spwater",
            "sammamish water"
        ]
    },
    "seattle_city_light": {
        "name": "Seattle City Light",
        "prompt": child_prompts.seattle_city_light.SEATTLE_CITY_LIGHT_PROMPT,
        "identifiers": [
            "seattle city light",
            "city light",
            "seattle light",
            "scl"
        ]
    },

    "seattle_public_utilities": {
        "name": "Seattle Public Utilities",
        "prompt": child_prompts.seattle_public_utilities.SEATTLE_PUBLIC_UTILITIES_PROMPT,
        "identifiers": [
            "seattle public utilities",
            "spu",
            "seattle utilities"
        ]
    },

    "waste_management": {
        "name": "Waste Management of Washington",
        "prompt": child_prompts.waste_management_washington.WASTE_MANAGEMENT_PROMPT,
        "identifiers": [
            "waste management",
            "wm",
            "waste management of washington"
        ]
    },

    "alderwood_water_wastewater": {
        "name": "Alderwood Water and Wastewater",
        "prompt": child_prompts.alderwood_water.ALDERWOOD_WATER_WASTEWATER_PROMPT,
        "identifiers": [
            "alderwood water",
            "alderwood water and wastewater",
            "alderwood",
            "alderwood wastewater"
        ]
    },

    "cedar_grove_organics_recycling": {
        "name": "Cedar Grove Organics Recycling",
        "prompt": child_prompts.cedar_grove.CEDAR_GROVE_ORGANICS_RECYCLING_PROMPT,
        "identifiers": [
            "cedar grove",
            "cedar grove organics",
            "cedar grove organics recycling",
            "cedar grove recycling"
        ]
    },

    "centrio_energy_seattle": {
        "name": "CenTrio Energy Seattle",
        "prompt": child_prompts.centrio_energy.CENTRIO_ENERGY_SEATTLE_PROMPT,
        "identifiers": [
            "centrio",
            "centrio energy",
            "centrio energy seattle",
            "centrio seattle"
        ]
    },

    "city_of_auburn": {
        "name": "City of Auburn",
        "prompt": child_prompts.city_of_auburn.CITY_OF_AUBURN_PROMPT,
        "identifiers": [
            "city of auburn",
            "auburn",
            "auburn washington",
            "auburn utilities"
        ]
    },

    "city_of_bellevue": {
        "name": "City of Bellevue",
        "prompt": child_prompts.city_of_bellevue.CITY_OF_BELLEVUE_PROMPT,
        "identifiers": [
            "city of bellevue",
            "bellevue",
            "bellevue washington",
            "bellevue utilities"
        ]
    },

    "city_of_bothell": {
        "name": "City of Bothell",
        "prompt": child_prompts.city_of_bothell.CITY_OF_BOTHELL_PROMPT,
        "identifiers": [
            "city of bothell",
            "bothell",
            "bothell washington",
            "bothell utilities"
        ]
    },

    "city_of_edmonds": {
        "name": "City of Edmonds",
        "prompt": child_prompts.city_of_edmonds.CITY_OF_EDMONDS_PROMPT,
        "identifiers": [
            "city of edmonds",
            "edmonds",
            "edmonds washington",
            "edmonds utilities"
        ]
    },

    "city_of_frisco": {
        "name": "City of Frisco",
        "prompt": child_prompts.city_of_frisco.CITY_OF_FRISCO_PROMPT,
        "identifiers": [
            "city of frisco",
            "frisco",
            "frisco texas",
            "frisco utilities"
        ]
    },

    "city_of_lacey": {
        "name": "City of Lacey",
        "prompt": child_prompts.city_of_lacey.CITY_OF_LACEY_PROMPT,
        "identifiers": [
            "city of lacey",
            "lacey",
            "lacey washington",
            "lacey utilities"
        ]
    },

    "city_of_ocean_shores": {
        "name": "City of Ocean Shores",
        "prompt": child_prompts.city_of_ocean_shores.CITY_OF_OCEAN_SHORES_PROMPT,
        "identifiers": [
            "city of ocean shores",
            "ocean shores",
            "ocean shores washington",
            "ocean shores utilities"
        ]
    },

    "city_of_olympia": {
        "name": "City of Olympia",
        "prompt": child_prompts.city_of_olympia.CITY_OF_OLYMPIA_PROMPT,
        "identifiers": [
            "city of olympia",
            "olympia",
            "olympia washington",
            "olympia utilities"
        ]
    },

    "city_of_renton": {
        "name": "City of Renton",
        "prompt": child_prompts.city_of_renton.CITY_OF_RENTON_PROMPT,
        "identifiers": [
            "city of renton",
            "renton",
            "renton washington",
            "renton utilities"
        ]
    },

    "grays_harbor_pud": {
        "name": "Grays Harbor PUD",
        "prompt": child_prompts.grays_harbor_pud.GRAYS_HARBOR_PUD_PROMPT,
        "identifiers": [
            "grays harbor pud",
            "grays harbor",
            "grays harbor public utility district",
            "ghpud"
        ]
    },

    "city_of_lynnwood": {
        "name": "City of Lynnwood",
        "prompt": child_prompts.city_of_lynnwood.CITY_OF_LYNNWOOD_PROMPT,
        "identifiers": [
            "city of lynnwood",
            "lynnwood",
            "lynwood",
            "lynnwood washington",
            "lynwood washington",
            "lynnwood utilities"
        ]
    },

    "rubatino_refuse_removal": {
        "name": "Rubatino Refuse Removal",
        "prompt": child_prompts.rubatino_refuse_removal.RUBATINO_REFUSE_REMOVAL_PROMPT,
        "identifiers": [
            "rubatino",
            "rubatino refuse",
            "rubatino refuse removal"
        ]
    },

    # Add more templates here as needed
}


def get_prompt_for_company(company_name):
    """
    Get the appropriate prompt template based on company name.
    
    Args:
        company_name (str): Name of the company/municipality
        
    Returns:
        str: The prompt template to use
    """
    if not company_name:
        return None
    
    company_lower = company_name.lower()
    
    # Check each template's identifiers
    for template_key, template_data in PROMPT_TEMPLATES.items():
        for identifier in template_data["identifiers"]:
            if identifier in company_lower:
                return template_data["prompt"]
    
    return None


def detect_company_from_filename(filename):
    """
    Attempt to detect the company/municipality from the PDF filename.
    
    Args:
        filename (str): The PDF filename
        
    Returns:
        str: Detected company name or None
    """
    filename_lower = filename.lower()

    # Special-case: avoid classifying PSE Gas filenames as PSE Electric just because "pse" matches first.
    # If the filename hints at gas, force the gas template.
    if ("pse" in filename_lower or "puget" in filename_lower) and (
        "gas" in filename_lower or "naturalgas" in filename_lower or "natural_gas" in filename_lower or "natural gas" in filename_lower
    ):
        return PROMPT_TEMPLATES["pse_gas"]["name"]
    
    # Check each template's identifiers against the filename
    for template_key, template_data in PROMPT_TEMPLATES.items():
        for identifier in template_data["identifiers"]:
            if identifier.replace(" ", "") in filename_lower.replace(" ", ""):
                return template_data["name"]
    
    return None


def get_default_prompt():
    """
    Returns a generic default prompt for bills that don't match any template.
    
    Returns:
        str: Default prompt template
    """
    return f"""{BASE_EXTRACTION_FIELDS}

    {BASE_JSON_FORMAT}

    IMPORTANT INSTRUCTIONS:
    - Extract ALL visible information - scan the entire document thoroughly
    - Use null only if information is truly not present
    - For payments: extract ALL payments applied, create one entry per payment
    - For adjustments: extract ALL adjustments separately with their category names and amounts
      - Use positive amounts for credits (e.g., "$50.00" for a credit)
      - Use negative amounts for debits/fees (e.g., "-$10.00" for a late fee)
    - For total amount due: this is the final balance after all calculations
    - For taxes: separate per-service taxes from global/bill-wide taxes
    - For services: GROUP all meters of the same service type into ONE service entry
    - For addresses: extract complete addresses including street, city, state, zip
    - For amounts: include dollar sign and exact amount (e.g., "$123.45")
    - For dates: use format like "March 03 2025" or "Mar 3 2025"
    - For readings: extract exact values (e.g., "12345", "12,345", "12345.6")
    - For CCF usage: extract numeric values (e.g., "70.00", "84.00", "15.5")
    - For meter data: extract CCF usage, previous reading, current reading for each line item
    - Use empty arrays [] if no items found for taxes, services, line_items, or meters
    - Look in ALL sections: headers, billing details, service breakdown, tax summary, payment history, etc.
    """

