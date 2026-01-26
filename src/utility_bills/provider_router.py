import base64
from pathlib import Path
from typing import Any, Callable, Dict, Union

from openai import OpenAI
from provider_functions import (
    alderwood,
    auburn,
    bellevue,
    bothell,
    cedar_grove,
    centrio,
    edmond,
    everett,
    frisco,
    kent,
    king_county,
    king_county_summary,
    lacey,
    lynnwood,
    ocean_shores,
    olympia,
    pse_electric,
    pse_gas,
    pse_gas_and_electric,
    recology,
    redmond,
    renton,
    republic,
    rubatino,
    sammamish,
    scl,
    scl_2,
    skagit,
    spu,
    sssd,
    valley_view,
    wd_20,
    wd_49,
    wmw,
)
from pydantic_models import (
    AlderwoodBillExtract,
    AuburnBillExtract,
    BellevueBillExtract,
    BothellBillExtract,
    CedarGroveBillExtract,
    CenTrioBillExtract,
    EdmondsBillExtract,
    EverettBillExtract,
    FriscoBillExtract,
    KentBillExtract,
    KingCountyBillExtract,
    KingCountySummaryBillExtract,
    LaceyBillExtract,
    LynnwoodBillExtract,
    OceanShoresBillExtract,
    OlympiaBillExtract,
    PSEElectricBillExtract,
    PSEGasAndElectricBillExtract,
    PSEGasBillExtract,
    RecologyBillExtract,
    RedmondBillExtract,
    RentonBillExtract,
    RepublicServicesBillExtract,
    RubatinoBillExtract,
    SammamishPlateauWaterBillExtract,
    SeattleCityLightBillExtract,
    SeattleCityLightCommercialBillExtract,
    SkagitPUDBillExtract,
    SPUBillExtract,
    SSSDBillExtract,
    ValleyViewBillExtract,
    WaterDistrict20BillExtract,
    WaterDistrict49BillExtract,
    WMBillExtract,
)

client = OpenAI()

# Map normalized provider names to prompt filenames
PROVIDER_PROMPTS: dict[str, str] = {
    "seattle public utilities": "spu.txt",
    "puget sound energy - gas": "pse_gas.txt",
    "puget sound energy - electric": "pse_electric.txt",
    "puget sound energy - gas and electric": "pse_gas_and_electric.txt",
    "seattle city light": "scl.txt",
    "seattle city light - commercial": "scl_2.txt",
    "waste management of washington": "wmw.txt",
    "sammamish plateau water": "sammamish.txt",
    "kent": "kent.txt",
    "everett public works": "everett.txt",
    "republic services": "republic.txt",
    "redmond city washington": "redmond.txt",
    "king county wastewater treatment division": "king_county.txt",
    "king county account summary": "king_county_summary.txt",
    "city of bellevue": "bellevue.txt",
    "city of lynnwood": "lynnwood.txt",
    "rubatino refuse removal": "rubatino.txt",
    "recology king county": "recology.txt",
    "king county water district 20": "wd_20.txt",
    "valley view sewer district": "valley_view.txt",
    "city of edmonds": "edmond.txt",
    "alderwood water & wastewater district": "alderwood.txt",
    "city of lacey": "lacey.txt",
    "city of renton": "renton.txt",
    "cedar grove organics recycling llc": "cedar_grove.txt",
    "centrio energy seattle": "centrio.txt",
    "southwest suburban sewer district": "sssd.txt",
    "city of bothell": "bothell.txt",
    "city of olympia": "olympia.txt",
    "city of auburn": "auburn.txt",
    "snohomish county pud": "skagit.txt",
    "city of frisco": "frisco.txt",
    "city of ocean shores": "ocean_shores.txt",
    "king county water district 49": "wd_49.txt",
    # add more providers here as I support them
}

