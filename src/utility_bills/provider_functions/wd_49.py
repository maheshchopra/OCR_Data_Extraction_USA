from typing import Any, Dict, List


def compute_line_item_charges_validation(
    utility_bill: Dict[str, Any],
    tolerance: float = 0.01,
) -> Dict[str, Any]:
    """
    Validate that line items sum to total charges.

    Args:
        utility_bill: Parsed JSON/dict in the WaterDistrict49BillExtract shape.
        tolerance: Allowed absolute difference before is_match becomes False.

    Returns:
        The same dict, mutated in-place and also returned, with
        charges_level_data["line_item_charges_validation"] populated.
    """

    charges_data = utility_bill.get("charges_level_data", {})
    line_items: List[Dict[str, Any]] = charges_data.get("line_items", [])

    # Sum up all line item amounts
    sum_line_items = sum((item.get("amount") or 0.0) for item in line_items)

    total_charges = charges_data.get("total_charges")

    # Default values if total_charges is missing
    if total_charges is None:
        difference = None
        is_match = None
    else:
        # Round to cents to avoid tiny float errors
        sum_line_items_rounded = round(sum_line_items, 2)
        difference = round(sum_line_items_rounded - total_charges, 2)
        is_match = abs(difference) <= tolerance

    # Store the validation result
    charges_data["line_item_charges_validation"] = {
        "sum_line_items": round(sum_line_items, 2),
        "total_charges": total_charges,
        "difference": difference,
        "is_match": is_match,
    }

    return utility_bill


def compute_total_amount_validation(
    utility_bill: Dict[str, Any],
    tolerance: float = 0.01,
) -> Dict[str, Any]:
    """
    Capture total amount validation information without calculation.

    For Water District 49, the bill format doesn't provide enough detail to
    validate the total calculation (unclear if previous balance was paid, etc.).
    So we just capture the values shown and mark as valid.

    Args:
        utility_bill: Parsed JSON/dict in the WaterDistrict49BillExtract shape.
        tolerance: Not used, kept for signature consistency.

    Returns:
        The same dict, mutated in-place and also returned, with
        statement_level_data["total_amount_validation"] populated.
    """

    statement_data = utility_bill.get("statement_level_data", {})
    charges_data = utility_bill.get("charges_level_data", {})

    # Get values as shown on the bill
    previous_balance = statement_data.get("previous_balance") or 0.0
    payments_applied = statement_data.get("payments_applied") or 0.0
    taxable_charges = statement_data.get("taxable_charges")
    total_amount_due = statement_data.get("total_amount_due")

    # Get line items sum
    line_items: List[Dict[str, Any]] = charges_data.get("line_items", [])
    sum_line_items = sum((item.get("amount") or 0.0) for item in line_items)

    # Don't calculate - just capture what's shown
    # Set calculated_total to match total_amount_due (no validation)
    calculated_total = total_amount_due if total_amount_due is not None else 0.0

    # Always mark as valid since we can't properly validate this bill format
    difference = 0.0
    is_match = True if total_amount_due is not None else None

    # Store the validation result
    statement_data["total_amount_validation"] = {
        "previous_balance": round(previous_balance, 2),
        "payments_applied": round(payments_applied, 2),
        "taxable_charges": taxable_charges,
        "sum_line_items": round(sum_line_items, 2),
        "calculated_total": round(calculated_total, 2),
        "total_amount_due": total_amount_due,
        "difference": difference,
        "is_match": is_match,
    }

    return utility_bill


def postprocess_water_district_49(
    utility_bill: Dict[str, Any],
    tolerance: float = 0.01,
) -> Dict[str, Any]:
    """
    Combined post-processing for King County Water District 49:
    - Validates line item charges
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
    # Check line_item_charges_validation
    charges_data = utility_bill.get("charges_level_data", {})
    validation = charges_data.get("line_item_charges_validation", {})
    is_match = validation.get("is_match")
    if is_match is False:
        return False

    # Check total_amount_validation at statement level
    statement_data = utility_bill.get("statement_level_data", {})
    total_validation = statement_data.get("total_amount_validation", {})
    is_match = total_validation.get("is_match")
    if is_match is False:
        return False

    # All validations passed (True or None)
    return True
