def ensure_fields(result: dict) -> dict:

    # Contact Information
    if "contact_info" not in result:
        result["contact_info"] = {
            "phone_number": None,
            "email": None
        }
    else:
        # Ensure all subfields exist
        if "phone_number" not in result["contact_info"]:
            result["contact_info"]["phone_number"] = None
        if "email" not in result["contact_info"]:
            result["contact_info"]["email"] = None
    
    # Meter Information
    if "meter" not in result:
        result["meter"] = {
            "meter_number": None,
            "read_dates": {
                "start_date": None,
                "end_date": None
            },
            "billing_days": None,
            "meter_readings": {
                "previous_reading": None,
                "present_reading": None
            },
            "usage": {
                "cubic_feet": None,
                "gallons": None
            }
        }
    else:
        # Ensure all nested fields exist
        if "meter_number" not in result["meter"]:
            result["meter"]["meter_number"] = None
        if "read_dates" not in result["meter"]:
            result["meter"]["read_dates"] = {
                "start_date": None,
                "end_date": None
            }
        if "billing_days" not in result["meter"]:
            result["meter"]["billing_days"] = None
        if "meter_readings" not in result["meter"]:
            result["meter"]["meter_readings"] = {
                "previous_reading": None,
                "present_reading": None
            }
        if "usage" not in result["meter"]:
            result["meter"]["usage"] = {
                "cubic_feet": None,
                "gallons": None
            }

    return result