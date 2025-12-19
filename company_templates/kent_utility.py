def ensure_fields(result: dict) -> dict:

    if "remit_payment_to" not in result:
            result["remit_payment_to"] = None
        
    # Payment Website
    if "payment_website" not in result:
        result["payment_website"] = None

    # Previous Amount Due
    if "previous_amount_due_amount" not in result:
        result["previous_amount_due_amount"] = None

    # Current Usage
    if "current_usage" not in result:
        result["current_usage"] = {
            "previous_reading": None,
            "current_reading": None,
            "usage": None
        }

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

    # Current Usage - ensure it has usage and uom split
    if "current_usage" not in result:
        result["current_usage"] = {
            "previous_reading": None,
            "current_reading": None,
            "usage": None,
            "uom": None
        }
    else:
        # If usage is in old format "25 CCF", split it
        current_usage_obj = result["current_usage"]
        if "usage" in current_usage_obj and "uom" not in current_usage_obj:
            usage_value = current_usage_obj.get("usage")
            if usage_value and isinstance(usage_value, str) and " " in usage_value:
                parts = usage_value.split()
                if len(parts) >= 2:
                    result["current_usage"]["usage"] = parts[0]
                    result["current_usage"]["uom"] = parts[1]
                else:
                    result["current_usage"]["uom"] = None
        elif "uom" not in current_usage_obj:
            result["current_usage"]["uom"] = None

    # Account Information
    if "account_info" not in result:
        result["account_info"] = {
            "account_number": result.get("account_number"),
            "customer_name": result.get("customer_name"),
            "service_address": result.get("service_address")
        }
    
    # Bill Details
    if "bill_details" not in result:
        result["bill_details"] = {
            "bill_date": result.get("bill_date"),
            "due_date": result.get("total_amount_due_date")
        }

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
                        "meter_number": None,
                        "usage": None,
                        "uom": None,
                        "previous_reading": None,
                        "previous_reading_type": None,
                        "current_reading": None,
                        "current_reading_type": None,
                        "usage_multiplier": None
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
                            "meter_number": None,
                            "usage": None,
                            "uom": None,
                            "previous_reading": None,
                            "previous_reading_type": None,
                            "current_reading": None,
                            "current_reading_type": None,
                            "usage_multiplier": None
                        }
                    ]
                else:
                    # Last resort: create entry with all null fields
                    service["line_item_charges"] = [
                        {
                            "category": None,
                            "description": None,
                            "rate": None,
                            "amount": None,
                            "meter_number": None,
                            "usage": None,
                            "uom": None,
                            "previous_reading": None,
                            "previous_reading_type": None,
                            "current_reading": None,
                            "current_reading_type": None,
                            "usage_multiplier": None
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
    
    # Current Charges - CRITICAL: Flatten nested line items into separate service entries
    # This ensures "Access" is extracted as its own service, not nested under Water
    if "current_charges" not in result or len(result.get("current_charges", [])) == 0:
        current_charges = []
        service_types = result.get("service_types", [])
        
        # Track all unique services we've seen to avoid duplicates
        seen_services = set()
        
        for service in service_types:
            service_name = service.get("service_name")
            current_service = service.get("current_service")
            
            # First, add the main service itself
            if service_name and current_service:
                if service_name not in seen_services:
                    current_charges.append({
                        "type": service_name,
                        "amount": current_service
                    })
                    seen_services.add(service_name)
            
            # Then, check line_item_charges for separate services (like Access)
            # that should be their own entries, not nested
            line_items = service.get("line_item_charges", [])
            for item in line_items:
                category = item.get("category")
                amount = item.get("amount")
                
                # If the category is different from the parent service name
                # and looks like a separate service (not just a subcategory),
                # add it as its own service
                if category and amount and category not in seen_services:
                    # Common separate services that might be nested: Access, Technology Fee, etc.
                    separate_service_keywords = ["access", "technology", "tech fee", "stormwater", "surface water"]
                    category_lower = category.lower()
                    
                    is_separate_service = any(keyword in category_lower for keyword in separate_service_keywords)
                    
                    # Also treat it as separate if it's not obviously a subcategory
                    # (subcategories usually contain words like "usage", "base", "charge", "rate")
                    subcategory_keywords = ["usage", "base charge", "rate", "tier", "block"]
                    is_subcategory = any(keyword in category_lower for keyword in subcategory_keywords)
                    
                    if is_separate_service or (not is_subcategory and category != service_name):
                        current_charges.append({
                            "type": category,
                            "amount": amount
                        })
                        seen_services.add(category)
        
        result["current_charges"] = current_charges
    
    # Totals
    if "totals" not in result:
        result["totals"] = {
            "total_current_charges": result.get("current_billing"),
            "total_due": result.get("total_amount_due")
        }

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

    return result