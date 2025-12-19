from PIL.Image import Image
import os
import sys
import json
import argparse
import base64
import glob
import shutil
from typing import Any, Optional, List
import atexit
from datetime import datetime
import pandas as pd
from openai import OpenAI

# Import prompt templates for different bill formats
import prompt_templates

def _readable_err(msg: str) -> None:
    print(msg, file=sys.stderr)


def ensure_template_specific_fields(result: dict, detected_company: str) -> dict:
    """
    Ensure that template-specific fields are present in the result, even if null.
    
    Args:
        result (dict): The extracted data
        detected_company (str): The detected company name
        
    Returns:
        dict: Updated result with template-specific fields
    """
    # Ensure global top-level fields exist for all templates
    general_top_level_fields = [
        "provider_website",
        "provider_customer_service_phone",
        "provider_customer_service_email",
        "provider_address",
        "provider_return_address",
        "bill_number",
        "bill_type",
        "balance",
        "service_days",
        "description"
    ]
    for field in general_top_level_fields:
        if field not in result:
            if field == "service_days" and "number_of_days" in result:
                result[field] = result.get("number_of_days")
            else:
                result[field] = None

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
        late_fee_defaults = {
            "latefee_applied": None,
            "latefee_date": None,
            "latefee_amount": None,
            "latefee_by_duedate_percentage": None,
            "latefee_by_duedate": None,
            "total_amount_with_latefee_by_duedate": None
        }
        for key, default in late_fee_defaults.items():
            if key not in result["late_fee_info"]:
                result["late_fee_info"][key] = default

    # Import and call company-specific template handler
    from company_templates import get_company_handler
    
    handler = get_company_handler(detected_company)
    if handler:
        result = handler(result)
    
    return result


def detect_company_from_pdf(pdf_path: str, client: OpenAI) -> Optional[str]:
    """
    Detect the company/provider name by scanning the PDF content using AI.
    
    Args:
        pdf_path: Path to the PDF file
        client: OpenAI client instance
        
    Returns:
        Detected company name that matches a company in COMPANY_MODULE_MAP, or None
    """
    try:
        from pdf2image import convert_from_path
        from company_templates import get_all_company_names
    except ImportError:
        return None

    # Get all possible company names
    company_names = get_all_company_names()
    
    # Convert only the first page to image (faster and cheaper)
    try:
        images = convert_from_path(pdf_path, dpi=200, first_page=1, last_page=1)
        if not images:
            return None
    except Exception as e:
        print(f"Warning: Could not convert PDF to image for company detection: {e}", file=sys.stderr)
        return None
    
    # Prepare the first page image
    image = images[0]
    temp_image_path = "temp_company_detection.png"
    
    try:
        image.save(temp_image_path, "PNG", optimize=True)
        
        # Read and encode the image
        with open(temp_image_path, "rb") as img_file:
            image_data = img_file.read()
            image_base64 = base64.b64encode(image_data).decode('utf-8')
        
        # Create a prompt that asks GPT to identify the provider name
        company_list = "\n".join([f"- {name}" for name in company_names])
        detection_prompt = f"""Look at this utility bill and identify the provider/company name.

        The provider name should match one of these supported companies:
        {company_list}

        Analyze the bill header, logo, address, or any company identification visible on the bill. Return your response as a JSON object with this exact format:
        {{
            "detected_provider_name": "exact company name from the list above, or null if not found"
        }}

        IMPORTANT RULE FOR PUGET SOUND ENERGY:
        - If the provider is Puget Sound Energy AND you see the words "Natural Gas" anywhere on the page,
          you MUST return "Puget Sound Energy - Gas" (NOT "Puget Sound Energy").

        Only return the exact company name from the list provided, or null if you cannot find a match. Be precise with spelling and capitalization."""
        
        # Send to GPT-4o vision model for company detection
        response = client.chat.completions.create(
            model="gpt-4o",
            messages=[
                {
                    "role": "user",
                    "content": [
                        {"type": "text", "text": detection_prompt},
                        {
                            "type": "image_url",
                            "image_url": {
                                "url": f"data:image/png;base64,{image_base64}",
                                "detail": "high"
                            }
                        }
                    ]
                }
            ],
            response_format={"type": "json_object"},
            max_tokens=500,
            temperature=0
        )
        
        # Parse the response
        if response.choices and response.choices[0].message.content:
            text = response.choices[0].message.content.strip()
            try:
                detection_result = json.loads(text)
                detected_name = detection_result.get("detected_provider_name")
                
                # Verify the detected name matches one in our list
                if detected_name and detected_name in company_names:
                    return detected_name
            except json.JSONDecodeError:
                pass
        
        return None
        
    except Exception as e:
        print(f"Warning: Error during AI-based company detection: {e}", file=sys.stderr)
        return None
    finally:
        # Clean up temporary image file
        try:
            if os.path.exists(temp_image_path):
                os.remove(temp_image_path)
        except Exception:
            pass