# provider-specific post‑processors
PROVIDER_POSTPROCESSORS: Dict[str, Callable[[dict], dict]] = {
    "seattle public utilities": spu.postprocess_seattle_public_utilities,
    "puget sound energy - gas": pse_gas.postprocess_pse_gas,
    "puget sound energy - electric": pse_electric.postprocess_pse_electric,
    "puget sound energy - gas and electric": pse_gas_and_electric.postprocess_pse_gas_and_electric,
    "seattle city light": scl.postprocess_seattle_city_light,
    "waste management of washington": wmw.postprocess_waste_management_washington,
    "sammamish plateau water": sammamish.postprocess_sammamish_plateau_water,
    "kent": kent.postprocess_kent,
    "everett public works": everett.postprocess_everett,
    "republic services": republic.postprocess_republic_services,
    "redmond city washington": redmond.postprocess_redmond,
    "king county wastewater treatment division": king_county.postprocess_king_county,
    "king county account summary": king_county_summary.postprocess_king_county_summary,
    "city of bellevue": bellevue.postprocess_bellevue,
    "city of lynnwood": lynnwood.postprocess_lynnwood,
    "rubatino refuse removal": rubatino.postprocess_rubatino,
    "recology king county": recology.postprocess_recology,
    "king county water district 20": wd_20.postprocess_water_district_20,
    "valley view sewer district": valley_view.postprocess_valley_view,
    "city of edmonds": edmond.postprocess_edmonds,
    "alderwood water & wastewater district": alderwood.postprocess_alderwood,
    "city of lacey": lacey.postprocess_lacey,
    "city of renton": renton.postprocess_renton,
    "cedar grove organics recycling llc": cedar_grove.postprocess_cedar_grove,
    "centrio energy seattle": centrio.postprocess_centrio,
    "southwest suburban sewer district": sssd.postprocess_sssd,
    "city of bothell": bothell.postprocess_bothell,
    "city of olympia": olympia.postprocess_olympia,
    "city of auburn": auburn.postprocess_auburn,
    "snohomish county pud": skagit.postprocess_skagit,
    "city of frisco": frisco.postprocess_frisco,
    "city of ocean shores": ocean_shores.postprocess_ocean_shores,
    "seattle city light - commercial": scl_2.postprocess_seattle_city_light_commercial,
    "king county water district 49": wd_49.postprocess_water_district_49,
    # add more providers here later
}

# provider-specific validation checkers
PROVIDER_VALIDATION_CHECKERS: Dict[str, Callable[[dict], bool]] = {
    "seattle public utilities": spu.check_validation_passed,
    "puget sound energy - gas": pse_gas.check_validation_passed,
    "puget sound energy - electric": pse_electric.check_validation_passed,
    "puget sound energy - gas and electric": pse_gas_and_electric.check_validation_passed,
    "seattle city light": scl.check_validation_passed,
    "waste management of washington": wmw.check_validation_passed,
    "sammamish plateau water": sammamish.check_validation_passed,
    "kent": kent.check_validation_passed,
    "everett public works": everett.check_validation_passed,
    "republic services": republic.check_validation_passed,
    "king county wastewater treatment division": king_county.check_validation_passed,
    "king county account summary": king_county_summary.check_validation_passed,
    "city of bellevue": bellevue.check_validation_passed,
    "city of lynnwood": lynnwood.check_validation_passed,
    "rubatino refuse removal": rubatino.check_validation_passed,
    "recology king county": recology.check_validation_passed,
    "king county water district 20": wd_20.check_validation_passed,
    "valley view sewer district": valley_view.check_validation_passed,
    "city of edmonds": edmond.check_validation_passed,
    "alderwood water & wastewater district": alderwood.check_validation_passed,
    "city of lacey": lacey.check_validation_passed,
    "city of renton": renton.check_validation_passed,
    "cedar grove organics recycling llc": cedar_grove.check_validation_passed,
    "centrio energy seattle": centrio.check_validation_passed,
    "southwest suburban sewer district": sssd.check_validation_passed,
    "city of bothell": bothell.check_validation_passed,
    "city of olympia": olympia.check_validation_passed,
    "city of auburn": auburn.check_validation_passed,
    "snohomish county pud": skagit.check_validation_passed,
    "city of frisco": frisco.check_validation_passed,
    "city of ocean shores": ocean_shores.check_validation_passed,
    "seattle city light - commercial": scl_2.check_validation_passed,
    "king county water district 49": wd_49.check_validation_passed,
    # add more providers here later
}

