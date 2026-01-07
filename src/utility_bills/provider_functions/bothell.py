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
        utility_bill: Parsed JSON/dict in the BothellBillExtract shape.
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
    For City of Bothell bills:
    - Calculate: previous_balance - payments_applied + penalties_adjustments + current_billing
    - Compare that sum to total_amount_due
    - Attach a total_amount_validation object to statement_level_data.

    Args:
        utility_bill: Parsed JSON/dict in the BothellBillExtract shape.
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

    # Get penalties_adjustments (treat None as 0)
    penalties_adjustments = statement_data.get("penalties_adjustments") or 0.0

    # Get current_billing (treat None as 0)
    current_billing = statement_data.get("current_billing") or 0.0

    # Calculate expected total
    # previous_balance - payments_applied + penalties_adjustments + current_billing
    calculated_total = (
        previous_balance - payments_applied + penalties_adjustments + current_billing
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
        "penalties_adjustments": round(penalties_adjustments, 2),
        "current_billing": round(current_billing, 2),
        "calculated_total": round(calculated_total, 2),
        "total_amount_due": total_amount_due,
        "difference": difference,
        "is_match": is_match,
    }

    return utility_bill


def postprocess_bothell(
    utility_bill: Dict[str, Any],
    tolerance: float = 0.01,
) -> Dict[str, Any]:
    """
    Combined post-processing for City of Bothell:
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