def extract_bill_data_via_llm(pdf_path: str) -> dict:
    if not os.path.isfile(pdf_path):
        raise FileNotFoundError(f"File not found: {pdf_path}")

    api_key = os.getenv("OPENAI_API_KEY")
    if not api_key:
        raise RuntimeError(
            "OPENAI_API_KEY is not set. Set it in your environment before running this script."
        )

    client = OpenAI(api_key=api_key)
    
    # Detect company from filename and select appropriate prompt
    filename = os.path.basename(pdf_path)
    detected_company = prompt_templates.detect_company_from_filename(filename)

    # If filename detection fails, try AI-based detection from PDF content
    if not detected_company:
        print(f"Filename detection failed. Attempting AI-based detection from PDF content...", file=sys.stderr)
        detected_company = detect_company_from_pdf(pdf_path, client)
        if detected_company:
            print(f"AI detected company: {detected_company}", file=sys.stderr)
        else:
            print(f"AI detection also failed. Using default template.", file=sys.stderr)

    # PSE service-type detection:
    # PSE PDFs are often image-only, so text extraction can fail. Use a lightweight vision check
    # to decide between gas vs electric before selecting the extraction prompt.
    if detected_company in ("Puget Sound Energy", "Puget Sound Energy - Gas"):
        pse_kind = detect_pse_service_type_from_pdf(pdf_path, client)
        if pse_kind == "gas":
            detected_company = "Puget Sound Energy - Gas"
        elif pse_kind == "electric":
            detected_company = "Puget Sound Energy"
    
    if detected_company:
        selected_prompt = prompt_templates.get_prompt_for_company(detected_company)
        print(f"Detected company: {detected_company} - Using specialized template", file=sys.stderr)
    else:
        selected_prompt = None
    
    # Fall back to default prompt if no template matched
    if not selected_prompt:
        selected_prompt = prompt_templates.get_default_prompt()
        print(f"No specific template detected - Using default template", file=sys.stderr)

    # Initialize variables
    account_number = None
    account_type = None
    customer_name = None
    service_address = None
    billing_address = None
    previous_balance = None
    current_billing = None
    current_adjustments = None
    total_amount_due = None
    total_amount_due_date = None
    bill_date = None
    number_of_days = None
    payment_information = {"payment_date": None, "payment_amount": None}
    payments_applied = []
    adjustments = []
    taxes = {"per_service_taxes": [], "global_taxes": []}
    service_types = []
    
    # Convert PDF pages to images
    try:
        from pdf2image import convert_from_path
    except ImportError:
        raise ImportError("pdf2image library not found. Install it with: pip install pdf2image")

    print(f"Converting PDF to images...", file=sys.stderr)
    images = convert_from_path(pdf_path, dpi=300)  # Higher DPI for better quality
    
    print(f"Processing {len(images)} page(s) with GPT-4o Vision...", file=sys.stderr)
    
    # Process all pages together - send all images to the vision model at once
    image_messages = []
    temp_files = []
    
    try:
        # Prepare all images as base64
        for i, image in enumerate[Image](images, 1):
            print(f"  Encoding page {i}/{len(images)}...", file=sys.stderr)
            
            # Save image to temporary file
            temp_image_path = f"temp_page_{i}.png"
            temp_files.append(temp_image_path)
            image.save(temp_image_path, "PNG", optimize=True)
            
            # Read and encode the image
            with open(temp_image_path, "rb") as img_file:
                image_data = img_file.read()
                image_base64 = base64.b64encode(image_data).decode('utf-8')
            
            # Add image to messages
            image_messages.append({
                "type": "image_url",
                "image_url": {
                    "url": f"data:image/png;base64,{image_base64}",
                    "detail": "high"  # Use high detail for better extraction
                }
            })
        
        # Create the message content with prompt and all images
        message_content = [{"type": "text", "text": selected_prompt}] + image_messages
        
        print(f"Sending images to GPT-4o Vision API...", file=sys.stderr)
        
        # Send to GPT-4o vision model
        response = client.chat.completions.create(
            model="gpt-4o",
            messages=[
                {
                    "role": "user",
                    "content": message_content
                }
            ],
            response_format={"type": "json_object"},
            max_tokens=16000,  # Increased for larger bills with multiple pages
            temperature=0
        )
        
        # Extract the response content
        if response.choices and response.choices[0].message.content:
            # print("\nTEXT RESPONSE")
            text = response.choices[0].message.content.strip()
            # print(text)
            # print("\nEND OF TEXT RESPONSE")
            
            
            try:
                # print("\nDATA")
                data = json.loads(text)
                # print(data)
                # print("\nEND OF DATA")
                account_number = data.get("account_number")
                account_type = data.get("account_type")
                customer_name = data.get("customer_name")
                service_address = data.get("service_address")
                billing_address = data.get("billing_address")
                previous_balance = data.get("previous_balance")
                current_billing = data.get("current_billing")
                current_adjustments = data.get("current_adjustments")
                total_amount_due = data.get("total_amount_due")
                total_amount_due_date = data.get("total_amount_due_date")
                bill_date = data.get("bill_date")
                number_of_days = data.get("number_of_days")
                payment_information = data.get("payment_information", {"payment_date": None, "payment_amount": None})
                payments_applied = data.get("payments_applied", [])
                adjustments = data.get("adjustments", [])
                taxes = data.get("taxes", {"per_service_taxes": [], "global_taxes": []})
                service_types = data.get("service_types", [])
                
                print(f"Successfully extracted data from {len(images)} page(s)", file=sys.stderr)
                
            except json.JSONDecodeError as json_err:
                print(f"JSON decode error: {json_err}", file=sys.stderr)
                print(f"Response text preview: {text[:500]}...", file=sys.stderr)
                raise RuntimeError("Failed to parse JSON response from GPT-4o")
        else:
            raise RuntimeError("No response from GPT-4o Vision API")
    
    finally:
        # Clean up temporary image files
        for temp_file in temp_files:
            try:
                if os.path.exists(temp_file):
                    os.remove(temp_file)
            except Exception as e:
                print(f"Warning: Could not delete temporary file {temp_file}: {e}", file=sys.stderr)

    # Validate that current service amounts sum to current billing
    # For company-specific validations, we need to pass the result after template fields are populated
    # So we'll do validation after ensure_template_specific_fields
    validation_result = None 

    result = data.copy()

    result.update({
        "account_number": account_number,
        "account_type": account_type,
        "customer_name": customer_name,
        "service_address": service_address,
        "billing_address": billing_address,
        "previous_balance": previous_balance,
        "current_billing": current_billing,
        "current_adjustments": current_adjustments,
        "total_amount_due": total_amount_due,
        "total_amount_due_date": total_amount_due_date,
        "bill_date": bill_date,
        "number_of_days": number_of_days,
        "payment_information": payment_information,
        "payments_applied": payments_applied,
        "adjustments": adjustments,
        "taxes": taxes,
        "service_types": service_types,
        "billing_validation": validation_result
    })
    
    
    # Ensure template-specific fields are present
    result = ensure_template_specific_fields(result, detected_company)

    # Enforce PSE account/meter type based on detected template (model sometimes flips these).
    if detected_company == "Puget Sound Energy - Gas":
        result["account_type"] = "Gas"
        for m in result.get("meters", []) or []:
            if isinstance(m, dict):
                m["service_type"] = "Gas"
                # If the model mistakenly wrote kWh, prefer therms when missing/incorrect
                if (m.get("uom") or "").lower() in ("kwh", "kw h", "kilowatt hours", "kilowatt-hour"):
                    m["uom"] = "Therms"
    elif detected_company == "Puget Sound Energy":
        result["account_type"] = "Electric"
        for m in result.get("meters", []) or []:
            if isinstance(m, dict):
                m["service_type"] = "Electric"
                if (m.get("uom") or "").lower() in ("therms", "therm", "ccf"):
                    m["uom"] = "kWh"

    # Validate billing amounts using company-specific charge structure
    if detected_company == "Everett Public Works":
        # For Everett, use current_charges for validation
        current_charges_list = result.get("current_charges", [])
        # Convert current_charges to service_types format for validation
        service_types_for_validation = []
        for charge in current_charges_list:
            service_types_for_validation.append({
                "service_name": charge.get("type"),
                "current_service": charge.get("amount")
            })
        validation_result = validate_billing_amounts(
            result.get("current_billing"), 
            service_types_for_validation, 
            result.get("current_adjustments")
        )
    elif detected_company == "Kent Utility":
        # For Kent, use current_charges for validation
        current_charges_list = result.get("current_charges", [])
        # Convert current_charges to service_types format for validation
        service_types_for_validation = []
        for charge in current_charges_list:
            service_types_for_validation.append({
                "service_name": charge.get("type"),
                "current_service": charge.get("amount")
            })
        validation_result = validate_billing_amounts(
            result.get("current_billing"), 
            service_types_for_validation, 
            result.get("current_adjustments")
        )
    elif detected_company == "City of Redmond":
        # For Redmond, use current_charges for validation
        current_charges_list = result.get("current_charges", [])
        # Convert current_charges to service_types format for validation
        service_types_for_validation = []
        for charge in current_charges_list:
            service_types_for_validation.append({
                "service_name": charge.get("type"),
                "current_service": charge.get("amount")
            })
        validation_result = validate_billing_amounts(
            result.get("current_billing"), 
            service_types_for_validation, 
            result.get("current_adjustments")
        )

    elif detected_company == "Puget Sound Energy":
        # For PSE Electric, validate that sum of all meter totals equals total_amount_due
        validation_result = validate_meter_based_billing(
            result.get("total_amount_due"),
            result.get("meters", []),
            result.get("previous_balance")
        )

    elif detected_company == "Puget Sound Energy - Gas":
        # For PSE Gas, validate that sum of all meter totals equals total_amount_due
        validation_result = validate_meter_based_billing(
            result.get("total_amount_due"),
            result.get("meters", []),
            result.get("previous_balance")
        )

    elif detected_company == "Seattle City Light":
        # For Seattle City Light, prefer amounts from the detailed billing CSV if available
        # Fallback to the extracted amounts array otherwise
        amounts_for_validation = result.get("amounts", []) or []
        try:
            source_filename = os.path.splitext(os.path.basename(pdf_path))[0]
            script_dir = os.path.dirname(os.path.abspath(__file__))
            csv_path = os.path.join(script_dir, "processed", "detailed_billing", f"{source_filename}_detailed_billing.csv")
            if os.path.exists(csv_path):
                df = pd.read_csv(csv_path)
                if "amount" in df.columns:
                    # Keep only non-null, non-empty amounts
                    amounts_for_validation = []
                    for a in df["amount"].tolist():
                        if a is None:
                            continue
                        s = str(a).strip()
                        if s == "" or s.lower() in ("null", "none", "nan"):
                            continue
                        amounts_for_validation.append(s)
                    # Also update the result amounts so the JSON reflects the CSV values
                    result["amounts"] = amounts_for_validation
        except Exception:
            # Best-effort; fall back to existing amounts
            pass

        validation_result = validate_amounts_based_billing(
            result.get("current_billing"),
            amounts_for_validation
        )

    elif detected_company == "Seattle Public Utilities":
        # For SPU, validate Total Amount Due including previous balance and payments applied.
        validation_result = validate_seattle_public_utilities_total_amount_due(
            result.get("total_amount_due"),
            result.get("service_types", []),
            result.get("current_adjustments"),
            result.get("balance"),
            result.get("previous_balance"),
            result.get("payments_applied", []),
        )

    elif detected_company == "Waste Management of Washington":
        # For Waste Management, validate using services + taxes
        validation_result = validate_waste_management_billing(
            result.get("current_billing"),
            result.get("service_types", []),
            result.get("taxes", {}),
            result.get("current_adjustments")
        )

    elif detected_company == "Recology Waste Services":
        # For Recology Waste Services, validate using services + taxes
        validation_result = validate_waste_management_billing(
            result.get("current_billing"),
            result.get("service_types", []),
            result.get("taxes", {}),
            result.get("current_adjustments")
        )
    
    elif detected_company == "City of Bothell":
        # For City of Bothell, all service charges and taxes are in service_types
        # Sum all service_types (which includes taxes) for validation
        validation_result = validate_billing_amounts(
            result.get("current_billing"), 
            result.get("service_types", []), 
            result.get("current_adjustments")
        )
    
    elif detected_company == "City of Edmonds":
        # Use service_types and adjustments for validation
        validation_result = validate_billing_amounts(
            result.get("current_billing"),
            result.get("service_types", []),
            result.get("current_adjustments")
        )

    elif detected_company == "City of Frisco":
        # Use service_types and adjustments for validation
        validation_result = validate_billing_amounts(
            result.get("current_billing"),
            result.get("service_types", []),
            result.get("current_adjustments")
        )

    elif detected_company == "City of Lacey":
        # Use service_types and adjustments for validation
        validation_result = validate_billing_amounts(
            result.get("current_billing"),
            result.get("service_types", []),
            result.get("current_adjustments")
        )

    elif detected_company == "City of Ocean Shores":
        # Use service_types and adjustments for validation
        validation_result = validate_billing_amounts(
            result.get("current_billing"),
            result.get("service_types", []),
            result.get("current_adjustments")
        )

    elif detected_company == "City of Olympia":
        # Use service_types and adjustments for validation
        validation_result = validate_billing_amounts(
            result.get("current_billing"),
            result.get("service_types", []),
            result.get("current_adjustments")
        )

    elif detected_company == "City of Renton":
        # Use service_types and adjustments for validation
        validation_result = validate_billing_amounts(
            result.get("current_billing"),
            result.get("service_types", []),
            result.get("current_adjustments")
        )

    elif detected_company == "Grays Harbor PUD":
        # Use service_types and adjustments for validation
        validation_result = validate_billing_amounts(
            result.get("current_billing"),
            result.get("service_types", []),
            result.get("current_adjustments")
        )

    elif detected_company == "City of Lynnwood":
        # Use service_types and adjustments for validation
        validation_result = validate_billing_amounts(
            result.get("current_billing"),
            result.get("service_types", []),
            result.get("current_adjustments")
        )

    elif detected_company == "Southwest Suburban Sewer District":
        # Use service_types and adjustments for validation
        validation_result = validate_billing_amounts(
            result.get("current_billing"),
            result.get("service_types", []),
            result.get("current_adjustments")
        )

    elif detected_company == "Valley View Sewer District":
        # Use service_types and adjustments for validation
        validation_result = validate_billing_amounts(
            result.get("current_billing"),
            result.get("service_types", []),
            result.get("current_adjustments")
        )

    elif detected_company == "King County Water District":
        # Use service_types and adjustments for validation
        validation_result = validate_billing_amounts(
            result.get("current_billing"),
            result.get("service_types", []),
            result.get("current_adjustments")
        )

    elif detected_company == "Snohomish County PUD":
        # Validate meters against total amount due
        validation_result = validate_current_charges_billing(
            result.get("current_billing"),
            result.get("current_charges", [])
        )

    elif detected_company == "Rubatino Refuse Removal":
        # For Rubatino, validate by summing ALL line item charges plus taxes
        # Compare against previous_balance (PRIOR BALANCE), not current_billing
        validation_result = validate_rubatino_billing(
            result.get("current_billing"),
            result.get("service_types", []),
            result.get("taxes", {}),
            result.get("current_adjustments"),
            result.get("previous_balance")  # Pass previous_balance for comparison
        )

    else:
        # For generic bills, use service_types
        validation_result = validate_billing_amounts(
            result.get("current_billing"), 
            result.get("service_types", []), 
            result.get("current_adjustments")
        )


    # Update the result with validation
    result["billing_validation"] = validation_result

    # Validate service line items for each service
    # Use company-specific validation functions
    if result.get("service_types"):
        if detected_company == "Valley View Sewer District":
            validated_services = validate_valley_view_service_line_items(result.get("service_types", []))
        elif detected_company == "Republic Services":
            validated_services = validate_republic_services_line_items(result.get("service_types", []))
        elif detected_company == "Seattle City Light":

            source_filename = os.path.splitext(os.path.basename(pdf_path))[0]
            validated_services = validate_seattle_city_light_line_items(
                result.get("service_types", []),
                result.get("detailed_billing_rows", []),
                source_filename
            )
        elif detected_company == "Seattle Public Utilities":
            fill_spu_water_service_line_items(result)
            validated_services = validate_service_line_items(result.get("service_types", []))
        else:
            validated_services = validate_service_line_items(result.get("service_types", []))
        result["service_types"] = validated_services

    # Create detailed billing DataFrame for Seattle City Light bills
    if detected_company == "Seattle City Light" and result.get("detailed_billing_rows"):
        source_filename = os.path.splitext(os.path.basename(pdf_path))[0]
        create_detailed_billing_dataframe(result, source_filename)

    return result