# Map provider names to their Pydantic models
PROVIDER_MODELS = {
    "seattle public utilities": SPUBillExtract,
    "puget sound energy - gas": PSEGasBillExtract,
    "puget sound energy - electric": PSEElectricBillExtract,
    "puget sound energy - gas and electric": PSEGasAndElectricBillExtract,
    "seattle city light": SeattleCityLightBillExtract,
    "waste management of washington": WMBillExtract,
    "sammamish plateau water": SammamishPlateauWaterBillExtract,
    "kent": KentBillExtract,
    "everett public works": EverettBillExtract,
    "republic services": RepublicServicesBillExtract,
    "redmond city washington": RedmondBillExtract,
    "king county wastewater treatment division": KingCountyBillExtract,
    "king county account summary": KingCountySummaryBillExtract,
    "city of bellevue": BellevueBillExtract,
    "city of lynnwood": LynnwoodBillExtract,
    "rubatino refuse removal": RubatinoBillExtract,
    "recology king county": RecologyBillExtract,
    "king county water district 20": WaterDistrict20BillExtract,
    "valley view sewer district": ValleyViewBillExtract,
    "city of edmonds": EdmondsBillExtract,
    "alderwood water & wastewater district": AlderwoodBillExtract,
    "city of lacey": LaceyBillExtract,
    "city of renton": RentonBillExtract,
    "cedar grove organics recycling llc": CedarGroveBillExtract,
    "centrio energy seattle": CenTrioBillExtract,
    "southwest suburban sewer district": SSSDBillExtract,
    "city of bothell": BothellBillExtract,
    "city of olympia": OlympiaBillExtract,
    "city of auburn": AuburnBillExtract,
    "snohomish county pud": SkagitPUDBillExtract,
    "city of frisco": FriscoBillExtract,
    "city of ocean shores": OceanShoresBillExtract,
    "seattle city light - commercial": SeattleCityLightCommercialBillExtract,
    "king county water district 49": WaterDistrict49BillExtract,
    # add more providers here later
}


