def ensure_fields(result: dict) -> dict:

    # Late fee info
    if "late_fee_info" not in result:
        result["late_fee_info"] = {
            "latefee_applied": None,
            "latefee_date": None,
            "latefee_amount": None,
            "latefee_by_duedate_percentage": None,
            "latefee_by_duedate": None,
            "total_amount_with_latefee_by_duedate": None
        }
    else:
        # Ensure all subfields exist
        if "latefee_applied" not in result["late_fee_info"]:
            result["late_fee_info"]["latefee_applied"] = None
        if "latefee_date" not in result["late_fee_info"]:
            result["late_fee_info"]["latefee_date"] = None
        if "latefee_amount" not in result["late_fee_info"]:
            result["late_fee_info"]["latefee_amount"] = None
        if "latefee_by_duedate_percentage" not in result["late_fee_info"]:
            result["late_fee_info"]["latefee_by_duedate_percentage"] = None
        if "latefee_by_duedate" not in result["late_fee_info"]:
            result["late_fee_info"]["latefee_by_duedate"] = None
        if "total_amount_with_latefee_by_duedate" not in result["late_fee_info"]:
            result["late_fee_info"]["total_amount_with_latefee_by_duedate"] = None

    # Meters
    if "meters" not in result:
        result["meters"] = []

    # Service types - ensure all required fields
    for service in result.get("service_types", []):
        if "line_item_charges" not in service:
            service["line_item_charges"] = []
        for line_item in service.get("line_item_charges", []):
            if "category" not in line_item:
                line_item["category"] = None
            if "description" not in line_item:
                line_item["description"] = None
            if "rate" not in line_item:
                line_item["rate"] = None
            if "amount" not in line_item:
                line_item["amount"] = None
            if "meter_number" not in line_item:
                line_item["meter_number"] = None
            if "usage" not in line_item:
                line_item["usage"] = None
            if "uom" not in line_item:
                line_item["uom"] = None
            if "previous_reading" not in line_item:
                line_item["previous_reading"] = None
            if "previous_reading_type" not in line_item:
                line_item["previous_reading_type"] = None
            if "current_reading" not in line_item:
                line_item["current_reading"] = None
            if "current_reading_type" not in line_item:
                line_item["current_reading_type"] = None
            if "usage_multiplier" not in line_item:
                line_item["usage_multiplier"] = None

    # Taxes
    if "taxes" not in result:
        result["taxes"] = {
            "per_service_taxes": [],
            "global_taxes": []
        }

    # Adjustments
    if "adjustments" not in result:
        result["adjustments"] = []

    # Payments applied
    if "payments_applied" not in result:
        result["payments_applied"] = []

    return result