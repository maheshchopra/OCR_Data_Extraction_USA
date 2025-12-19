def ensure_fields(result: dict) -> dict:

    # Service Period
    if "service_period" not in result:
        result["service_period"] = None
    
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

    # For Waste Management, create a consolidated service entry with all line item charges + taxes
    # This allows validation that all charges sum to the total current_billing
    service_types = result.get("service_types", [])
    current_billing = result.get("current_billing")
    
    if service_types and current_billing:
        # Collect all line item charges from all services
        all_line_item_charges = []
        
        for service in service_types:
            line_item_charges = service.get("line_item_charges", [])
            for line_item in line_item_charges:
                # Create a copy of the line item
                charge_entry = {
                    "category": line_item.get("category"),
                    "description": line_item.get("description"),
                    "rate": line_item.get("rate"),
                    "amount": line_item.get("amount") or line_item.get("charge"),
                    "meter_number": line_item.get("meter_number"),
                    "usage": line_item.get("usage"),
                    "uom": line_item.get("uom"),
                    "previous_reading": line_item.get("previous_reading"),
                    "previous_reading_type": line_item.get("previous_reading_type"),
                    "current_reading": line_item.get("current_reading"),
                    "current_reading_type": line_item.get("current_reading_type"),
                    "usage_multiplier": line_item.get("usage_multiplier")
                }
                all_line_item_charges.append(charge_entry)
        
        # Add taxes as line item charges
        taxes = result.get("taxes", {})
        
        # Add per_service_taxes
        per_service_taxes = taxes.get("per_service_taxes", [])
        for tax in per_service_taxes:
            tax_name = tax.get("tax_name")
            tax_amount = tax.get("tax_amount")
            if tax_name and tax_amount:
                all_line_item_charges.append({
                    "category": tax_name,
                    "description": None,
                    "rate": tax.get("tax_rate"),
                    "amount": tax_amount,
                    "meter_number": None,
                    "usage": None,
                    "uom": None,
                    "previous_reading": None,
                    "previous_reading_type": None,
                    "current_reading": None,
                    "current_reading_type": None,
                    "usage_multiplier": None
                })
        
        # Add global_taxes
        global_taxes = taxes.get("global_taxes", [])
        for tax in global_taxes:
            tax_name = tax.get("tax_name")
            tax_amount = tax.get("tax_amount")
            if tax_name and tax_amount:
                all_line_item_charges.append({
                    "category": tax_name,
                    "description": None,
                    "rate": tax.get("tax_rate"),
                    "amount": tax_amount,
                    "meter_number": None,
                    "usage": None,
                    "uom": None,
                    "previous_reading": None,
                    "previous_reading_type": None,
                    "current_reading": None,
                    "current_reading_type": None,
                    "usage_multiplier": None
                })
        
        # Create a consolidated service entry for validation
        # Check if a consolidated service already exists
        consolidated_service_name = "Total Current Charges"
        consolidated_exists = False
        for service in service_types:
            if service.get("service_name") == consolidated_service_name:
                consolidated_exists = True
                # Update the existing consolidated service
                service["current_service"] = current_billing
                service["line_item_charges"] = all_line_item_charges
                break
        
        # If no consolidated service exists, add one
        if not consolidated_exists:
            consolidated_service = {
                "service_name": consolidated_service_name,
                "current_service": current_billing,
                "service_from_date": service_types[0].get("service_from_date") if service_types else None,
                "service_to_date": service_types[0].get("service_to_date") if service_types else None,
                "previous_reading": None,
                "current_reading": None,
                "line_item_charges": all_line_item_charges
            }
            service_types.append(consolidated_service)
            result["service_types"] = service_types

    return result