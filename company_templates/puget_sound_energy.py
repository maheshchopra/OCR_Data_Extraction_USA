def _parse_number(value):
    """Parse an integer/float string like '1,120' into a float, or None on failure."""
    if value is None:
        return None
    s = str(value).replace(',', '').strip()
    if s == '':
        return None
    try:
        return float(s)
    except (ValueError, TypeError):
        return None

def _normalize_pse_multipliers(result: dict) -> dict:
    """
    For each meter, ensure multiplier is consistent with start/end reads and usage.
    If usage ~= (end_read - start_read) * multiplier but the current multiplier is off
    by a clear factor (like 40 vs 80), correct the multiplier to the implied value.
    """
    meters = result.get("meters", [])
    for meter in meters:
        start = _parse_number(meter.get("start_read") or meter.get("previous_reading"))
        end = _parse_number(meter.get("end_read") or meter.get("current_reading"))
        usage = _parse_number(meter.get("usage"))
        current_mult = _parse_number(meter.get("multiplier"))

        if start is None or end is None or usage is None:
            continue
        diff = end - start
        if diff <= 0:
            continue

        implied = usage / diff
        implied_rounded = round(implied)

        # Only trust the implied multiplier if it is effectively an integer
        if abs(implied - implied_rounded) < 0.01:
            # If we have no multiplier, or the existing one disagrees significantly, correct it
            if current_mult is None or abs(current_mult - implied_rounded) > 0.1:
                meter["multiplier"] = str(int(implied_rounded))

    return result