def parse_dollar_amount(amount_str):
    """Parse a dollar amount string and return the numeric value."""
    if not amount_str:
        return 0.0
    
    # Remove dollar sign, commas, and whitespace
    cleaned = str(amount_str).replace('$', '').replace(',', '').strip()
    
    try:
        return float(cleaned)
    except (ValueError, TypeError):
        return 0.0

def validate_billing_amounts(current_billing, service_types, current_adjustments=None):
    """Validate that the sum of current service amounts plus adjustments equals the current billing amount."""
    if not current_billing:
        return {
            "is_valid": False,
            "reason": "Missing current_billing data",
            "current_billing_amount": None,
            "service_total": None,
            "current_adjustments": None,
            "total_with_adjustments": None,
            "difference": None
        }
    
    # Parse the current billing amount
    current_billing_amount = parse_dollar_amount(current_billing)
    
    # Parse the current adjustments amount
    adjustments_amount = parse_dollar_amount(current_adjustments) if current_adjustments else 0.0
    
    # Calculate the sum of all current service amounts
    service_total = 0.0
    service_list = []
    
    for service in service_types:
        service_name = service.get('service_name', 'Unknown Service')
        current_service = service.get('current_service')
        
        if current_service:
            current_service_amount = parse_dollar_amount(current_service)
            service_total += current_service_amount
            service_list.append({
                "service_name": service_name,
                "amount": current_service_amount
            })
    
    # Total = service amounts + adjustments
    total_with_adjustments = service_total + adjustments_amount
    
    # Calculate difference between calculated total and current billing
    difference = abs(current_billing_amount - total_with_adjustments)
    
    # Consider amounts equal if difference is less than $0.01 (to handle rounding)
    is_valid = difference < 0.01
    
    return {
        "is_valid": is_valid,
        "current_billing_amount": current_billing_amount,
        "service_total": service_total,
        "current_adjustments": adjustments_amount,
        "total_with_adjustments": total_with_adjustments,
        "difference": round(difference, 2),
        "services": service_list,
        "reason": f"Services (${service_total:.2f}) + Adjustments (${adjustments_amount:.2f}) = ${total_with_adjustments:.2f} {'matches' if is_valid else 'does not match'} Current Billing (${current_billing_amount:.2f})"
    }


def validate_seattle_public_utilities_total_amount_due(
    total_amount_due,
    service_types,
    current_adjustments=None,
    balance=None,
    previous_balance=None,
    payments_applied=None,
):
    """
    Seattle Public Utilities bills reconcile Total Amount Due using a carry-forward balance.

    Preferred validation:
      (Balance) + (Sum of service current charges) + (Adjustments) == Total Amount Due

    Fallback (if balance is missing or clearly inconsistent):
      (Previous Balance - Payments Applied) + (Sum of service current charges) + (Adjustments) == Total Amount Due
    """
    if not total_amount_due:
        return {
            "is_valid": False,
            "reason": "Missing total_amount_due data",
            "total_amount_due": None,
            "service_total": None,
            "current_adjustments": None,
            "previous_balance_net_of_payments": None,
            "total_calculated": None,
            "difference": None,
            "services": []
        }

    total_due_amount = parse_dollar_amount(total_amount_due)
    adjustments_amount = parse_dollar_amount(current_adjustments) if current_adjustments else 0.0

    # Services sum
    service_total = 0.0
    service_list = []
    for service in service_types or []:
        service_name = service.get('service_name', 'Unknown Service')
        current_service = service.get('current_service')
        if current_service:
            amt = parse_dollar_amount(current_service)
            service_total += amt
            service_list.append({"service_name": service_name, "amount": amt})

    # Carry-forward amounts
    balance_amount = parse_dollar_amount(balance) if balance else 0.0

    prev_balance_amount = parse_dollar_amount(previous_balance) if previous_balance else 0.0
    payments_total = 0.0
    for p in payments_applied or []:
        payments_total += parse_dollar_amount(p.get("payment_amount"))
    previous_balance_net = prev_balance_amount - payments_total

    total_using_balance = service_total + adjustments_amount + balance_amount
    total_using_prev_net = service_total + adjustments_amount + previous_balance_net

    diff_using_balance = abs(total_due_amount - total_using_balance)
    diff_using_prev_net = abs(total_due_amount - total_using_prev_net)

    # Prefer the explicit 'balance' field if it validates; otherwise fall back.
    used_balance = balance is not None and str(balance).strip() != "" and diff_using_balance < 0.01
    used_prev_net = (not used_balance) and (diff_using_prev_net < 0.01)

    if used_balance:
        total_calculated = total_using_balance
        difference = diff_using_balance
        reason = (
            f"Services (${service_total:.2f}) + Adjustments (${adjustments_amount:.2f}) + "
            f"Balance (${balance_amount:.2f}) = ${total_calculated:.2f} "
            f"matches Total Amount Due (${total_due_amount:.2f})"
        )
        is_valid = True
    elif used_prev_net:
        total_calculated = total_using_prev_net
        difference = diff_using_prev_net
        reason = (
            f"Services (${service_total:.2f}) + Adjustments (${adjustments_amount:.2f}) + "
            f"Previous Balance Net (${previous_balance_net:.2f}) = ${total_calculated:.2f} "
            f"matches Total Amount Due (${total_due_amount:.2f})"
        )
        is_valid = True
    else:
        # Neither matched; report using balance if present, otherwise previous net.
        if balance is not None and str(balance).strip() != "":
            total_calculated = total_using_balance
            difference = diff_using_balance
            reason = (
                f"Services (${service_total:.2f}) + Adjustments (${adjustments_amount:.2f}) + "
                f"Balance (${balance_amount:.2f}) = ${total_calculated:.2f} "
                f"does not match Total Amount Due (${total_due_amount:.2f})"
            )
        else:
            total_calculated = total_using_prev_net
            difference = diff_using_prev_net
            reason = (
                f"Services (${service_total:.2f}) + Adjustments (${adjustments_amount:.2f}) + "
                f"Previous Balance Net (${previous_balance_net:.2f}) = ${total_calculated:.2f} "
                f"does not match Total Amount Due (${total_due_amount:.2f})"
            )
        is_valid = False

    return {
        "is_valid": is_valid,
        "total_amount_due": total_due_amount,
        "service_total": service_total,
        "current_adjustments": adjustments_amount,
        "balance": balance_amount,
        "previous_balance_net_of_payments": previous_balance_net,
        "total_calculated": total_calculated,
        "difference": round(difference, 2),
        "services": service_list,
        "reason": reason
    }

