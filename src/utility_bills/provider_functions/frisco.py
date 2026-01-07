from typing import Any, Dict, List


def compute_line_item_charges_validation(
    utility_bill: Dict[str, Any],
    tolerance: float = 0.01,
) -> Dict[str, Any]:
    """
    For City of Frisco bills:
    - Sum all service_charges[].charge_amount from charges_level_data
    - Compare that sum to current_charges_total
    - Attach a line_item_charges_validation object with details.

    Args:
        utility_bill: Parsed JSON/dict in the FriscoBillExtract shape.
        tolerance: Allowed absolute difference before is_match becomes False.

    Returns:
        The same dict, mutated in-place and also returned, with
        charges_level_data["line_item_charges_validation"] populated.
    """

    charges_data: Dict[str, Any] = utility_bill.get("charges_level_data", {})
    service_charges: List[Dict[str, Any]] = charges_data.get("service_charges", [])

    # Sum up all charge_amount values from service_charges (treat None as 0)
    sum_service_charges = sum(
        (item.get("charge_amount") or 0.0) for item in service_charges
    )

    current_charges_total = charges_data.get("current_charges_total")

    # Default values if current_charges_total is missing
    if current_charges_total is None:
        difference = None
        is_match = None
    else:
        # Round to cents to avoid tiny float errors
        sum_service_charges_rounded = round(sum_service_charges, 2)
        difference = round(sum_service_charges_rounded - current_charges_total, 2)
        is_match = abs(difference) <= tolerance

    # Store the validation result
    charges_data["line_item_charges_validation"] = {
        "sum_service_charges": round(sum_service_charges, 2),
        "current_charges_total": current_charges_total,
        "difference": difference,
        "is_match": is_match,
    }

    return utility_bill


def compute_total_amount_validation(
    utility_bill: Dict[str, Any],
    tolerance: float = 0.01,
) -> Dict[str, Any]:
    """
    For City of Frisco bills:
    - Calculate: current_billing (which should equal total_amount_due if no balance)
    - If there's a balance or previous amounts, factor those in
    - Compare calculated total to total_amount_due
    - Attach a total_amount_validation object to statement_level_data.

    Args:
        utility_bill: Parsed JSON/dict in the FriscoBillExtract shape.
        tolerance: Allowed absolute difference before is_match becomes False.

    Returns:
        The same dict, mutated in-place and also returned, with
        statement_level_data["total_amount_validation"] populated.
    """

    statement_data = utility_bill.get("statement_level_data", {})

    # Get previous_balance (treat None as 0)
    previous_balance = statement_data.get("previous_balance") or 0.0

    # Get payments_applied (treat None as 0)
    payments_applied = statement_data.get("payments_applied") or 0.0

    # Get balance (treat None as 0)
    balance = statement_data.get("balance") or 0.0

    # Get current_billing (treat None as 0)
    current_billing = statement_data.get("current_billing") or 0.0

    # Calculate expected total
    # For Frisco: if balance is shown, use balance + current_billing
    # Otherwise, just current_billing (assuming payments cleared previous balance)
    if balance != 0.0:
        calculated_total = balance + current_billing
    else:
        calculated_total = current_billing

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

    # Store the validation result
    statement_data["total_amount_validation"] = {
        "previous_balance": round(previous_balance, 2),
        "payments_applied": round(payments_applied, 2),
        "balance": round(balance, 2),
        "current_billing": round(current_billing, 2),
        "calculated_total": round(calculated_total, 2),
        "total_amount_due": total_amount_due,
        "difference": difference,
        "is_match": is_match,
    }

    return utility_bill


def postprocess_frisco(
    utility_bill: Dict[str, Any],
    tolerance: float = 0.01,
) -> Dict[str, Any]:
    """
    Combined post-processing for City of Frisco:
    - Validates line item charges (sum of service charges vs current_charges_total)
    - Validates total amount due calculation
    """
    utility_bill = compute_line_item_charges_validation(utility_bill, tolerance)
    utility_bill = compute_total_amount_validation(utility_bill, tolerance)
    return utility_bill


def check_validation_passed(utility_bill: Dict[str, Any]) -> bool:
    """
    Check if all validation checks passed (all is_match values are True or None).

    This function checks:
    - line_item_charges_validation["is_match"] in charges_level_data
    - total_amount_validation["is_match"] in statement_level_data

    Args:
        utility_bill: The extracted utility bill dictionary after post-processing.

    Returns:
        True if all validations passed (all is_match are True or None), False otherwise.
    """
    # Check line_item_charges_validation in charges_level_data
    charges_data = utility_bill.get("charges_level_data", {})
    validation = charges_data.get("line_item_charges_validation", {})
    is_match = validation.get("is_match")
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