def ensure_fields(result: dict) -> dict:
    # Force correct account type for this template (model may mislabel as Gas)
    result["account_type"] = "Electric"
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

    # PSE Meters array
    if "meters" not in result:
        result["meters"] = []
    
    # Ensure each meter has all required fields
    for meter in result.get("meters", []):
        if "meter_number" not in meter:
            meter["meter_number"] = None
        # Force correct service type for this template
        meter["service_type"] = "Electric"
        if "start_date" not in meter:
            meter["start_date"] = None
        if "service_from_date" not in meter:
            meter["service_from_date"] = meter.get("start_date")
        if "start_read" not in meter:
            meter["start_read"] = None
        if "previous_reading" not in meter:
            meter["previous_reading"] = meter.get("start_read")
        if "previous_reading_type" not in meter:
            meter["previous_reading_type"] = None
        if "end_date" not in meter:
            meter["end_date"] = None
        if "service_to_date" not in meter:
            meter["service_to_date"] = meter.get("end_date")
        if "end_read" not in meter:
            meter["end_read"] = None
        if "current_reading" not in meter:
            meter["current_reading"] = meter.get("end_read")
        if "current_reading_type" not in meter:
            meter["current_reading_type"] = None
        if "multiplier" not in meter:
            meter["multiplier"] = None
        if "usage" not in meter:
            meter["usage"] = None
        # Prefer kWh for electric meters; override common wrong values
        if ("uom" not in meter) or ((meter.get("uom") or "").lower() in ("therms", "therm", "ccf")):
            meter["uom"] = "kWh"
        if "meter_read_type" not in meter:
            meter["meter_read_type"] = None
        
        # Ensure charge_details array exists and has all fields
        if "charge_details" not in meter:
            meter["charge_details"] = []
        
        for charge in meter.get("charge_details", []):
            if "category" not in charge:
                charge["category"] = charge.get("description")
            if "description" not in charge:
                charge["description"] = None
            if "rate" not in charge:
                charge["rate"] = None
            if "rate_x_unit" not in charge:
                charge["rate_x_unit"] = None
            if "charge" not in charge:
                charge["charge"] = None
            if "amount" not in charge:
                charge["amount"] = charge.get("charge")
        
        # Ensure other_charges_and_credits array exists and has all fields
        if "other_charges_and_credits" not in meter:
            meter["other_charges_and_credits"] = []
        
        for charge in meter.get("other_charges_and_credits", []):
            if "category" not in charge:
                charge["category"] = charge.get("description")
            if "description" not in charge:
                charge["description"] = None
            if "rate" not in charge:
                charge["rate"] = None
            if "rate_x_unit" not in charge:
                charge["rate_x_unit"] = None
            if "charge" not in charge:
                charge["charge"] = None
            if "amount" not in charge:
                charge["amount"] = charge.get("charge")
        
        # Ensure taxes array exists
        if "taxes" not in meter:
            meter["taxes"] = []
        
        if "total_current_electric_charges" not in meter:
            meter["total_current_electric_charges"] = None
    
    # Ensure service_types exists
    if "service_types" not in result:
        result["service_types"] = []

    # For PSE Electric, populate service_types from meters
    # Each meter becomes a service entry with line_item_charges from charge_details + other_charges_and_credits + taxes
    meters = result.get("meters", [])
    if meters and len(result.get("service_types", [])) == 0:
        service_types = []
        
        for meter in meters:
            meter_number = meter.get("meter_number", "Unknown")
            total_charges = meter.get("total_current_electric_charges")
            
            # Create service_name using meter number
            service_name = f"Electric Service - Meter {meter_number}" if meter_number else "Electric Service"
            
            # Collect all line item charges from charge_details, other_charges_and_credits, and taxes
            line_item_charges = []
            
            # Add charge_details
            for charge in meter.get("charge_details", []):
                amount = charge.get("amount") or charge.get("charge")
                if amount:
                    line_item_charges.append({
                        "category": charge.get("category") or charge.get("description"),
                        "description": charge.get("description"),
                        "rate": charge.get("rate"),
                        "amount": amount,
                        "meter_number": meter_number,
                        "usage": meter.get("usage"),
                        "uom": meter.get("uom"),
                        "previous_reading": meter.get("previous_reading"),
                        "previous_reading_type": meter.get("previous_reading_type"),
                        "current_reading": meter.get("current_reading"),
                        "current_reading_type": meter.get("current_reading_type"),
                        "usage_multiplier": meter.get("multiplier")
                    })
            
            # Add other_charges_and_credits
            for charge in meter.get("other_charges_and_credits", []):
                amount = charge.get("amount") or charge.get("charge")
                if amount:
                    line_item_charges.append({
                        "category": charge.get("category") or charge.get("description"),
                        "description": charge.get("description"),
                        "rate": charge.get("rate"),
                        "amount": amount,
                        "meter_number": meter_number,
                        "usage": meter.get("usage"),
                        "uom": meter.get("uom"),
                        "previous_reading": meter.get("previous_reading"),
                        "previous_reading_type": meter.get("previous_reading_type"),
                        "current_reading": meter.get("current_reading"),
                        "current_reading_type": meter.get("current_reading_type"),
                        "usage_multiplier": meter.get("multiplier")
                    })
            
            # Add taxes (taxes use "charge" field, not "amount")
            for tax in meter.get("taxes", []):
                tax_amount = tax.get("charge")
                if tax_amount:
                    line_item_charges.append({
                        "category": tax.get("description") or "Tax",
                        "description": tax.get("description"),
                        "rate": tax.get("rate"),
                        "amount": tax_amount,
                        "meter_number": meter_number,
                        "usage": None,
                        "uom": None,
                        "previous_reading": None,
                        "previous_reading_type": None,
                        "current_reading": None,
                        "current_reading_type": None,
                        "usage_multiplier": None
                    })
            
            # Create service entry
            service_entry = {
                "service_name": service_name,
                "current_service": total_charges,
                "service_from_date": meter.get("service_from_date") or meter.get("start_date"),
                "service_to_date": meter.get("service_to_date") or meter.get("end_date"),
                "previous_reading": meter.get("previous_reading"),
                "current_reading": meter.get("current_reading"),
                "line_item_charges": line_item_charges
            }
            
            service_types.append(service_entry)
        
        result["service_types"] = service_types
    
    # Ensure taxes structure exists
    if "taxes" not in result:
        result["taxes"] = {
            "per_service_taxes": [],
            "global_taxes": []
        }

    result = _normalize_pse_multipliers(result)

    return result
    
    # Ensure taxes structure exists
    if "taxes" not in result:
        result["taxes"] = {
            "per_service_taxes": [],
            "global_taxes": []
        }

    result = _normalize_pse_multipliers(result)

    return result