def ensure_fields(result: dict) -> dict:

    # Contact Information
    if "contact_info" not in result:
        result["contact_info"] = {
            "website": None,
            "phone_number": None
        }
    else:
        # Ensure all subfields exist
        if "website" not in result["contact_info"]:
            result["contact_info"]["website"] = None
        if "phone_number" not in result["contact_info"]:
            result["contact_info"]["phone_number"] = None
    
    # Late Payment Charge
    if "late_payment_charge" not in result:
        result["late_payment_charge"] = {
            "percentage": None,
            "description": None
        }
    else:
        # Ensure all subfields exist
        if "percentage" not in result["late_payment_charge"]:
            result["late_payment_charge"]["percentage"] = None
        if "description" not in result["late_payment_charge"]:
            result["late_payment_charge"]["description"] = None
    
    # Consumption Units - separate array
    if "consumption_units" not in result:
        result["consumption_units"] = []
    
    # Amounts - separate array
    if "amounts" not in result:
        result["amounts"] = []

    # Detailed billing rows table
    if "detailed_billing_rows" not in result:
        result["detailed_billing_rows"] = []
    
    return result