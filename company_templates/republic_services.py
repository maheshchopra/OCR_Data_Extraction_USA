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
        result["service_days"] = None
    
    # Company Address
    if "company_address" not in result:
        result["company_address"] = None
    
    # Contact Information
    if "contact_info" not in result:
        result["contact_info"] = {
            "phone_number": None,
            "support_website": None
        }
    else:
        # Ensure all subfields exist
        if "phone_number" not in result["contact_info"]:
            result["contact_info"]["phone_number"] = None
        if "support_website" not in result["contact_info"]:
            result["contact_info"]["support_website"] = None
    
    # Payment Website
    if "payment_website" not in result:
        result["payment_website"] = None
    
    # Late Fee
    if "late_fee" not in result:
        result["late_fee"] = {
            "percentage": None,
            "description": None
        }
    else:
        # Ensure all subfields exist
        if "percentage" not in result["late_fee"]:
            result["late_fee"]["percentage"] = None
        if "description" not in result["late_fee"]:
            result["late_fee"]["description"] = None
    
    # Late Fee Info (detailed)
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

    # For Republic Services, add taxes to line_item_charges for validation
    # Taxes are shown in the "Amount" column and should be included in the total
    for service in result.get("service_types", []):
        line_item_charges = service.get("line_item_charges", [])
        
        # Get taxes from the result
        taxes = result.get("taxes", {})
        global_taxes = taxes.get("global_taxes", [])
        
        # Add each global tax as a line item charge
        for tax in global_taxes:
            tax_name = tax.get("tax_name")
            tax_amount = tax.get("tax_amount")
            
            if tax_name and tax_amount:
                # Check if this tax is already in line_item_charges
                tax_already_exists = False
                for line_item in line_item_charges:
                    if line_item.get("category") == tax_name:
                        tax_already_exists = True
                        break
                
                # Only add if not already present
                if not tax_already_exists:
                    line_item_charges.append({
                        "category": tax_name,
                        "description": None,
                        "rate": None,
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
        
        # Update the service with the modified line_item_charges
        service["line_item_charges"] = line_item_charges

    return result