def validate_meter_based_billing(total_amount_due, meters, previous_balance=None):
    """Validate that the sum of all meter totals equals total amount due.

    For Puget Sound Energy, bills may include a Previous Balance that is carried
    into the Total Amount Due. In that case, the validation should treat:
      sum(meter totals) + previous_balance == total_amount_due
    """
    if not total_amount_due:
        return {
            "is_valid": False,
            "reason": "Missing total_amount_due data",
            "total_amount_due": None,
            "meters_total": None,
            "difference": None,
            "meters": []
        }
    
    # Parse the total amount due
    total_due_amount = parse_dollar_amount(total_amount_due)

    # Parse previous balance if provided (PSE rule)
    previous_balance_amount = parse_dollar_amount(previous_balance) if previous_balance else 0.0
    
    # Calculate the sum of all meter totals
    meters_total = 0.0
    meter_list = []
    
    def _meter_total_str(meter_dict: dict):
        """
        PSE Electric typically uses 'total_current_electric_charges'.
        PSE Gas bills may use a variety of keys (including incorrect ones from older prompts),
        so we accept several.
        """
        if not isinstance(meter_dict, dict):
            return None

        # Fast-path common keys
        for k in (
            "total_current_electric_charges",
            "total_current_gas_charges",
            "total_current_Gas_charges",
            "total_current_charges",
            "current_charges_total",
            "total_current_charges_total",
        ):
            if meter_dict.get(k):
                return meter_dict.get(k)

        # Case-insensitive fallback
        for k, v in meter_dict.items():
            if not v:
                continue
            kl = str(k).lower().strip()
            if kl in (
                "total_current_electric_charges",
                "total_current_gas_charges",
                "total_current_charges",
                "current_charges_total",
                "total_current_charges_total",
            ):
                return v
        return None

    for meter in meters:
        meter_number = meter.get('meter_number', 'Unknown Meter')
        meter_total = _meter_total_str(meter)
        
        if meter_total:
            meter_total_amount = parse_dollar_amount(meter_total)
            meters_total += meter_total_amount
            meter_list.append({
                "meter_number": meter_number,
                "amount": meter_total_amount
            })
    
    # Calculate difference between Total Amount Due and just the meters total.
    # (For PSE bills with Previous Balance, this "gap" should equal the Previous Balance.)
    difference = abs(total_due_amount - meters_total)

    # Validation rule (PSE nuance):
    # Some PSE bills have Total Amount Due that equals the current meter totals (no roll-forward),
    # while others include an unpaid Previous Balance.
    #
    # We therefore accept the bill as valid if EITHER of these matches:
    # - meters_total == total_due_amount
    # - meters_total + previous_balance == total_due_amount
    diff_direct = abs(total_due_amount - meters_total)
    diff_with_prev = abs(total_due_amount - (meters_total + previous_balance_amount))

    used_previous_balance = abs(previous_balance_amount) >= 0.005 and diff_with_prev < 0.01
    is_valid = diff_direct < 0.01 or used_previous_balance

    if used_previous_balance:
        reason = (
            f"Sum of all meters (${meters_total:.2f}) + previous balance (${previous_balance_amount:.2f}) "
            f"matches Total Amount Due (${total_due_amount:.2f})"
        )
    else:
        reason = (
            f"Sum of all meters (${meters_total:.2f}) "
            f"{'matches' if is_valid else 'does not match'} Total Amount Due (${total_due_amount:.2f})"
        )
    
    return {
        "is_valid": is_valid,
        "total_amount_due": total_due_amount,
        "meters_total": meters_total,
        "difference": round(difference, 2),
        "meters": meter_list,
        "reason": reason
    }


def pdf_first_page_contains_text(pdf_path: str, needle: str) -> bool:
    """
    Best-effort text check on page 1. This avoids extra AI calls for simple
    classification heuristics (e.g., PSE Gas vs Electric).
    """
    if not needle:
        return False
    try:
        from pypdf import PdfReader  # type: ignore
    except ImportError:
        try:
            from PyPDF2 import PdfReader  # type: ignore
        except ImportError:
            return False

    try:
        reader = PdfReader(pdf_path)
        if not reader.pages:
            return False
        text = reader.pages[0].extract_text() or ""
        return needle.lower() in text.lower()
    except Exception:
        return False


def detect_pse_service_type_from_pdf(pdf_path: str, client: OpenAI) -> Optional[str]:
    """
    Determine whether a PSE bill is Gas or Electric by looking at the "Your Usage Information"
    section on page 1 (typically the label above the bar chart: "Natural Gas" or "Electricity").

    Returns:
      - "gas" | "electric" | None
    """
    # Cheap fast-path: try text extraction first (works for some PDFs).
    if pdf_first_page_contains_text(pdf_path, "Natural Gas"):
        return "gas"
    # Some bills say "Electricity"; some say "Electric". Treat either as electric if Gas not found.
    if pdf_first_page_contains_text(pdf_path, "Electricity") or pdf_first_page_contains_text(pdf_path, "Electric"):
        return "electric"

    # Vision fallback (image-only PDFs).
    try:
        from pdf2image import convert_from_path
    except ImportError:
        return None

    temp_image_path = "temp_pse_service_type.png"
    try:
        images = convert_from_path(pdf_path, dpi=200, first_page=1, last_page=1)
        if not images:
            return None
        images[0].save(temp_image_path, "PNG", optimize=True)
        with open(temp_image_path, "rb") as img_file:
            image_base64 = base64.b64encode(img_file.read()).decode("utf-8")

        prompt = """You are classifying a Puget Sound Energy (PSE) utility bill.

Look at the LEFT side of the first page where the "Your Usage Information" bar chart is.
The bill will typically show a label ABOVE that bar chart, such as:
- "Natural Gas"  -> this is a GAS bill
- "Electricity" or "Electric" -> this is an ELECTRIC bill

Return ONLY valid JSON in this exact shape:
{
  "service_type": "gas" | "electric" | null,
  "evidence": "the exact words you saw (e.g., Natural Gas)"
}

If you cannot clearly see the label, return service_type null."""

        response = client.chat.completions.create(
            model="gpt-4o",
            messages=[
                {
                    "role": "user",
                    "content": [
                        {"type": "text", "text": prompt},
                        {
                            "type": "image_url",
                            "image_url": {
                                "url": f"data:image/png;base64,{image_base64}",
                                "detail": "high",
                            },
                        },
                    ],
                }
            ],
            response_format={"type": "json_object"},
            max_tokens=200,
            temperature=0,
        )

        if response.choices and response.choices[0].message.content:
            try:
                parsed = json.loads(response.choices[0].message.content.strip())
                st = (parsed.get("service_type") or "").strip().lower()
                if st in ("gas", "electric"):
                    return st
            except Exception:
                return None

        return None
    except Exception:
        return None
    finally:
        try:
            if os.path.exists(temp_image_path):
                os.remove(temp_image_path)
        except Exception:
            pass

def validate_amounts_based_billing(current_billing, amounts):
    """Validate that the sum of all amounts equals the current billing."""
    if not current_billing:
        return {
            "is_valid": False,
            "reason": "Missing current_billing data",
            "current_billing_amount": None,
            "detailed_billing_total": None,
            "difference": None,
            "detailed_items": []
        }
    
    # Parse the current billing amount
    current_billing_amount = parse_dollar_amount(current_billing)
    
    # Calculate the sum of all detailed billing amounts
    amounts_total = 0.0
    amounts_list = []
    
    for amount in amounts:
        if amount:
            amount_value = parse_dollar_amount(amount)
            amounts_total += amount_value
            amounts_list.append(amount_value)
    
    # Calculate difference
    difference = abs(current_billing_amount - amounts_total)
    
    # Consider amounts equal if difference is less than $0.01 (to handle rounding)
    is_valid = difference < 0.01
    
    return {
        "is_valid": is_valid,
        "current_billing_amount": current_billing_amount,
        "amounts_total": amounts_total,
        "difference": round(difference, 2),
        "amounts_list": amounts_list,
        "reason": f"Sum of all amounts (${amounts_total:.2f}) {'matches' if is_valid else 'does not match'} Current Billing (${current_billing_amount:.2f})"
    }

