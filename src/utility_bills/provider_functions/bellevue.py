from typing import Any, Dict, List


def compute_service_line_item_charges_validation(
    service: Dict[str, Any],
    tolerance: float = 0.01,
) -> Dict[str, Any]:
    """
    For a single service in Bellevue bills:
    - Sum all line_item_charges[].line_item_charge_amount
    - Compare that sum to service_total
    - Attach a line_item_charges_validation object with details.

    Args:
        service: A single service dict from charges_level_data.services
        tolerance: Allowed absolute difference before is_match becomes False.

    Returns:
        The same service dict, mutated in-place and also returned, with
        "line_item_charges_validation" populated.
    """
    line_items: List[Dict[str, Any]] = service.get("line_item_charges", [])

    # Sum up all line_item_charge_amount values
    sum_line_items = sum(
        (item.get("line_item_charge_amount") or 0.0) for item in line_items
    )

    service_total = service.get("service_total")

    # Default values if service_total is missing
    if service_total is None:
        difference = None
        is_match = None
    else:
        # Round to cents to avoid tiny float errors
        sum_line_items_rounded = round(sum_line_items, 2)
        difference = round(sum_line_items_rounded - service_total, 2)
        is_match = abs(difference) <= tolerance

    # Store the validation result
    service["line_item_charges_validation"] = {
        "sum_line_item_charges": round(sum_line_items, 2),
        "service_total": service_total,
        "difference": difference,
        "is_match": is_match,
    }

    return service


def compute_total_amount_validation(
    utility_bill: Dict[str, Any],
    tolerance: float = 0.01,
) -> Dict[str, Any]:
    """
    For Bellevue bills:
    - Get total_previous_charges from statement_level_data
    - Get current_billing from statement_level_data
    - Calculate: total_previous_charges + current_billing
    - Compare calculated total to total_amount_due
    - Attach a total_amount_validation object to statement_level_data.

    Note: total_previous_charges is the NET of previous balance and payments.
          It can be negative if there's a credit on the account.

    Args:
        utility_bill: Parsed JSON/dict in the BellevueBillExtract shape.
        tolerance: Allowed absolute difference before is_match becomes False.

    Returns:
        The same dict, mutated in-place and also returned, with
        statement_level_data["total_amount_validation"] populated.
    """
    statement_data = utility_bill.get("statement_level_data", {})
    miscellaneous_data = utility_bill.get("miscellaneous_level_data", {})

    # Get all components, treating None as 0.0
    previous_balance = statement_data.get("previous_balance") or 0.0
    payments_applied = statement_data.get("payments_applied") or 0.0
    current_billing = statement_data.get("current_billing") or 0.0
    other_charges = miscellaneous_data.get("other_charges_and_adjustments") or 0.0

    # Calculate expected total: total_previous_charges + current_billing
    # Note: total_previous_charges can be negative (credit)
    calculated_total = (
        previous_balance + payments_applied + current_billing + other_charges
    )

    # Get total_amount_due from statement
    total_amount_due = statement_data.get("total_amount_due")

    # Compute validation
    if total_amount_due is None:
        difference = None
        is_match = None
    else:
        # Round to cents to avoid tiny float errors
        calculated_total_rounded = round(calculated_total, 2)
        total_amount_due_rounded = round(total_amount_due, 2)
        difference = round(calculated_total_rounded - total_amount_due_rounded, 2)
        is_match = abs(difference) <= tolerance

    # Store the validation result at statement level
    statement_data["total_amount_validation"] = {
        "previous_balance": round(previous_balance, 2),
        "payments_applied": round(payments_applied, 2),
        "current_billing": round(current_billing, 2),
        "other_charges_and_adjustments": round(other_charges, 2),
        "calculated_total": round(calculated_total, 2),
        "total_amount_due": total_amount_due,
        "difference": difference,
        "is_match": is_match,
    }

    return utility_bill


def postprocess_bellevue(
    utility_bill: Dict[str, Any],
    tolerance: float = 0.01,
) -> Dict[str, Any]:
    """
    Combined post-processing for Bellevue utility bills:
    - Validates each service's line item charges sum to its service_total
    - Validates all service totals sum to current_service_charges
    - Validates total amount due calculation

    Args:
        utility_bill: Parsed JSON/dict in the BellevueBillExtract shape.
        tolerance: Allowed absolute difference before is_match becomes False.

    Returns:
        The same dict with validation objects added.
    """
    # Validate each service's line items
    charges_data = utility_bill.get("charges_level_data", {})
    services = charges_data.get("services", [])

    for service in services:
        compute_service_line_item_charges_validation(service, tolerance)

    # Validate total amount due
    utility_bill = compute_total_amount_validation(utility_bill, tolerance)

    return utility_bill


def check_validation_passed(utility_bill: Dict[str, Any]) -> bool:
    """
    Check if all validation checks passed for Bellevue bills.

    This function checks:
    - line_item_charges_validation["is_match"] for each service in charges_level_data.services
    - services_total_validation["is_match"] in charges_level_data
    - total_amount_validation["is_match"] in statement_level_data

    Args:
        utility_bill: The extracted utility bill dictionary after post-processing.

    Returns:
        True if all validations passed (all is_match are True or None), False otherwise.
    """
    # Check each service's line item validation
    charges_data = utility_bill.get("charges_level_data", {})
    services = charges_data.get("services", [])

    for service in services:
        line_item_charges_validation = service.get("line_item_charges_validation", {})
        is_match = line_item_charges_validation.get("is_match")
        # If is_match is False, validation failed
        if is_match is False:
            return False

    # Check total_amount_validation at statement level
    statement_data = utility_bill.get("statement_level_data", {})
    total_validation = statement_data.get("total_amount_validation", {})
    is_match = total_validation.get("is_match")
    # If is_match is False, validation failed
    if is_match is False:
        return False

    # All validations passed (True or None)
    return True
