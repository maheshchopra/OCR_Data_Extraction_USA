def ensure_fields(result: dict) -> dict:
    # Provider Address
    if "provider_address" not in result:
        result["provider_address"] = None

    # Balance Information
    if "balance_info" not in result:
        result["balance_info"] = {
            "current_balance": None,
            "balance_after_due_date": None
        }
    
    # Meters - ensure at least one meter with null values if empty
    if "meters" not in result or not result["meters"] or len(result["meters"]) == 0:
        result["meters"] = [
            {
                "meter_number": None,
                "meter_location": None,
                "service_type": None,
                "read_date": None,
                "previous_reading": None,
                "current_reading": None,
                "usage": None,
                "uom": None,
                "multiplier": None,
                "read_type": None
            }
        ]
        
    # Contact Information - just phone number
    if "contact_info" not in result:
        result["contact_info"] = {}
    
    if "phone_number" not in result["contact_info"]:
        result["contact_info"]["phone_number"] = None

    if "website" not in result["contact_info"]:
        result["contact_info"]["website"] = None
    
    # Account Information
    if "account_info" not in result:
        result["account_info"] = {
            "account_number": result.get("account_number"),
            "service_address": result.get("service_address")
        }
    
    # Bill Details
    if "bill_details" not in result:
        result["bill_details"] = {
            "date_billed": result.get("bill_date"),
            "due_date": result.get("total_amount_due_date")
        }
    
    # Current Charges - populate from service_types if empty
    if "current_charges" not in result or len(result.get("current_charges", [])) == 0:
        current_charges = []
        service_types = result.get("service_types", [])
        for service in service_types:
            service_name = service.get("service_name")
            current_service = service.get("current_service")
            if service_name and current_service:
                current_charges.append({
                    "type": service_name,
                    "amount": current_service
                })
        result["current_charges"] = current_charges
    
    # Ensure line_item_charges in service_types are populated from current_charges
    for service in result.get("service_types", []):
        service_name = service.get("service_name")
        current_service = service.get("current_service")
        
        # If line_item_charges is empty or missing, populate from current_charges
        if (
            "line_item_charges" not in service
            or not service.get("line_item_charges")
            or len(service.get("line_item_charges", [])) == 0
        ):
            # Try to find matching entry in current_charges
            matching_charge = None
            current_charges = result.get("current_charges", [])
            
            for charge in current_charges:
                charge_type = charge.get("type", "")
                # Match service_name with charge type (handle variations)
                if charge_type and service_name:
                    # Normalize both strings for comparison (remove extra spaces, case insensitive)
                    normalized_charge_type = " ".join(charge_type.split()).lower()
                    normalized_service_name = " ".join(service_name.split()).lower()
                    if normalized_charge_type == normalized_service_name:
                        matching_charge = charge
                        break
            
            # If we found a matching charge, use its amount
            if matching_charge:
                charge_amount = matching_charge.get("amount")
                service["line_item_charges"] = [
                    {
                        "category": service_name,  # Use service_name as category
                        "description": None,
                        "rate": None,
                        "amount": charge_amount,  # Populate from current_charges
                        "meter_number": service.get("meter_number"),
                        "usage": service.get("usage"),
                        "uom": service.get("uom"),
                        "previous_reading": service.get("previous_reading"),
                        "previous_reading_type": service.get("previous_reading_type"),
                        "current_reading": service.get("current_reading"),
                        "current_reading_type": service.get("current_reading_type"),
                        "usage_multiplier": service.get("usage_multiplier")
                    }
                ]
            else:
                # Fallback: use current_service amount if available
                if current_service:
                    service["line_item_charges"] = [
                        {
                            "category": service_name,
                            "description": None,
                            "rate": None,
                            "amount": current_service,
                            "meter_number": service.get("meter_number"),
                            "usage": service.get("usage"),
                            "uom": service.get("uom"),
                            "previous_reading": service.get("previous_reading"),
                            "previous_reading_type": service.get("previous_reading_type"),
                            "current_reading": service.get("current_reading"),
                            "current_reading_type": service.get("current_reading_type"),
                            "usage_multiplier": service.get("usage_multiplier")
                        }
                    ]
        else:
            # If line_item_charges exist, ensure each one has all fields
            for line_item in service.get("line_item_charges", []):
                # Ensure all fields exist with null defaults
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
    
    # Create a consolidated service entry for validation
    # This validates that all current_charges sum to total_current_charges
    current_charges = result.get("current_charges", [])
    totals = result.get("totals", {})
    total_current_charges = totals.get("total_current_charges") or result.get("current_billing")
    
    if current_charges and total_current_charges:
        # Collect all line item charges from current_charges
        all_line_item_charges = []
        
        for charge in current_charges:
            charge_type = charge.get("type")
            charge_amount = charge.get("amount")
            
            if charge_type and charge_amount:
                all_line_item_charges.append({
                    "category": charge_type,
                    "description": None,
                    "rate": None,
                    "amount": charge_amount,
                    "meter_number": None,
                    "usage": None,
                    "uom": None,
                    "previous_reading": None,
                    "previous_reading_type": None,
                    "current_reading": None,
                    "current_reading_type": None,
                    "usage_multiplier": None
                })
        
        # Check if a consolidated service already exists
        consolidated_service_name = "Total Current Charges"
        service_types = result.get("service_types", [])
        consolidated_exists = False
        
        for service in service_types:
            if service.get("service_name") == consolidated_service_name:
                consolidated_exists = True
                # Update the existing consolidated service
                service["current_service"] = total_current_charges
                service["line_item_charges"] = all_line_item_charges
                break
        
        # If no consolidated service exists, add one
        if not consolidated_exists:
            consolidated_service = {
                "service_name": consolidated_service_name,
                "current_service": total_current_charges,
                "service_from_date": service_types[0].get("service_from_date") if service_types else None,
                "service_to_date": service_types[0].get("service_to_date") if service_types else None,
                "previous_reading": None,
                "current_reading": None,
                "line_item_charges": all_line_item_charges
            }
            service_types.append(consolidated_service)
            result["service_types"] = service_types
    
    # Totals
    if "totals" not in result:
        result["totals"] = {
            "total_current_charges": result.get("current_billing"),
            "total_due": result.get("total_amount_due")
        }
    
    # Consumption - split into usage and uom if it's still combined
    if "consumption" not in result:
        usage_value = None
        uom_value = None
        # Try to get consumption from service_types (water service typically has CCF usage)
        service_types = result.get("service_types", [])
        for service in service_types:
            if "water" in service.get("service_name", "").lower():
                # Check line_item_charges for usage
                line_items = service.get("line_item_charges", [])
                for item in line_items:
                    usage = item.get("usage")
                    uom = item.get("uom")
                    if usage:
                        usage_value = usage
                        uom_value = uom if uom else "CCF"
                        break
                if usage_value:
                    break
        
        result["consumption"] = {
            "usage": usage_value,
            "uom": uom_value
        }
    else:
        # If consumption exists but is in old format "134 CCF", split it
        consumption = result["consumption"]
        if isinstance(consumption, dict):
            if "current_consumption" in consumption and ("usage" not in consumption or "uom" not in consumption):
                # Old format - need to split
                current_consumption = consumption.get("current_consumption")
                if current_consumption and isinstance(current_consumption, str):
                    parts = current_consumption.split()
                    if len(parts) >= 2:
                        result["consumption"] = {
                            "usage": parts[0],
                            "uom": parts[1]
                        }
                    else:
                        result["consumption"] = {
                            "usage": current_consumption,
                            "uom": None
                        }
    return result