def validate_waste_management_billing(current_billing, service_types, taxes, current_adjustments=None):
    """Validate that the sum of services + taxes + adjustments equals current billing for Waste Management bills."""
    if not current_billing:
        return {
            "is_valid": False,
            "reason": "Missing current_billing data",
            "current_billing_amount": None,
            "service_total": None,
            "taxes_total": None,
            "current_adjustments": None,
            "total_with_taxes_and_adjustments": None,
            "difference": None
        }
    
    # Parse the current billing amount
    current_billing_amount = parse_dollar_amount(current_billing)
    
    # Parse the current adjustments amount
    adjustments_amount = parse_dollar_amount(current_adjustments) if current_adjustments else 0.0
    
    # List of service names that are summary/total lines and should be excluded
    summary_service_names = [
        "total current charges",
        "total",
        "subtotal",
        "grand total",
        "current charges total",
        "service total"
    ]
    
    # Calculate the sum of all service amounts (excluding summary/total services)
    service_total = 0.0
    service_list = []
    
    for service in service_types:
        service_name = service.get('service_name', 'Unknown Service')
        current_service = service.get('current_service')
        
        # Skip summary/total services
        if service_name and service_name.lower().strip() in summary_service_names:
            continue
        
        if current_service:
            current_service_amount = parse_dollar_amount(current_service)
            service_total += current_service_amount
            service_list.append({
                "service_name": service_name,
                "amount": current_service_amount
            })
    
    # Calculate the sum of all taxes
    taxes_total = 0.0
    tax_list = []
    
    if taxes and isinstance(taxes, dict):
        # Add per-service taxes
        per_service_taxes = taxes.get("per_service_taxes", [])
        for tax in per_service_taxes:
            tax_amount = tax.get("tax_amount")
            if tax_amount:
                tax_amount_value = parse_dollar_amount(tax_amount)
                taxes_total += tax_amount_value
                tax_list.append({
                    "tax_name": tax.get("tax_name", "Unknown Tax"),
                    "amount": tax_amount_value
                })
        
        # Add global taxes
        global_taxes = taxes.get("global_taxes", [])
        for tax in global_taxes:
            tax_amount = tax.get("tax_amount")
            if tax_amount:
                tax_amount_value = parse_dollar_amount(tax_amount)
                taxes_total += tax_amount_value
                tax_list.append({
                    "tax_name": tax.get("tax_name", "Unknown Tax"),
                    "amount": tax_amount_value
                })
    
    # Total = service amounts + taxes + adjustments
    total_with_taxes_and_adjustments = service_total + taxes_total + adjustments_amount
    
    # Calculate difference between calculated total and current billing
    difference = abs(current_billing_amount - total_with_taxes_and_adjustments)
    
    # Consider amounts equal if difference is less than $0.01 (to handle rounding)
    is_valid = difference < 0.01
    
    return {
        "is_valid": is_valid,
        "current_billing_amount": current_billing_amount,
        "service_total": service_total,
        "taxes_total": taxes_total,
        "current_adjustments": adjustments_amount,
        "total_with_taxes_and_adjustments": total_with_taxes_and_adjustments,
        "difference": round(difference, 2),
        "services": service_list,
        "taxes": tax_list,
        "reason": f"Services (${service_total:.2f}) + Taxes (${taxes_total:.2f}) + Adjustments (${adjustments_amount:.2f}) = ${total_with_taxes_and_adjustments:.2f} {'matches' if is_valid else 'does not match'} Current Billing (${current_billing_amount:.2f})"
    }



def validate_current_charges_billing(current_billing, current_charges):
    """Validate that the sum of all current charges equals the current billing amount."""
    if not current_billing:
        return {
            "is_valid": False,
            "reason": "Missing current_billing data",
            "current_billing_amount": None,
            "current_charges_total": None,
            "difference": None,
            "current_charges": []
        }

    current_billing_amount = parse_dollar_amount(current_billing)

    charges_total = 0.0
    charges_list = []
    for charge in current_charges or []:
        category = charge.get("category", "Unknown Charge")
        amount_str = charge.get("amount")
        amount_val = parse_dollar_amount(amount_str) if amount_str is not None else 0.0
        charges_total += amount_val
        charges_list.append({
            "category": category,
            "amount": amount_val
        })

    difference = abs(current_billing_amount - charges_total)
    is_valid = difference < 0.01

    return {
        "is_valid": is_valid,
        "current_billing_amount": current_billing_amount,
        "current_charges_total": charges_total,
        "difference": round(difference, 2),
        "current_charges": charges_list,
        "reason": f"Sum of Current Charges (${charges_total:.2f}) {'matches' if is_valid else 'does not match'} Current Billing (${current_billing_amount:.2f})"
    }

def validate_rubatino_billing(current_billing, service_types, taxes, current_adjustments=None, previous_balance=None):
    """
    Validate Rubatino bills by summing ALL line item charges from all services plus all taxes.
    The sum should equal the PRIOR BALANCE amount (previous_balance), not current_billing.
    This is because Rubatino bills show all charges in a table, and the PRIOR BALANCE is the total.
    All items from the description column (except PRIOR BALANCE and payments) should be counted.
    """
    if not previous_balance:
        return {
            "is_valid": False,
            "reason": "Missing previous_balance data",
            "previous_balance_amount": None,
            "line_items_total": None,
            "current_adjustments": None,
            "total_with_adjustments": None,
            "difference": None
        }
    
    # Parse the previous balance amount (this is what we're comparing against)
    previous_balance_amount = parse_dollar_amount(previous_balance)
    
    # Parse the current adjustments amount
    adjustments_amount = parse_dollar_amount(current_adjustments) if current_adjustments else 0.0
    
    # List of service names that are summary/total lines and should be excluded
    summary_service_names = [
        "total current charges",
        "total",
        "subtotal",
        "grand total",
        "current charges total",
        "service total",
        "prior balance",
        "payment lockbox"
    ]
    
    # Sum ALL line item charges from ALL services (not the current_service amounts)
    # This includes all items from the description column except PRIOR BALANCE and payments
    line_items_total = 0.0
    line_items_list = []
    
    for service in service_types:
        service_name = service.get('service_name', 'Unknown Service')
        
        # Skip summary/total services and payment entries
        if service_name and service_name.lower().strip() in summary_service_names:
            continue
        
        # Sum all line item charges for this service
        line_item_charges = service.get('line_item_charges', [])
        for line_item in line_item_charges:
            # Skip if this is a payment or prior balance entry
            category = line_item.get('category', '').lower()
            if 'payment' in category or 'prior balance' in category:
                continue
                
            amount_str = line_item.get('amount') or line_item.get('charge')
            if amount_str:
                amount_value = parse_dollar_amount(amount_str)
                line_items_total += amount_value
                line_items_list.append({
                    "service_name": service_name,
                    "category": line_item.get('category', 'Unknown Category'),
                    "amount": amount_value
                })
    
    # Add all taxes to the line items total (treating them as line item charges)
    # Taxes are also part of the description column and should be included
    if taxes and isinstance(taxes, dict):
        # Add per-service taxes
        per_service_taxes = taxes.get("per_service_taxes", [])
        for tax in per_service_taxes:
            tax_amount = tax.get("tax_amount")
            if tax_amount:
                tax_amount_value = parse_dollar_amount(tax_amount)
                line_items_total += tax_amount_value
                line_items_list.append({
                    "service_name": None,
                    "category": tax.get("tax_name", "Unknown Tax"),
                    "amount": tax_amount_value
                })
        
        # Add global taxes
        global_taxes = taxes.get("global_taxes", [])
        for tax in global_taxes:
            tax_amount = tax.get("tax_amount")
            if tax_amount:
                tax_amount_value = parse_dollar_amount(tax_amount)
                line_items_total += tax_amount_value
                line_items_list.append({
                    "service_name": None,
                    "category": tax.get("tax_name", "Unknown Tax"),
                    "amount": tax_amount_value
                })
    
    # Total = all line items (services + taxes) + adjustments
    total_with_adjustments = line_items_total + adjustments_amount
    
    # Calculate difference between calculated total and previous balance
    difference = abs(previous_balance_amount - total_with_adjustments)
    
    # Consider amounts equal if difference is less than $0.01 (to handle rounding)
    is_valid = difference < 0.01
    
    return {
        "is_valid": is_valid,
        "previous_balance_amount": previous_balance_amount,
        "line_items_total": line_items_total,
        "current_adjustments": adjustments_amount,
        "total_with_adjustments": total_with_adjustments,
        "difference": round(difference, 2),
        "line_items": line_items_list,
        "reason": f"Line Items (${line_items_total:.2f}) + Adjustments (${adjustments_amount:.2f}) = ${total_with_adjustments:.2f} {'matches' if is_valid else 'does not match'} Prior Balance (${previous_balance_amount:.2f})"
    }

