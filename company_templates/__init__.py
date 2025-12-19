import os
from typing import Callable, Optional, List

# Map company names to their module names (normalized)
_COMPANY_MODULE_MAP = {
    "City of Redmond": "city_of_redmond",
    "Everett Public Works": "everett_public_works",
    "Kent Utility": "kent_utility",
    "Puget Sound Energy": "puget_sound_energy",
    "Puget Sound Energy - Gas": "puget_sound_energy_gas",
    "Republic Services": "republic_services",
    "Sammamish Plateau Water": "sammamish_plateau_water",
    "Seattle City Light": "seattle_city_light",
    "Seattle Public Utilities": "seattle_public_utilities",
    "Waste Management of Washington": "waste_management_washington",
    "Recology Waste Services": "recology_waste_services",
    "Southwest Suburban Sewer District": "southwest_suburban_sewer",
    "Valley View Sewer District": "valley_view_sewer",
    "King County Water District Twenty": "king_county_water_district_twenty",
    "Snohomish County PUD": "snohomish_county_pud",
    "Alderwood Water and Wastewater": "alderwood_water",
    "Cedar Grove Organics Recycling": "cedar_grove",
    "CenTrio Energy Seattle": "centrio_energy",
    "City of Auburn": "city_of_auburn",
    "City of Bellevue": "city_of_bellevue",
    "City of Bothell": "city_of_bothell",
    "City of Edmonds": "city_of_edmonds",
    "City of Frisco": "city_of_frisco",
    "City of Lacey": "city_of_lacey",
    "City of Ocean Shores": "city_of_ocean_shores",
    "City of Olympia": "city_of_olympia",
    "City of Renton": "city_of_renton",
    "Grays Harbor PUD": "grays_harbor_pud",
    "City of Lynnwood": "city_of_lynnwood",
    "Rubatino Refuse Removal": "rubatino_refuse_removal",
}


def get_all_company_names() -> List[str]:
    """
    Get a list of all supported company names.
    
    Returns:
        List of company names
    """
    return list(_COMPANY_MODULE_MAP.keys())


def get_company_handler(company_name: str) -> Optional[Callable]:
    """
    Get the handler function for a specific company.

    Args:
        company_name: The detected company name

    Returns:
        The handler function if found, None otherwise
    """
    if not company_name:
        return None

    module_name = _COMPANY_MODULE_MAP.get(company_name)
    if not module_name:
        return None

    try:
        # Dynamically import the module
        module = __import__(f"company_templates.{module_name}", fromlist=[module_name])
        # Each module should have an 'ensure_fields' function
        return getattr(module, "ensure_fields", None)
    except (ImportError, AttributeError):
        return None
