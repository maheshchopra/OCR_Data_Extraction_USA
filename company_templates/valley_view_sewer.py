def ensure_fields(result: dict) -> dict:

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
    if "balance" not in result:
        result["balance"] = None
    if "service_days" not in result:
        result["service_days"] = result.get("number_of_days")
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
    if "meters" not in result:
        result["meters"] = []

    for service in result.get("service_types", []):
        if "line_item_charges" not in service:
            service["line_item_charges"] = []
        
        # First, find the first unit charge rate for this service and check if we need to split line items
        first_unit_charge_rate = None
        first_unit_charge_item = None
        has_units_line_item = False
        
        for line_item in service.get("line_item_charges", []):
            category = line_item.get("category", "").upper()
            if "FIRST UNIT CHARGE" in category or (category.startswith("FIRST") and "UNIT" in category and "CHARGE" in category):
                first_unit_charge_item = line_item
                rate_str = line_item.get("rate")
                if rate_str:
                    try:
                        first_unit_charge_rate = float(str(rate_str).replace('$', '').replace(',', '').strip())
                    except (ValueError, TypeError):
                        pass
            else:
                # Check if there's already a units line item (e.g., "95 Units", "95 UNITS @")
                if "UNITS" in category or "UNIT @" in category:
                    has_units_line_item = True
        
        # If we have a First Unit Charge with usage > 1 and no separate units line item, create one
        # This handles cases where extraction incorrectly put usage on the First Unit Charge
        if first_unit_charge_item and first_unit_charge_rate and not has_units_line_item:
            usage_str = first_unit_charge_item.get("usage")
            if usage_str:
                try:
                    usage = float(str(usage_str).replace(',', '').strip())
                    if usage > 1:
                        # Fix the First Unit Charge to have usage = 1
                        first_unit_charge_item["usage"] = "1"
                        first_unit_charge_item["uom"] = "Unit"
                        
                        # Create a new line item for the units (usage should be the full amount, e.g., 95)
                        # Formula: (first_unit_rate * usage) + first_unit_rate
                        calculated_amount = (first_unit_charge_rate * usage) + first_unit_charge_rate
                        
                        units_line_item = {
                            "category": f"{int(usage)} Units",
                            "description": None,
                            "rate": str(first_unit_charge_rate),
                            "amount": f"{calculated_amount:.2f}",
                            "meter_number": None,
                            "usage": str(int(usage)),
                            "uom": "Units",
                            "previous_reading": None,
                            "previous_reading_type": None,
                            "current_reading": None,
                            "current_reading_type": None,
                            "usage_multiplier": None
                        }
                        service["line_item_charges"].append(units_line_item)
                except (ValueError, TypeError):
                    pass
        
        # Now process all line items
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

            # Recalculate amount based on line item type
            rate_str = line_item.get("rate")
            usage_str = line_item.get("usage")
            category = line_item.get("category", "").upper()
            
            if rate_str and usage_str:
                try:
                    # Parse rate and usage as floats
                    rate = float(str(rate_str).replace('$', '').replace(',', '').strip())
                    usage = float(str(usage_str).replace(',', '').strip())
                    
                    # Check if this is a "FIRST UNIT CHARGE" line item
                    if "FIRST UNIT CHARGE" in category or (category.startswith("FIRST") and "UNIT" in category and "CHARGE" in category):
                        # For first unit charge, the amount should just be the rate, and usage should be 1
                        calculated_amount = rate
                        line_item["usage"] = "1"
                    else:
                        # For other line items (like "95 UNITS @"), use: (first_unit_charge_rate * usage) + first_unit_charge_rate
                        # Use the first_unit_charge_rate if we found it, otherwise use the current rate
                        charge_rate = first_unit_charge_rate if first_unit_charge_rate is not None else rate
                        calculated_amount = (charge_rate * usage) + charge_rate
                    
                    # Update the amount field
                    line_item["amount"] = f"{calculated_amount:.2f}"
                except (ValueError, TypeError):
                    # If parsing fails, keep the original amount
                    pass

    if "taxes" not in result:
        result["taxes"] = {
            "per_service_taxes": [],
            "global_taxes": []
        }
    if "adjustments" not in result:
        result["adjustments"] = []
    if "payments_applied" not in result:
        result["payments_applied"] = []

    return result