def ensure_fields(result: dict) -> dict:
    # Force correct account type for this template (model may mislabel as Electric)
    result["account_type"] = "Gas"
    # Top-level fields
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
    if "bill_number" not in result:
        result["bill_number"] = None
    if "bill_type" not in result:
        result["bill_type"] = None
    if "service_days" not in result:
        result["service_days"] = result.get("number_of_days")
    if "description" not in result:
        result["description"] = None
    if "balance" not in result:
        result["balance"] = None

    # Contact Information
    if "contact_info" not in result:
        result["contact_info"] = {
            "website": None,
            "email": None,
            "phone_number": None
        }
    else:
        # Ensure all subfields exist
        if "website" not in result["contact_info"]:
            result["contact_info"]["website"] = None
        if "email" not in result["contact_info"]:
            result["contact_info"]["email"] = None
        if "phone_number" not in result["contact_info"]:
            result["contact_info"]["phone_number"] = None
    
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
    
    # Late Fee Info (additional structure)
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

    # PSE Gas Meters array
    if "meters" not in result:
        result["meters"] = []
    else:
        # Filter out unexpected non-dict entries (e.g., nulls from model output)
        result["meters"] = [m for m in result.get("meters", []) if isinstance(m, dict)]
    
    # Ensure each meter has all required fields
    for meter in result.get("meters", []):
        if "meter_number" not in meter:
            meter["meter_number"] = None
        if "meter_location" not in meter:
            meter["meter_location"] = None
        # Force correct service type for this template
        meter["service_type"] = "Gas"
        if "read_date" not in meter:
            meter["read_date"] = None
        if "start_date" not in meter:
            meter["start_date"] = None
        if "service_from_date" not in meter:
            meter["service_from_date"] = meter.get("start_date")
        if "previous_reading" not in meter:
            meter["previous_reading"] = None
        if "previous_reading_type" not in meter:
            meter["previous_reading_type"] = None
        if "end_date" not in meter:
            meter["end_date"] = None
        if "service_to_date" not in meter:
            meter["service_to_date"] = meter.get("end_date")
        if "current_reading" not in meter:
            meter["current_reading"] = None
        if "current_reading_type" not in meter:
            meter["current_reading_type"] = None
        if "multiplier" not in meter:
            meter["multiplier"] = None
        if "usage" not in meter:
            meter["usage"] = None
        # Prefer therms for gas meters; override common wrong value
        if ("uom" not in meter) or ((meter.get("uom") or "").lower() in ("kwh", "kw h", "kilowatt hours", "kilowatt-hour")):
            meter["uom"] = "Therms"
        if "read_type" not in meter:
            meter["read_type"] = None
        if "total_current_electric_charges" not in meter:
            meter["total_current_electric_charges"] = None
    
    # Ensure service_types exists
    if "service_types" not in result:
        result["service_types"] = []
    else:
        # Filter out unexpected non-dict entries
        result["service_types"] = [s for s in result.get("service_types", []) if isinstance(s, dict)]
    
    # Ensure line_item_charges in service_types have all fields
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
    
    # Ensure taxes structure exists
    if "taxes" not in result:
        result["taxes"] = {
            "per_service_taxes": [],
            "global_taxes": []
        }
    
    # Ensure adjustments array exists
    if "adjustments" not in result:
        result["adjustments"] = []
    
    # Ensure payments_applied array exists
    if "payments_applied" not in result:
        result["payments_applied"] = []

    return result