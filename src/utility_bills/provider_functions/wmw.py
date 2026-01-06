from typing import Any, Dict, List


def compute_line_item_validation(
    utility_bill: Dict[str, Any],
    tolerance: float = 0.01,
) -> Dict[str, Any]:
    """
    For each charges_level_data service:
    - Sum all line_items[].amount
    - Compare that sum to total_current_charges
    - Attach a line_item_validation object with details.

    Args:
        utility_bill: Parsed JSON/dict in the WMBillExtract shape.
        tolerance: Allowed absolute difference before is_match becomes False.

    Returns:
        The same dict, mutated in-place and also returned, with
        charges_level_data[i]["line_item_charges_validation"] populated.
    """

    charges_level_data: List[Dict[str, Any]] = utility_bill.get(
        "charges_level_data", []
    )

    for charges in charges_level_data:
        line_items: List[Dict[str, Any]] = charges.get("line_items", [])

        # Sum up all amount values (treat None as 0)
        sum_line_items = sum((item.get("amount") or 0.0) for item in line_items)

        total_current_charges = charges.get("total_current_charges")

        # Default values if total_current_charges is missing
        if total_current_charges is None:
            difference = None
            is_match = None
        else:
            # Round to cents to avoid tiny float errors
            sum_line_items_rounded = round(sum_line_items, 2)
            difference = round(sum_line_items_rounded - total_current_charges, 2)
            is_match = abs(difference) <= tolerance

        # Store the validation result
        charges["line_item_charges_validation"] = {
            "sum_line_items": round(sum_line_items, 2),
            "total_current_charges": total_current_charges,
            "difference": difference,
            "is_match": is_match,
        }

    return utility_bill


def compute_total_amount_validation(
    utility_bill: Dict[str, Any],
    tolerance: float = 0.01,
) -> Dict[str, Any]:
    """
    For Waste Management of Washington bills:
    - Calculate: previous_balance + payments_applied + current_billing
    - Compare to total_amount_due
    - Attach a total_amount_validation object to statement_level_data.

    Note: payments_applied is typically negative on WM bills (shown in parentheses),
    so the formula is: previous_balance + payments_applied + current_billing = total_amount_due
    Example: 1,224.81 + (-1,224.81) + 1,224.81 = 1,224.81

    Formula: previous_balance + payments_applied + adjustments + current_billing = total_amount_due
    Example: 1,224.81 + (-1,224.81) + 0.00 + 1,224.81 = 1,224.81

    Args:
        utility_bill: Parsed JSON/dict in the WMBillExtract shape.
        tolerance: Allowed absolute difference before is_match becomes False.

    Returns:
        The same dict, mutated in-place and also returned, with
        statement_level_data["total_amount_validation"] populated.
    """

    statement_data = utility_bill.get("statement_level_data", {})
    misc_data = utility_bill.get("miscellaneous_level_data", {})

    # Get previous_balance, payments_applied, adjustments, and current_billing (treat None as 0)
    previous_balance = statement_data.get("previous_balance") or 0.0
    payments_applied = statement_data.get("payments_applied") or 0.0
    adjustments = misc_data.get("adjustments") or 0.0
    current_billing = statement_data.get("current_billing") or 0.0

    # Calculate expected total
    # adjustments can be positive or negative
    calculated_total = (
        previous_balance + payments_applied + adjustments + current_billing
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
        "adjustments": round(adjustments, 2),
        "current_billing": round(current_billing, 2),
        "calculated_total": round(calculated_total, 2),
        "total_amount_due": total_amount_due,
        "difference": difference,
        "is_match": is_match,
    }

    return utility_bill


def postprocess_waste_management_washington(
    utility_bill: Dict[str, Any],
    tolerance: float = 0.01,
) -> Dict[str, Any]:
    """
    Combined post-processing for Waste Management of Washington:
    - Validates line item amounts per service location
    - Validates total amount due calculation

    Args:
        utility_bill: Parsed JSON/dict in the WMBillExtract shape.
        tolerance: Allowed absolute difference before is_match becomes False.

    Returns:
        The same dict with validation fields populated.
    """
    utility_bill = compute_line_item_validation(utility_bill, tolerance)
    utility_bill = compute_total_amount_validation(utility_bill, tolerance)
    return utility_bill


def check_validation_passed(utility_bill: Dict[str, Any]) -> bool:
    """
    Check if all validation checks passed (all is_match values are True or None).

    This function checks:
    - All line_item_charges_validation["is_match"] in charges_level_data
    - total_amount_validation["is_match"] in statement_level_data

    Args:
        utility_bill: The extracted utility bill dictionary after post-processing.

    Returns:
        True if all validations passed (all is_match are True or None), False otherwise.
    """
    # Check line_item_validation for each service location
    charges_level_data = utility_bill.get("charges_level_data", [])
    for charges in charges_level_data:
        validation = charges.get("line_item_charges_validation", {})
        is_match = validation.get("is_match")
        # If any is_match is False, validation failed
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