def validate_service_line_items(service_types):
    """
    Validate that for each service, the current_service amount equals 
    the sum of all line_item_charges amounts.
    
    Args:
        service_types: List of service dictionaries
        
    Returns:
        List of services with current_service_validation added to each service
    """
    if not service_types:
        return []
    
    validated_services = []
    
    for service in service_types:
        service_name = service.get('service_name', 'Unknown Service')
        current_service_str = service.get('current_service')
        line_item_charges = service.get('line_item_charges', [])
        
        # Parse current_service amount
        current_service_amount = parse_dollar_amount(current_service_str) if current_service_str else 0.0
        
        # Sum all line item charge amounts
        line_items_total = 0.0
        line_items_list = []
        
        for line_item in line_item_charges:
            amount_str = line_item.get('amount') or line_item.get('charge')
            if amount_str:
                amount_value = parse_dollar_amount(amount_str)
                line_items_total += amount_value
                line_items_list.append({
                    "category": line_item.get('category', 'Unknown Category'),
                    "amount": amount_value
                })
        
        # Calculate difference
        difference = abs(current_service_amount - line_items_total)
        
        # Consider amounts equal if difference is less than $0.01 (to handle rounding)
        is_valid = difference < 0.05
        
        # Create validation object
        validation = {
            "is_valid": is_valid,
            "current_service_amount": current_service_amount,
            "line_items_total": line_items_total,
            "difference": round(difference, 2),
            "line_items": line_items_list,
            "reason": f"Line items (${line_items_total:.2f}) {'matches' if is_valid else 'does not match'} Current Service (${current_service_amount:.2f})"
        }
        
        # Create a copy of the service and add validation
        validated_service = service.copy()
        validated_service["current_service_validation"] = validation
        validated_services.append(validated_service)
    
    return validated_services

def validate_valley_view_service_line_items(service_types):
    """
    Validate Valley View service line items.
    For Valley View bills, the structure is:
    - "First Unit Charge" line item (informational, not included in total)
    - "X Units @" line item (the actual charge: (first_unit_rate * units) + first_unit_rate)
    The current_service should equal the "X Units @" line item amount only.
    
    Args:
        service_types: List of service dictionaries
        
    Returns:
        List of services with current_service_validation added to each service
    """
    if not service_types:
        return []
    
    validated_services = []
    
    for service in service_types:
        service_name = service.get('service_name', 'Unknown Service')
        current_service_str = service.get('current_service')
        line_item_charges = service.get('line_item_charges', [])
        
        # Parse current_service amount
        current_service_amount = parse_dollar_amount(current_service_str) if current_service_str else 0.0
        
        # Find the "First Unit Charge" rate and the units line item
        first_unit_charge_rate = None
        first_unit_charge_item = None
        units_line_item = None
        
        for line_item in line_item_charges:
            category = line_item.get('category', '').upper()
            if "FIRST UNIT CHARGE" in category or (category.startswith("FIRST") and "UNIT" in category and "CHARGE" in category):
                first_unit_charge_item = line_item
                rate_str = line_item.get("rate")
                if rate_str:
                    try:
                        first_unit_charge_rate = float(str(rate_str).replace('$', '').replace(',', '').strip())
                    except (ValueError, TypeError):
                        pass
            else:
                # This should be the units line item (e.g., "95 Units", "95 UNITS @")
                units_line_item = line_item
        
        # Sum line items, excluding "First Unit Charge"
        line_items_total = 0.0
        line_items_list = []
        
        for line_item in line_item_charges:
            category = line_item.get('category', '').upper()
            # Skip "First Unit Charge" line items - they are informational only
            if "FIRST UNIT CHARGE" in category or (category.startswith("FIRST") and "UNIT" in category and "CHARGE" in category):
                continue
                
            amount_str = line_item.get('amount') or line_item.get('charge')
            if amount_str:
                amount_value = parse_dollar_amount(amount_str)
                line_items_total += amount_value
                line_items_list.append({
                    "category": line_item.get('category', 'Unknown Category'),
                    "amount": amount_value
                })
        
        # If no units line item was found but we have a First Unit Charge with usage,
        # we might need to calculate it from the First Unit Charge
        if line_items_total == 0.0 and first_unit_charge_item and first_unit_charge_rate:
            usage_str = first_unit_charge_item.get('usage')
            if usage_str:
                try:
                    usage = float(str(usage_str).replace(',', '').strip())
                    # If usage > 1, this might actually be the units line item
                    # Calculate: (first_unit_rate * usage) + first_unit_rate
                    if usage > 1:
                        calculated_amount = (first_unit_charge_rate * usage) + first_unit_charge_rate
                        line_items_total = calculated_amount
                        line_items_list.append({
                            "category": first_unit_charge_item.get('category', 'Unknown Category'),
                            "amount": calculated_amount
                        })
                except (ValueError, TypeError):
                    pass
        
        # Calculate difference
        difference = abs(current_service_amount - line_items_total)
        
        # Consider amounts equal if difference is less than $0.01 (to handle rounding)
        is_valid = difference < 0.05
        
        # Create validation object
        validation = {
            "is_valid": is_valid,
            "current_service_amount": current_service_amount,
            "line_items_total": line_items_total,
            "difference": round(difference, 2),
            "line_items": line_items_list,
            "reason": f"Line items (${line_items_total:.2f}) {'matches' if is_valid else 'does not match'} Current Service (${current_service_amount:.2f})"
        }
        
        # Create a copy of the service and add validation
        validated_service = service.copy()
        validated_service["current_service_validation"] = validation
        validated_services.append(validated_service)
    
    return validated_services

def validate_republic_services_line_items(service_types):
    """
    Validate Republic Services line items.
    For Republic Services bills:
    - Sum ALL line item amounts (including negative values)
    - Include tax line items (taxes are shown in the Amount column and are part of the total)
    - The sum should equal the current_service amount
    
    Args:
        service_types: List of service dictionaries
        
    Returns:
        List of services with current_service_validation added to each service
    """
    if not service_types:
        return []
    
    validated_services = []
    
    for service in service_types:
        service_name = service.get('service_name', 'Unknown Service')
        current_service_str = service.get('current_service')
        line_item_charges = service.get('line_item_charges', [])
        
        # Parse current_service amount
        current_service_amount = parse_dollar_amount(current_service_str) if current_service_str else 0.0
        
        # Sum ALL line item amounts (including negative values and taxes)
        # All items in the Amount column should be included
        line_items_total = 0.0
        line_items_list = []
        
        for line_item in line_item_charges:
            amount_str = line_item.get('amount') or line_item.get('charge')
            if amount_str:
                # parse_dollar_amount should handle negative values correctly
                amount_value = parse_dollar_amount(amount_str)
                line_items_total += amount_value
                line_items_list.append({
                    "category": line_item.get('category', 'Unknown Category'),
                    "amount": amount_value
                })
        
        # Calculate difference
        difference = abs(current_service_amount - line_items_total)
        
        # Consider amounts equal if difference is less than $0.05 (to handle rounding)
        is_valid = difference < 0.05
        
        # Create validation object
        validation = {
            "is_valid": is_valid,
            "current_service_amount": current_service_amount,
            "line_items_total": line_items_total,
            "difference": round(difference, 2),
            "line_items": line_items_list,
            "reason": f"Line items (${line_items_total:.2f}) {'matches' if is_valid else 'does not match'} Current Service (${current_service_amount:.2f})"
        }
        
        # Create a copy of the service and add validation
        validated_service = service.copy()
        validated_service["current_service_validation"] = validation
        validated_services.append(validated_service)
    
    return validated_services

def validate_seattle_city_light_line_items(service_types, detailed_billing_rows, source_filename: str):
    """
    Validate Seattle City Light line items using the saved detailed billing CSV if available.
    Falls back to detailed_billing_rows. Only rows with non-empty amounts are used.
    Categories are taken from service_through_date for rows that have an amount.
    """
    if not service_types:
        return []

    def _none_if_nan(val):
        try:
            import math
            if isinstance(val, float) and math.isnan(val):
                return None
        except Exception:
            pass
        # pandas may leave NaN as numpy.nan
        try:
            import numpy as np  # type: ignore
            if val is np.nan:  # noqa: E721
                return None
        except Exception:
            pass
        return val

    # Prefer CSV rows
    rows_iter = detailed_billing_rows or []
    try:
        script_dir = os.path.dirname(os.path.abspath(__file__))
        csv_path = os.path.join(script_dir, "processed", "detailed_billing", f"{source_filename}_detailed_billing.csv")
        if os.path.exists(csv_path):
            df = pd.read_csv(csv_path)
            if "amount" in df.columns:
                # Keep only rows with real amounts
                df = df[df["amount"].notna() & (df["amount"].astype(str).str.strip().str.lower().isin(["", "null", "none", "nan"]) == False)]
                rows_iter = df.to_dict(orient="records")
    except Exception:
        pass

    # Filter rows to only those with real amounts
    rows_filtered = []
    for row in rows_iter:
        amt = row.get("amount")
        if amt is None:
            continue
        amt_str = str(amt).strip()
        if amt_str == "" or amt_str.lower() in ("null", "none", "nan"):
            continue
        rows_filtered.append(row)

    # Sum amounts and build line_items_list; also replace service line_item_charges with these rows
    line_items_total = 0.0
    line_items_list = []
    csv_line_items = []
    seen_categories = set()
    for row in rows_filtered:
        amount_str = row.get("amount")
        if amount_str is None:
            continue
        amount_val = parse_dollar_amount(amount_str)
        line_items_total += amount_val

        # Category from service_through_date (e.g., Base Service Charge, Small General Energy)
        category = row.get("service_through_date") or row.get("service_category") or "Unknown Category"

        line_items_list.append({
            "category": category,
            "amount": amount_val
        })
        # Keep first occurrence per category to avoid accidental overrides
        if category not in seen_categories:
            seen_categories.add(category)
            csv_line_items.append({
                "category": category,
                "description": None,
            "rate": _none_if_nan(row.get("unit_charge")),
                "amount": f"{amount_val:.2f}",
            "meter_number": _none_if_nan(row.get("meter_number")),
            "usage": _none_if_nan(row.get("consumption_units")),
                "uom": None,
            "previous_reading": _none_if_nan(row.get("previous_reading")),
                "previous_reading_type": None,
            "current_reading": _none_if_nan(row.get("current_reading")),
                "current_reading_type": None,
            "usage_multiplier": _none_if_nan(row.get("multiplier"))
            })

    # Apply the same total to each service for validation
    validated_services = []
    for service in service_types:
        current_service_amount = parse_dollar_amount(service.get("current_service")) if service.get("current_service") else 0.0
        difference = abs(current_service_amount - line_items_total)
        is_valid = difference < 0.05
        validation = {
            "is_valid": is_valid,
            "current_service_amount": current_service_amount,
            "line_items_total": line_items_total,
            "difference": round(difference, 2),
            "line_items": line_items_list,
            "reason": f"Line items (${line_items_total:.2f}) {'matches' if is_valid else 'does not match'} Current Service (${current_service_amount:.2f})"
        }
        svc = service.copy()
        svc["current_service_validation"] = validation
        # Overwrite line_item_charges with CSV-derived items to keep categories/amounts aligned
        svc["line_item_charges"] = csv_line_items
        validated_services.append(svc)

    return validated_services


