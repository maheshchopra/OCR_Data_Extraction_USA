def ensure_fields(result: dict) -> dict:

    # Top-level provider fields
    if "provider_website" not in result:
        result["provider_website"] = None
    if "provider_customer_service_phone" not in result:
        result["provider_customer_service_phone"] = None
    if "provider_customer_service_email" not in result:
        result["provider_customer_service_email"] = None
    if "provider_address" not in result:
        result["provider_address"] = None
    if "provider_return_address" not in result:
        result["provider_return_address"] = None
    
    # Bill information
    if "bill_number" not in result:
        result["bill_number"] = None
    if "bill_type" not in result:
        result["bill_type"] = None
    
    # Balance and service days
    if "balance" not in result:
        result["balance"] = None
    if "service_days" not in result:
        result["service_days"] = result.get("number_of_days")
    
    # Late Fee Info
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
    
    # Meters - waste services typically don't have meters, but ensure empty array
    if "meters" not in result:
        result["meters"] = []
    
    # Ensure service_types and line_item fields
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
    
    # Payments
    if "payments_applied" not in result:
        result["payments_applied"] = []

    return result