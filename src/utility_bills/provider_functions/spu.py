from typing import Any, Dict, List


def compute_line_item_charges_validation(
    utility_bill: Dict[str, Any],
    tolerance: float = 0.01,
) -> Dict[str, Any]:
    """
    For each meter_level_data service:
    - Sum all line_item_charges[].line_item_charge_amount
    - Compare that sum to current_service_amount
    - Attach a line_item_charges_validation object with details.

    Args:
        utility_bill: Parsed JSON/dict in the UtilityBillExtract shape.
        tolerance: Allowed absolute difference before is_match becomes False.

    Returns:
        The same dict, mutated in-place and also returned, with
        meter_level_data[i]["line_item_charges_validation"] populated.
    """

    meter_level_data: List[Dict[str, Any]] = utility_bill.get("meter_level_data", [])

    for meter in meter_level_data:
        line_items: List[Dict[str, Any]] = meter.get("line_item_charges", [])

        # Sum up all line_item_charge_amount values (treat None as 0)
        sum_line_items = sum(
            (item.get("line_item_charge_amount") or 0.0) for item in line_items
        )

        current_service_amount = meter.get("current_service_amount")

        # Default values if current_service_amount is missing
        if current_service_amount is None:
            difference = None
            is_match = None
        else:
            # Round to cents to avoid tiny float errors
            sum_line_items_rounded = round(sum_line_items, 2)
            difference = round(sum_line_items_rounded - current_service_amount, 2)
            is_match = abs(difference) <= tolerance

        # Store the validation result under the new key
        meter["line_item_charges_validation"] = {
            "sum_line_item_charges": round(sum_line_items, 2),
            "current_service_amount": current_service_amount,
            "difference": difference,
            "is_match": is_match,
        }

    return utility_bill


def compute_total_amount_validation(
    utility_bill: Dict[str, Any],
    tolerance: float = 0.01,
) -> Dict[str, Any]:
    """
    For Seattle Public Utilities bills:
    - Sum balance + all current_service_amount values from meter_level_data
    - Compare that sum to total_amount_due
    - Attach a total_amount_validation object to statement_level_data.

    Args:
        utility_bill: Parsed JSON/dict in the UtilityBillExtract shape.
        tolerance: Allowed absolute difference before is_match becomes False.

    Returns:
        The same dict, mutated in-place and also returned, with
        statement_level_data["total_amount_validation"] populated.
    """

    statement_data = utility_bill.get("statement_level_data", {})
    meter_level_data: List[Dict[str, Any]] = utility_bill.get("meter_level_data", [])

    # Get balance (treat None as 0)
    balance = statement_data.get("balance") or 0.0

    # Sum all current_service_amount values from meter_level_data
    sum_service_amounts = sum(
        (meter.get("current_service_amount") or 0.0) for meter in meter_level_data
    )

    # Get current_adjustments and current_other_charges from miscellaneous_level_data
    misc_data = utility_bill.get("miscellaneous_level_data", {})
    current_adjustments = misc_data.get("current_adjustments") or 0.0
    current_other_charges = misc_data.get("current_other_charges") or 0.0

    # Calculate expected total
    calculated_total = (
        balance + sum_service_amounts + current_adjustments + current_other_charges
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
        "balance": round(balance, 2),
        "sum_current_service_amounts": round(sum_service_amounts, 2),
        "current_adjustments": round(current_adjustments, 2),
        "current_other_charges": round(current_other_charges, 2),
        "calculated_total": round(calculated_total, 2),
        "total_amount_due": total_amount_due,
        "difference": difference,
        "is_match": is_match,
    }

    return utility_bill


def postprocess_seattle_public_utilities(
    utility_bill: Dict[str, Any],
    tolerance: float = 0.01,
) -> Dict[str, Any]:
    """
    Combined post-processing for Seattle Public Utilities:
    - Validates line item charges per service
    - Validates total amount due calculation
    """
    utility_bill = compute_line_item_charges_validation(utility_bill, tolerance)
    utility_bill = compute_total_amount_validation(utility_bill, tolerance)
    return utility_bill


def check_validation_passed(utility_bill: Dict[str, Any]) -> bool:
    """
    Check if all validation checks passed (all is_match values are True or None).

    This function checks:
    - All line_item_charges_validation["is_match"] in meter_level_data
    - total_amount_validation["is_match"] in statement_level_data

    Args:
        utility_bill: The extracted utility bill dictionary after post-processing.

    Returns:
        True if all validations passed (all is_match are True or None), False otherwise.
    """
    # Check line_item_charges_validation for each meter
    meter_level_data = utility_bill.get("meter_level_data", [])
    for meter in meter_level_data:
        validation = meter.get("line_item_charges_validation", {})
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
