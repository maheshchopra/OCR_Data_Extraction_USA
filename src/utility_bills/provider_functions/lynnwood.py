from typing import Any, Dict, List


def compute_line_item_charges_validation(
    utility_bill: Dict[str, Any],
    tolerance: float = 0.01,
) -> Dict[str, Any]:
    """
    For Lynnwood bills:
    - Sum all meter_level_data[].charge values
    - Compare that sum to current_billing from statement_level_data
    - Attach a line_item_charges_validation object to statement_level_data.

    Args:
        utility_bill: Parsed JSON/dict in the LynnwoodBillExtract shape.
        tolerance: Allowed absolute difference before is_match becomes False.

    Returns:
        The same dict, mutated in-place and also returned, with
        statement_level_data["line_item_charges_validation"] populated.
    """
    meter_level_data: List[Dict[str, Any]] = utility_bill.get("meter_level_data", [])
    statement_data = utility_bill.get("statement_level_data", {})

    # Sum all charge values from meter_level_data (treat None as 0)
    sum_meter_charges = sum((meter.get("charge") or 0.0) for meter in meter_level_data)

    current_billing = statement_data.get("current_billing")

    # Default values if current_billing is missing
    if current_billing is None:
        difference = None
        is_match = None
    else:
        # Round to cents to avoid tiny float errors
        sum_meter_charges_rounded = round(sum_meter_charges, 2)
        current_billing_rounded = round(current_billing, 2)
        difference = round(sum_meter_charges_rounded - current_billing_rounded, 2)
        is_match = abs(difference) <= tolerance

    # Store the validation result in statement_level_data
    statement_data["line_item_charges_validation"] = {
        "sum_meter_charges": round(sum_meter_charges, 2),
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
    For Lynnwood bills:
    - Calculate: previous_balance - payments_applied + current_billing + late_fee_applied + adjustments
    - Compare calculated total to total_amount_due
    - Attach a total_amount_validation object to statement_level_data.

    Note: payments_applied is typically negative (representing a credit),
          so we subtract it (which effectively adds the credit).

    Args:
        utility_bill: Parsed JSON/dict in the LynnwoodBillExtract shape.
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
    late_fee_applied = statement_data.get("late_fee_applied") or 0.0
    adjustments = miscellaneous_data.get("adjustments") or 0.0

    # Calculate expected total
    # Formula: previous_balance - payments_applied + current_billing + late_fee_applied + adjustments
    # Note: payments_applied is typically negative, so subtracting it adds the credit
    calculated_total = (
        previous_balance + payments_applied + current_billing + adjustments
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
        "late_fee_applied": round(late_fee_applied, 2),
        "adjustments": round(adjustments, 2),
        "calculated_total": round(calculated_total, 2),
        "total_amount_due": total_amount_due,
        "difference": difference,
        "is_match": is_match,
    }

    return utility_bill


def postprocess_lynnwood(
    utility_bill: Dict[str, Any],
    tolerance: float = 0.01,
) -> Dict[str, Any]:
    """
    Combined post-processing for Lynnwood utility bills:
    - Validates that sum of meter charges matches current_billing
    - Validates total amount due calculation

    Args:
        utility_bill: Parsed JSON/dict in the LynnwoodBillExtract shape.
        tolerance: Allowed absolute difference before is_match becomes False.

    Returns:
        The same dict with validation objects added.
    """
    utility_bill = compute_line_item_charges_validation(utility_bill, tolerance)
    utility_bill = compute_total_amount_validation(utility_bill, tolerance)
    return utility_bill


def check_validation_passed(utility_bill: Dict[str, Any]) -> bool:
    """
    Check if all validation checks passed for Lynnwood bills.

    This function checks:
    - line_item_charges_validation["is_match"] in statement_level_data
    - total_amount_validation["is_match"] in statement_level_data

    Args:
        utility_bill: The extracted utility bill dictionary after post-processing.

    Returns:
        True if all validations passed (all is_match are True or None), False otherwise.
    """
    statement_data = utility_bill.get("statement_level_data", {})

    # Check line_item_charges_validation
    line_item_validation = statement_data.get("line_item_charges_validation", {})
    is_match = line_item_validation.get("is_match")
    if is_match is False:
        return False

    # Check total_amount_validation
    total_validation = statement_data.get("total_amount_validation", {})
    is_match = total_validation.get("is_match")
    if is_match is False:
        return False

    # All validations passed (True or None)
    return True