def detect_provider_from_file_id(file_id: str) -> str:
    """
    Ask the LLM to read the bill PDF and return the provider name.
    """

    allowed_providers = list(PROVIDER_PROMPTS.keys())
    allowed_display = ", ".join(f"'{name}'" for name in allowed_providers)

    response = client.responses.create(
        model="gpt-4.1-mini",  # or another inexpensive model
        input=[
            {
                "role": "user",
                "content": [
                    {"type": "input_file", "file_id": file_id},
                    {
                        "type": "input_text",
                        "text": (
                            "You are identifying the utility provider that issued this bill.\n\n"
                            "You MUST answer with EXACTLY ONE name from the following list, "
                            "and nothing else (no extra words, punctuation, or explanation):\n"
                            f"{allowed_display}\n\n"
                            "Look at the bill carefully:\n"
                            "- For Puget Sound Energy bills, check if it's for Natural Gas, Electric service or both together\n"
                            "- For Seattle City Light bills, check the detailed billing section:\n"
                            "  * If you see 'Power Factor Penalty', 'Small General Energy', service categories 'KVRH' or 'KW', "
                            "or totals formatted as 'Total for: [address]', answer: seattle city light - commercial\n"
                            "  * Otherwise, answer: seattle city light\n"
                            "- For King County bills:\n"
                            "  * If you see 'Account Summary' as a heading with an information icon (i in a circle) next to it, "
                            "AND the page shows fields like 'Most Recent Invoice #', 'Most Recent Invoice Date', 'Remaining Balance', "
                            "and 'Choose a Payment Amount' section, answer: king county account summary\n"
                            "  * If you see a detailed invoice with 'DESCRIPTION' section, '*Past Due', 'Current Billing', "
                            "'Discount Early Payoff', or 'BILLING PERIOD' table, answer: king county wastewater treatment division\n"
                            "- For King County Water District bills:\n"
                            "  * Look for 'King County Water District No. 49' or 'KING COUNTY Water District No.49' in the header/logo area\n"
                            "  * If found, answer: king county water district 49\n"
                            "  * If you see 'KING COUNTY WATER DISTRICT 20', answer: king county water district 20\n"
                            "- Choose the specific option that matches BOTH the provider and service type\n"
                            "- scroll to the VERY BOTTOM of the page and look for a URL/website address\n"
                            "If you find a URL containing 'rubatino.onlineportal.us.com', answer: rubatino refuse removal\n"
                            "Reply with only that exact name."
                        ),
                    },
                ],
            }
        ],
    )

    # Extract the text from the response
    provider_text = response.output[0].content[0].text

    # Convert to plain string
    if hasattr(provider_text, "value"):
        provider_name = provider_text.value
    else:
        provider_name = str(provider_text)

    # Normalize and validate
    provider_name = provider_name.strip()
    normalized = provider_name.lower()

    if normalized not in PROVIDER_PROMPTS:
        raise ValueError(
            f"Model returned unknown provider '{provider_name}'. "
            f"Expected one of: {list(PROVIDER_PROMPTS.keys())}"
        )

    # return normalized since the dict keys are lowercase
    return normalized


def encode_png_to_base64(file_path: str | Path) -> str:
    """
    Encode a PNG file to base64 string.

    Args:
        file_path: Path to the PNG file.

    Returns:
        Base64 encoded string of the PNG image.
    """
    with open(file_path, "rb") as f:
        return base64.b64encode(f.read()).decode("utf-8")


def detect_provider_from_png(png_path: str | Path, client: OpenAI | None = None) -> str:
    """
    Ask the LLM to read the bill PNG image and return the provider name.

    Args:
        png_path: Path to the PNG file.
        client: OpenAI client instance. If None, creates a new one.

    Returns:
        The normalized provider name.
    """
    if client is None:
        client = OpenAI()

    allowed_providers = list(PROVIDER_PROMPTS.keys())
    allowed_display = ", ".join(f"'{name}'" for name in allowed_providers)

    base64_image = encode_png_to_base64(png_path)

    response = client.chat.completions.create(
        model="gpt-4o",
        messages=[
            {
                "role": "user",
                "content": [
                    {
                        "type": "image_url",
                        "image_url": {
                            "url": f"data:image/png;base64,{base64_image}",
                        },
                    },
                    {
                        "type": "text",
                        "text": (
                            "You are identifying the utility provider that issued this bill.\n\n"
                            "You MUST answer with EXACTLY ONE name from the following list, "
                            "and nothing else (no extra words, punctuation, or explanation):\n"
                            f"{allowed_display}\n\n"
                            "Look at the bill carefully:\n"
                            "- For Puget Sound Energy bills, check if it's for Natural Gas, Electric service or both together\n"
                            "- For Seattle City Light bills, check the detailed billing section:\n"
                            "  * If you see 'Power Factor Penalty', 'Small General Energy', service categories 'KVRH' or 'KW', "
                            "or totals formatted as 'Total for: [address]', answer: seattle city light - commercial\n"
                            "  * Otherwise, answer: seattle city light\n"
                            "- For King County bills:\n"
                            "  * If you see 'Account Summary' as a heading with an information icon (i in a circle) next to it, "
                            "AND the page shows fields like 'Most Recent Invoice #', 'Most Recent Invoice Date', 'Remaining Balance', "
                            "and 'Choose a Payment Amount' section, answer: king county account summary\n"
                            "  * If you see a detailed invoice with 'DESCRIPTION' section, '*Past Due', 'Current Billing', "
                            "'Discount Early Payoff', or 'BILLING PERIOD' table, answer: king county wastewater treatment division\n"
                            "- For King County Water District bills:\n"
                            "  * Look for 'King County Water District No. 49' or 'KING COUNTY Water District No.49' in the header/logo area\n"
                            "  * If found, answer: king county water district 49\n"
                            "  * If you see 'KING COUNTY WATER DISTRICT 20', answer: king county water district 20\n"
                            "- Choose the specific option that matches BOTH the provider and service type\n"
                            "- scroll to the VERY BOTTOM of the page and look for a URL/website address\n"
                            "If you find a URL containing 'rubatino.onlineportal.us.com', answer: rubatino refuse removal\n"
                            "Reply with only that exact name."
                        ),
                    },
                ],
            }
        ],
        max_tokens=100,
    )

    provider_name = response.choices[0].message.content.strip()
    normalized = provider_name.lower()

    if normalized not in PROVIDER_PROMPTS:
        raise ValueError(
            f"Model returned unknown provider '{provider_name}'. "
            f"Expected one of: {list(PROVIDER_PROMPTS.keys())}"
        )

    return normalized


