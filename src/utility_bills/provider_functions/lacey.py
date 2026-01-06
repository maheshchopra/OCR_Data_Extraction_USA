from typing import Any, Dict, List


def compute_charges_validation(
    utility_bill: Dict[str, Any],
    tolerance: float = 0.01,
) -> Dict[str, Any]:
    """
    For City of Lacey bills:
    - Sum all charges_level_data[].charge_amount values
    - Compare that sum to statement_level_data.current_billing
    - Attach a charges_level_data_validation object at the top level.

    Args:
        utility_bill: Parsed JSON/dict in the LaceyBillExtract shape.
        tolerance: Allowed absolute difference before is_match becomes False.

    Returns:
        The same dict, mutated in-place and also returned, with
        "charges_level_data_validation" populated at the top level.
    """

    statement_data = utility_bill.get("statement_level_data", {})
    charges_level_data: List[Dict[str, Any]] = utility_bill.get(
        "charges_level_data", []
    )

    # Sum all charge_amount values (treat None as 0)
    sum_charges = sum(
        (charge.get("charge_amount") or 0.0) for charge in charges_level_data
    )

    # Get current_billing from statement
    current_billing = statement_data.get("current_billing")

    # Compute validation
    if current_billing is None:
        difference = None
        is_match = None
    else:
        # Round to cents to avoid tiny float errors
        sum_charges_rounded = round(sum_charges, 2)
        current_billing_rounded = round(current_billing, 2)
        difference = round(sum_charges_rounded - current_billing_rounded, 2)
        is_match = abs(difference) <= tolerance

    # Store the validation result at the top level
    utility_bill["line_item_charges_validation"] = {
        "sum_charges": round(sum_charges, 2),
        "current_billing": current_billing,
        "difference": difference,
        "is_match": is_match,
    }

    return utility_bill


def compute_total_amount_validation(
    utility_bill: Dict[str, Any],
    tolerance: float = 0.01,
) -> Dict[str, Any]:
    """
    For City of Lacey bills:
    - Calculate: previous_balance + payments_applied + current_adjustments + current_billing
    - Compare that sum to total_amount_due
    - Attach a total_amount_validation object to statement_level_data.

    Args:
        utility_bill: Parsed JSON/dict in the LaceyBillExtract shape.
        tolerance: Allowed absolute difference before is_match becomes False.

    Returns:
        The same dict, mutated in-place and also returned, with
        statement_level_data["total_amount_validation"] populated.
    """

    statement_data = utility_bill.get("statement_level_data", {})

    # Get values (treat None as 0)
    previous_balance = statement_data.get("previous_balance") or 0.0
    payments_applied = statement_data.get("payments_applied") or 0.0
    current_adjustments = statement_data.get("current_adjustments") or 0.0
    current_billing = statement_data.get("current_billing") or 0.0

    # Calculate expected total
    # Note: payments_applied should already be negative if it was extracted correctly
    calculated_total = (
        previous_balance + payments_applied + current_adjustments + current_billing
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

    # Store the validation result
    statement_data["total_amount_validation"] = {
        "previous_balance": round(previous_balance, 2),
        "payments_applied": round(payments_applied, 2),
        "current_adjustments": round(current_adjustments, 2),
        "current_billing": round(current_billing, 2),
        "calculated_total": round(calculated_total, 2),
        "total_amount_due": total_amount_due,
        "difference": difference,
        "is_match": is_match,
    }

    return utility_bill


def postprocess_lacey(
    utility_bill: Dict[str, Any],
    tolerance: float = 0.01,
) -> Dict[str, Any]:
    """
    Combined post-processing for City of Lacey:
    - Validates that sum of charges equals current billing
    - Validates total amount due calculation (includes adjustments)
    """
    utility_bill = compute_charges_validation(utility_bill, tolerance)
    utility_bill = compute_total_amount_validation(utility_bill, tolerance)
    return utility_bill


def check_validation_passed(utility_bill: Dict[str, Any]) -> bool:
    """
    Check if all validation checks passed (all is_match values are True or None).

    This function checks:
    - charges_level_data_validation["is_match"] at top level
    - total_amount_validation["is_match"] in statement_level_data

    Args:
        utility_bill: The extracted utility bill dictionary after post-processing.

    Returns:
        True if all validations passed (all is_match are True or None), False otherwise.
    """
    # Check charges_level_data_validation at top level
    charges_validation = utility_bill.get("line_item_charges_validation", {})
    is_match = charges_validation.get("is_match")
    if is_match is False:
        return False

    # Check total_amount_validation in statement_level_data
    statement_data = utility_bill.get("statement_level_data", {})
    total_validation = statement_data.get("total_amount_validation", {})
    is_match = total_validation.get("is_match")
    if is_match is False:
        return False

    # All validations passed (True or None)
    return True
