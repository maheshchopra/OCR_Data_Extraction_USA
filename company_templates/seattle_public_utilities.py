def ensure_fields(result: dict) -> dict:

    # Ensure Seattle Public Utilities-specific fields exist
        
    # Contact Information
    if "contact_info" not in result:
        result["contact_info"] = {
            "website": None,
            "phone_number": None,
            "email": None
        }
    else:
        # Ensure all subfields exist
        if "website" not in result["contact_info"]:
            result["contact_info"]["website"] = None
        if "phone_number" not in result["contact_info"]:
            result["contact_info"]["phone_number"] = None
        if "email" not in result["contact_info"]:
            result["contact_info"]["email"] = None
    
    # Late Payment Fee
    if "late_payment_fee" not in result:
        result["late_payment_fee"] = {
            "percentage": None,
            "description": None
        }
    else:
        # Ensure all subfields exist
        if "percentage" not in result["late_payment_fee"]:
            result["late_payment_fee"]["percentage"] = None
        if "description" not in result["late_payment_fee"]:
            result["late_payment_fee"]["description"] = None
    
    # Consumption Information
    if "consumption" not in result:
        result["consumption"] = {
            "ccf": None,
            "gallons": None,
            "ccf_to_gallons_conversion": None
        }
    else:
        # Ensure all subfields exist
        if "ccf" not in result["consumption"]:
            result["consumption"]["ccf"] = None
        if "gallons" not in result["consumption"]:
            result["consumption"]["gallons"] = None
        if "ccf_to_gallons_conversion" not in result["consumption"]:
            result["consumption"]["ccf_to_gallons_conversion"] = None

    # Ensure service_category field exists in line_item_charges for all services
    for service in result.get("service_types", []):
        if "line_item_charges" not in service:
            service["line_item_charges"] = []
        for line_item in service.get("line_item_charges", []):
            if "service_category" not in line_item:
                line_item["service_category"] = None

    return result