def get_prompt_path_for_provider(
    project_root: Union[str, Path],
    provider_name: str,
) -> Path:
    """
    Map a detected provider name to the corresponding prompt file path.
    """
    project_root = Path(project_root)

    normalized = provider_name.strip().lower()
    prompt_filename = PROVIDER_PROMPTS.get(normalized)

    if not prompt_filename:
        # You can change this to a default prompt or logging behavior if you prefer
        raise ValueError(
            f"Unknown provider '{provider_name}'. "
            f"Known providers: {list(PROVIDER_PROMPTS.keys())}"
        )

    return project_root / "src" / "utility_bills" / "prompts" / prompt_filename


def select_prompt_for_bill(
    project_root: Union[str, Path],
    file_id: str,
) -> Path:
    """
    High-level helper: detect provider from the bill and return the prompt path.
    """
    provider_name = detect_provider_from_file_id(file_id)
    return get_prompt_path_for_provider(project_root, provider_name)


def postprocess_for_provider(provider_name: str, data: dict) -> dict:
    """
    Apply any provider-specific post‑processing to the extracted JSON.
    If no post‑processor is registered, return data unchanged.
    """
    func = PROVIDER_POSTPROCESSORS.get(provider_name.strip().lower())
    if not func:
        return data
    return func(data)


def check_validation_for_provider(provider_name: str, data: dict) -> bool:
    """
    Check if validation passed for a provider-specific utility bill.
    If no validation checker is registered, returns True by default.

    Args:
        provider_name: The normalized provider name.
        data: The extracted utility bill dictionary after post-processing.

    Returns:
        True if validation passed or no checker is registered, False otherwise.
    """
    func = PROVIDER_VALIDATION_CHECKERS.get(provider_name.strip().lower())
    if not func:
        # If no validation checker is registered, assume validation passed
        return True
    return func(data)


def get_model_for_provider(provider_name: str):
    """
    Get the Pydantic model class for a given provider.

    Args:
        provider_name: The normalized provider name.

    Returns:
        The Pydantic model class for that provider.

    Raises:
        ValueError: If no model is registered for the provider.
    """
    normalized = provider_name.strip().lower()
    model_class = PROVIDER_MODELS.get(normalized)

    if model_class is None:
        raise ValueError(
            f"No Pydantic model registered for provider '{provider_name}'. "
            f"Known providers: {list(PROVIDER_MODELS.keys())}"
        )

    return model_class
