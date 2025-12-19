import sys

def ensure_fields(result: dict) -> dict:
    # Ensure new top-level fields exist
    if "provider_website" not in result:
        result["provider_website"] = None
    if "provider_customer_service_phone" not in result:
        result["provider_customer_service_phone"] = None
    if "provider_customer_service_email" not in result:
        result["provider_customer_service_email"] = None
    if "service_days" not in result:
        # Map from number_of_days if available
        result["service_days"] = result.get("number_of_days")
    if "description" not in result:
        result["description"] = None

    if "provider_info" not in result:
        result["provider_info"] = {
            "provider_address": None,
            "provider_return_address": None
        }
    
    # Ensure bill_info exists
    if "bill_info" not in result:
        result["bill_info"] = {
            "bill_number": None,
            "bill_type": None
        }
    
    # Ensure balance_info exists
    if "balance_info" not in result:
        result["balance_info"] = {
            "current_balance": None,
            "balance_after_due_date": None
        }
    
    # Ensure meters exists
    if "meters" not in result or not result["meters"] or len(result["meters"]) == 0:
        result["meters"] = [
            {
                "meter_number": None,
                "meter_location": None,
                "service_type": None,
                "read_date": None,
                "previous_reading": None,
                "previous_reading_type": None,
                "current_reading": None,
                "current_reading_type": None,
                "usage": None,
                "uom": None,
                "multiplier": None,
                "read_type": None
            }
        ]
    else:
        # Ensure each existing meter has all fields
        for meter in result.get("meters", []):
            if "previous_reading_type" not in meter:
                meter["previous_reading_type"] = None
            if "current_reading_type" not in meter:
                meter["current_reading_type"] = None

    # Ensure line_item_charges in service_types have all fields
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
                # Match service_name with charge type (handle variations like "Storm: Stormwater" vs "Storm:Stormwater")
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

    if "agency_information" not in result or not result["agency_information"]:
        # Use a standard default for City of Redmond
        result["agency_information"] = "City of Redmond, PO Box 97010, Redmond, WA 98073"
    
    # Populate account_information
    if "account_information" not in result:
        result["account_information"] = {
            "account_number": result.get("account_number"),
            "customer_name": result.get("customer_name"),
            "service_address": result.get("service_address"),
            "billing_address": result.get("billing_address")
        }
    
    # Populate bill_details - ensure structure exists
    if "bill_details" not in result:
        result["bill_details"] = {}

    if not result.get("bill_details", {}).get("service_period"):
        service_period = None

        # Try to calculate from bill_date and number_of_days
        if result.get("bill_date") and result.get("number_of_days"):
            try:
                from datetime import datetime, timedelta
                
                # Parse bill date
                bill_date_str = result.get("bill_date")
                num_days_str = result.get("number_of_days")

                # Try to parse the date (handle multiple formats)
                bill_date = None
                for fmt in ["%B %d %Y", "%b %d %Y", "%m/%d/%Y"]:
                    try:
                        bill_date = datetime.strptime(bill_date_str, fmt)
                        break
                    except ValueError:
                        continue
                
                if bill_date:
                    num_days = int(num_days_str)
                    
                    # Calculate start date (bill date minus number of days)
                    start_date = bill_date - timedelta(days=num_days)
                    
                    # Format the service period (Windows-compatible)
                    start_str = f"{start_date.month}/{start_date.day}/{start_date.year}"
                    end_str = f"{bill_date.month}/{bill_date.day}/{bill_date.year}"
                    service_period = f"{start_str} to {end_str} ({num_days} days)"
                    
                    print(f"Calculated service_period: {service_period}", file=sys.stderr)
                
            except Exception as e:
                print(f"Warning: Could not calculate service period: {e}", file=sys.stderr)
        
        # Set the service_period (will be None if calculation failed)
        result["bill_details"]["service_period"] = service_period

    # Ensure bill_details fields are populated from base fields if missing
    if "billing_date" not in result["bill_details"] or not result["bill_details"]["billing_date"]:
        result["bill_details"]["billing_date"] = result.get("bill_date")

    if "due_date" not in result["bill_details"] or not result["bill_details"]["due_date"]:
        result["bill_details"]["due_date"] = result.get("total_amount_due_date")
    
    # Populate current_charges from service_types if empty
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
    
    # Populate bill_summary - try to find payments_received from payments_applied
    if "bill_summary" not in result:
        result["bill_summary"] = {}
    
    # Check if payments_received is missing and try to populate it
    if not result["bill_summary"].get("payments_received"):
        # Try to get from payments_applied array
        payments_applied = result.get("payments_applied", [])
        if payments_applied and len(payments_applied) > 0:
            # Sum up all payments
            total_payments = 0.0
            for payment in payments_applied:
                payment_amount = payment.get("payment_amount")
                if payment_amount:
                    # Parse dollar amount
                    cleaned = str(payment_amount).replace('$', '').replace(',', '').strip()
                    try:
                        total_payments += float(cleaned)
                    except:
                        pass
            
            if total_payments > 0:
                result["bill_summary"]["payments_received"] = f"${total_payments:.2f}"
    
    # Ensure all bill_summary fields exist
    result["bill_summary"]["previous_balance"] = result["bill_summary"].get("previous_balance") or result.get("previous_balance")
    result["bill_summary"]["current_charges"] = result["bill_summary"].get("current_charges") or result.get("current_billing")
    result["bill_summary"]["adjustments"] = result["bill_summary"].get("adjustments") or result.get("current_adjustments")
    result["bill_summary"]["total_amount_due"] = result["bill_summary"].get("total_amount_due") or result.get("total_amount_due")

    return result