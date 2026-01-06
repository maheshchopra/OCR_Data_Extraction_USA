from typing import Any, Dict, List


def compute_line_item_charges_validation(
    utility_bill: Dict[str, Any],
    tolerance: float = 0.01,
) -> Dict[str, Any]:
    """
    For PSE gas bills:
    - Sum all line_item_charges[].line_item_charge_amount in charges_level_data
    - Compare that sum to current_natural_gas_charges
    - Attach a line_item_charges_validation object with details.

    Args:
        utility_bill: Parsed JSON/dict in the PSEGasBillExtract shape.
        tolerance: Allowed absolute difference before is_match becomes False.

    Returns:
        The same dict, mutated in-place and also returned, with
        charges_level_data["line_item_charges_validation"] populated.
    """

    charges_data: Dict[str, Any] = utility_bill.get("charges_level_data", {})
    line_items: List[Dict[str, Any]] = charges_data.get("line_item_charges", [])

    # Sum up all line_item_charge_amount values (treat None as 0)
    sum_line_items = sum(
        (item.get("line_item_charge_amount") or 0.0) for item in line_items
    )

    current_charges = charges_data.get("current_natural_gas_charges")

    # Default values if current_charges is missing
    if current_charges is None:
        difference = None
        is_match = None
    else:
        # Round to cents to avoid tiny float errors
        sum_line_items_rounded = round(sum_line_items, 2)
        difference = round(sum_line_items_rounded - current_charges, 2)
        is_match = abs(difference) <= tolerance

    # Store the validation result
    charges_data["line_item_charges_validation"] = {
        "sum_line_item_charges": round(sum_line_items, 2),
        "current_natural_gas_charges": current_charges,
        "difference": difference,
        "is_match": is_match,
    }

    return utility_bill


def compute_total_amount_validation(
    utility_bill: Dict[str, Any],
    tolerance: float = 0.01,
) -> Dict[str, Any]:
    """
    For PSE gas bills:
    - Get total_previous_charges (Total Previous Charges) from statement_level_data
    - Get current_billing (Total Current Charges) from statement_level_data
    - Calculate: total_previous_charges + current_billing
    - Compare calculated total to total_amount_due
    - Attach a total_amount_validation object to statement_level_data.

    Note: total_previous_charges is the NET of previous balance and payments.
          It can be negative if there's a credit on the account.

    Args:
        utility_bill: Parsed JSON/dict in the PSEGasBillExtract shape.
        tolerance: Allowed absolute difference before is_match becomes False.

    Returns:
        The same dict, mutated in-place and also returned, with
        statement_level_data["total_amount_validation"] populated.
    """

    statement_data = utility_bill.get("statement_level_data", {})

    total_previous_charges = statement_data.get("total_previous_charges")
    current_billing = statement_data.get("current_billing") or 0.0

    # Calculate expected total: total_previous_charges + current_billing
    # Note: total_previous_charges can be negative (credit)
    calculated_total = total_previous_charges + current_billing

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
        "previous_balance": round(total_previous_charges, 2),
        "current_billing": round(current_billing, 2),
        "calculated_total": round(calculated_total, 2),
        "total_amount_due": total_amount_due,
        "difference": difference,
        "is_match": is_match,
    }

    return utility_bill


def postprocess_pse_gas(
    utility_bill: Dict[str, Any],
    tolerance: float = 0.01,
) -> Dict[str, Any]:
    """
    Combined post-processing for PSE gas bills:
    - Validates line item charges sum to current natural gas charges
    - Validates total amount due calculation

    Args:
        utility_bill: Parsed JSON/dict in the PSEGasBillExtract shape.
        tolerance: Allowed absolute difference before is_match becomes False.

    Returns:
        The same dict with validation objects added.
    """
    utility_bill = compute_line_item_charges_validation(utility_bill, tolerance)
    utility_bill = compute_total_amount_validation(utility_bill, tolerance)
    return utility_bill


def check_validation_passed(utility_bill: Dict[str, Any]) -> bool:
    """
    Check if all validation checks passed for PSE gas bills.

    This function checks:
    - line_item_charges_validation["is_match"] in charges_level_data
    - total_amount_validation["is_match"] in statement_level_data

    Args:
        utility_bill: The extracted utility bill dictionary after post-processing.

    Returns:
        True if all validations passed (all is_match are True or None), False otherwise.
    """
    # Check line_item_charges_validation
    charges_data = utility_bill.get("charges_level_data", {})
    line_item_charges_validation = charges_data.get("line_item_charges_validation", {})
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