def fill_spu_water_service_line_items(result: dict) -> None:
    """
    For Seattle Public Utilities water service, propagate the meter header fields
    (previous/current reading, usage, uom, usage_multiplier) into each line_item_charge
    when missing. This helps when the model extracts the header row but leaves
    line items with null readings/usages.
    """
    service_types = result.get("service_types", [])
    if not service_types:
        return

    # Try to get overall consumption from top-level consumption.ccf.usage if present
    top_usage = None
    consumption = result.get("consumption") or {}
    if isinstance(consumption, dict):
        ccf = consumption.get("ccf") or {}
        if isinstance(ccf, dict):
            top_usage = ccf.get("usage")

    for service in service_types:
        name = (service.get("service_name") or "").lower()
        if "water" not in name:
            continue

        prev = service.get("previous_reading")
        curr = service.get("current_reading")
        multiplier = service.get("usage_multiplier") or "1.00"

        for li in service.get("line_item_charges", []):
            if not li.get("previous_reading") and prev:
                li["previous_reading"] = prev
            if not li.get("current_reading") and curr:
                li["current_reading"] = curr

            # Fill usage/uom: prefer existing, otherwise use top-level usage
            if not li.get("usage") and top_usage:
                li["usage"] = str(top_usage)
            if not li.get("uom") and (li.get("usage") or top_usage):
                li["uom"] = "CCF"

            # Fill multiplier if empty
            if not li.get("usage_multiplier") and multiplier:
                li["usage_multiplier"] = multiplier

        # Only one water service expected; break after processing
        break

def create_detailed_billing_dataframe(result: dict, source_filename: str) -> Optional[str]:
    """
    Create a pandas DataFrame from detailed_billing_rows and save it to a CSV file.
    
    Args:
        result: The extracted bill data dictionary
        source_filename: The original PDF filename (without extension)
        
    Returns:
        Path to the saved CSV file, or None if pandas is not available or no data exists
    """
    
    detailed_billing_rows = result.get("detailed_billing_rows")
    if not detailed_billing_rows:
        return None
    
    try:
        # Convert to DataFrame
        df = pd.DataFrame(detailed_billing_rows)
        
        # Reorder columns to match the bill structure
        column_order = [
            "meter_number",
            "service_category",
            "service_from_date",
            "service_through_date",
            "previous_reading",
            "current_reading",
            "multiplier",
            "consumption_units",
            "power_factor",
            "rate_code",
            "unit_charge",
            "amount"
        ]
        
        # Only include columns that exist in the DataFrame
        available_columns = [col for col in column_order if col in df.columns]
        df = df[available_columns]
        
        # Get the directory where the script is located
        script_dir = os.path.dirname(os.path.abspath(__file__))
        detailed_billing_dir = os.path.join(script_dir, "processed", "detailed_billing")
        
        # Create directory if it doesn't exist
        if not os.path.exists(detailed_billing_dir):
            os.makedirs(detailed_billing_dir)
        
        # Create filename
        csv_filename = f"{source_filename}_detailed_billing.csv"
        csv_path = os.path.join(detailed_billing_dir, csv_filename)
        
        # Save to CSV
        df.to_csv(csv_path, index=False)
        
        print(f"Saved detailed billing table to: {csv_path}", file=sys.stderr)
        
        return csv_path
        
    except Exception as e:
        print(f"Error creating detailed billing DataFrame: {e}", file=sys.stderr)
        return None

def find_pdf_files_in_inbox() -> List[str]:
    """Find all PDF files in the inbox folder."""
    # Get the directory where the script is located
    script_dir = os.path.dirname(os.path.abspath(__file__))
    inbox_dir = os.path.join(script_dir, "inbox")
    
    # Check if inbox directory exists
    if not os.path.exists(inbox_dir):
        print(f"Creating inbox directory: {inbox_dir}")
        os.makedirs(inbox_dir)
        return []
    
    # Find all PDF files in the inbox directory
    pdf_pattern = os.path.join(inbox_dir, "*.pdf")
    pdf_files = glob.glob(pdf_pattern)
    
    # Sort files by modification time (newest first)
    pdf_files.sort(key=lambda x: os.path.getmtime(x), reverse=True)
    
    return pdf_files

def create_folder_structure():
    """Create the required folder structure for organizing processed files."""
    script_dir = os.path.dirname(os.path.abspath(__file__))
    
    folders_to_create = [
        os.path.join(script_dir, "processed", "json"),
        os.path.join(script_dir, "processed", "pdf"),
        os.path.join(script_dir, "unprocessed", "json"),
        os.path.join(script_dir, "unprocessed", "pdf")
    ]
    
    for folder in folders_to_create:
        if not os.path.exists(folder):
            os.makedirs(folder)
            print(f"Created folder: {folder}")

def is_extraction_successful(result: dict) -> bool:
    """Determine if extraction was successful based on the extracted data."""
    try:
        # Consider extraction successful if we have meaningful data beyond just account number
        has_customer_info = bool(result.get("customer_name") is not None and result.get("customer_name") != "")
        has_billing_info = bool(result.get("current_billing") is not None and result.get("current_billing") != "")
        has_address_info = bool((result.get("service_address") is not None and result.get("service_address") != "") or 
                               (result.get("billing_address") is not None and result.get("billing_address") != ""))
        
        service_types = result.get("service_types", [])
        has_service_info = bool(service_types and len(service_types) > 0)
        
        taxes = result.get("taxes", {})
        per_service_taxes = taxes.get("per_service_taxes", []) if isinstance(taxes, dict) else []
        global_taxes = taxes.get("global_taxes", []) if isinstance(taxes, dict) else []
        has_tax_info = bool((per_service_taxes and len(per_service_taxes) > 0) or 
                           (global_taxes and len(global_taxes) > 0))
        
        # Extraction is successful if we have at least 2 of these categories
        success_indicators = [has_customer_info, has_billing_info, has_address_info, has_service_info, has_tax_info]
        
        # Debug logging
        print(f"Debug - success_indicators: {success_indicators}", file=sys.stderr)
        
        success_count = sum(success_indicators)
        
        return success_count >= 2
    except Exception as e:
        print(f"Error in is_extraction_successful: {e}", file=sys.stderr)
        print(f"Result data: {result}", file=sys.stderr)
        return False  # Default to unsuccessful if there's an error

def organize_files(pdf_path: str, result: dict, filename: str):
    """Organize the PDF and JSON files into appropriate folders based on extraction success."""
    script_dir = os.path.dirname(os.path.abspath(__file__))
    
    # Debug logging
    print(f"Debug - organize_files called with result keys: {list(result.keys())}", file=sys.stderr)
    
    # Determine if extraction was successful
    extraction_successful = is_extraction_successful(result)
    
    # Set target folders based on success
    if extraction_successful:
        target_pdf_folder = os.path.join(script_dir, "processed", "pdf")
        target_json_folder = os.path.join(script_dir, "processed", "json")
        status = "processed"
    else:
        target_pdf_folder = os.path.join(script_dir, "unprocessed", "pdf")
        target_json_folder = os.path.join(script_dir, "unprocessed", "json")
        status = "unprocessed"
    
    # Move PDF file
    target_pdf_path = os.path.join(target_pdf_folder, filename)
    try:
        if os.path.exists(pdf_path):
            shutil.move(pdf_path, target_pdf_path)
            print(f" Moved PDF to {status}/pdf/{filename}")
        else:
            print(f"PDF file not found at {pdf_path}, skipping move")
    except Exception as e:
        print(f"Error moving PDF: {e}")
    
    # Save JSON file
    json_filename = os.path.splitext(filename)[0] + ".json"
    target_json_path = os.path.join(target_json_folder, json_filename)
    try:
        with open(target_json_path, 'w', encoding='utf-8') as f:
            json.dump(result, f, indent=2, ensure_ascii=False)
        print(f"Saved JSON to {status}/json/{json_filename}")
    except Exception as e:
        print(f"Error saving JSON: {e}")
    
    return extraction_successful

class _TeeStream:
    def __init__(self, *streams):
        self._streams = streams

    def write(self, data):
        for s in self._streams:
            try:
                s.write(data)
            except Exception:
                # Best-effort: ignore write errors to secondary streams
                pass
        self.flush()
        return len(data)

    def flush(self):
        for s in self._streams:
            try:
                s.flush()
            except Exception:
                pass

    def isatty(self):
        # Report TTY if primary stream is a TTY
        try:
            return bool(getattr(self._streams[0], "isatty", lambda: False)())
        except Exception:
            return False

def setup_run_logging() -> str:
    """Create a per-run log file under logs/ and tee stdout/stderr to it.

    Returns the path to the created log file.
    """
    script_dir = os.path.dirname(os.path.abspath(__file__))
    logs_dir = os.path.join(script_dir, "logs")
    if not os.path.exists(logs_dir):
        os.makedirs(logs_dir)

    timestamp = datetime.now().strftime("%Y-%m-%d_%H-%M-%S")
    log_path = os.path.join(logs_dir, f"run_{timestamp}.txt")

    log_file = open(log_path, "w", encoding="utf-8", newline="\n")

    # Keep original streams
    original_stdout = sys.stdout
    original_stderr = sys.stderr

    # Tee to both console and file
    sys.stdout = _TeeStream(original_stdout, log_file)
    sys.stderr = _TeeStream(original_stderr, log_file)

    def _close_log():
        try:
            log_file.flush()
        except Exception:
            pass
        try:
            log_file.close()
        except Exception:
            pass

    atexit.register(_close_log)

    # Write a simple header
    print(f"=== Utility Bills Processing Run @ {timestamp} ===")
    print(f"Python: {sys.version.split()[0]}  PID: {os.getpid()}")
    print(f"Working dir: {os.getcwd()}")
    print("===============================================\n")

    return log_path

def process_batch(pdf_files_batch: list, batch_number: int, total_batches: int) -> tuple:
	"""Process a batch of PDF files and return success/failure counts."""
	results = []
	successful_count = 0
	failed_count = 0
	
	print(f"\n{'='*60}")
	print(f"PROCESSING BATCH {batch_number} of {total_batches} ({len(pdf_files_batch)} files)")
	print(f"{'='*60}")
	
	for i, pdf_file in enumerate[Any](pdf_files_batch, 1):
		filename = os.path.basename(pdf_file)
		print(f"\n[{batch_number}.{i}] Processing: {filename}")
		
		try:
			result = extract_bill_data_via_llm(pdf_file)
			result["source_file"] = filename
			
			# Organize the file and determine success
			extraction_successful = organize_files(pdf_file, result, filename)
			
			if extraction_successful:
				successful_count += 1
				print(f"Successfully processed {filename}")
			else:
				failed_count += 1
				print(f"Incomplete extraction for {filename}")
			
			results.append(result)
			
		except Exception as exc:
			error_result = {
				"source_file": filename,
				"error": str(exc),
				"account_number": None,
                "account_type": None,
				"customer_name": None,
				"service_address": None,
				"billing_address": None,
				"previous_balance": None,
				"current_billing": None,
				"current_adjustments": None,
                "total_amount_due": None,
				"total_amount_due_date": None,
				"bill_date": None,
				"number_of_days": None,
				"payment_information": {"payment_date": None, "payment_amount": None},
                "payments_applied": [],
                "adjustments": [],
				"taxes": {"per_service_taxes": [], "global_taxes": []},
				"service_types": [],
				"billing_validation": None
			}
			
			# Organize failed file - check if file still exists
			try:
				if os.path.exists(pdf_file):
					organize_files(pdf_file, error_result, filename)
				else:
					print(f"Warning: PDF file {filename} was not found for organization", file=sys.stderr)
			except Exception as org_exc:
				print(f"Warning: Could not organize failed file {filename}: {org_exc}", file=sys.stderr)
			
			failed_count += 1
			results.append(error_result)
			print(f"Error processing {filename}: {exc}")
	
	# Batch summary
	print(f"\n{'='*60}")
	print(f"BATCH {batch_number} SUMMARY")
	print(f"{'='*60}")
	print(f"Files in batch: {len(pdf_files_batch)}")
	print(f"Successfully processed: {successful_count}")
	print(f"Failed/Incomplete: {failed_count}")
	
	return results, successful_count, failed_count

def main() -> int:
	parser = argparse.ArgumentParser(description="Extract information from utility bill PDFs in the inbox folder.")
	parser.add_argument("--pdf-path", type=str, help="Optional: Path to a specific PDF file to process")
	parser.add_argument("--batch-size", type=int, default=20, help="Number of files to process in each batch (default: 20)")
	parser.add_argument("--batch-delay", type=int, default=5, help="Seconds to wait between batches (default: 5)")
	args = parser.parse_args()

	# Initialize per-run logging to logs/run_YYYY-mm-dd_HH-MM-SS.txt
	setup_run_logging()

	# Create folder structure
	create_folder_structure()

	# If a specific PDF path is provided, process that file
	if args.pdf_path:
		try:
			result = extract_bill_data_via_llm(args.pdf_path)
			filename = os.path.basename(args.pdf_path)
			result["source_file"] = filename
			
			# Organize the file
			extraction_successful = organize_files(args.pdf_path, result, filename)
			
			print(f"\nExtraction {'successful' if extraction_successful else 'incomplete'}")
			print(json.dumps(result, indent=2, ensure_ascii=False))
			return 0
		except Exception as exc:
			_readable_err(f"Error processing {args.pdf_path}: {exc}")
			return 1

	# Otherwise, process files from the inbox folder
	pdf_files = find_pdf_files_in_inbox()
	
	if not pdf_files:
		print("No PDF files found in the inbox folder.")
		print("Please place PDF files in the 'inbox' directory and run the program again.")
		return 0

	print(f"Found {len(pdf_files)} PDF file(s) in inbox folder:")
	for i, pdf_file in enumerate(pdf_files, 1):
		filename = os.path.basename(pdf_file)
		print(f"  {i}. {filename}")

	# Process files in batches
	batch_size = args.batch_size
	batch_delay = args.batch_delay
	total_batches = (len(pdf_files) + batch_size - 1) // batch_size  # Ceiling division
	
	print(f"\n{'='*60}")
	print(f"STARTING BATCH PROCESSING")
	print(f"{'='*60}")
	print(f"Total files: {len(pdf_files)}")
	print(f"Batch size: {batch_size}")
	print(f"Total batches: {total_batches}")
	print(f"{'='*60}")

	all_results = []
	total_successful = 0
	total_failed = 0
	
	for batch_num in range(1, total_batches + 1):
		start_idx = (batch_num - 1) * batch_size
		end_idx = min(start_idx + batch_size, len(pdf_files))
		batch_files = pdf_files[start_idx:end_idx]
		
		try:
			batch_results, batch_successful, batch_failed = process_batch(batch_files, batch_num, total_batches)
			all_results.extend(batch_results)
			total_successful += batch_successful
			total_failed += batch_failed
			
			# Pause between batches (except for the last one)
			if batch_num < total_batches:
				print(f"\nBatch {batch_num} completed. Starting batch {batch_num + 1} in {batch_delay} seconds...")
				try:
					import time
					for i in range(batch_delay, 0, -1):
						print(f"Starting in {i}...", end="\r")
						time.sleep(1)
					print("Starting next batch...        ")  # Clear the countdown line
				except KeyboardInterrupt:
					print(f"\n\nProcessing stopped by user after batch {batch_num}")
					break
					
		except KeyboardInterrupt:
			print(f"\n\nProcessing stopped by user during batch {batch_num}")
			break
		except Exception as e:
			print(f"\nError processing batch {batch_num}: {e}")
			total_failed += len(batch_files)
			continue

	# Final summary
	print(f"\n{'='*60}")
	print("FINAL PROCESSING SUMMARY")
	print(f"{'='*60}")
	print(f"Total files processed: {len(all_results)}")
	print(f"Successfully extracted: {total_successful}")
	print(f"Incomplete/Failed: {total_failed}")
	print(f"\nFiles organized into:")
	print(f"  - processed/pdf: {total_successful} files")
	print(f"  - processed/json: {total_successful} files")
	print(f"  - unprocessed/pdf: {total_failed} files")
	print(f"  - unprocessed/json: {total_failed} files")
	
	return 0

if __name__ == "__main__":
	sys.exit(main())