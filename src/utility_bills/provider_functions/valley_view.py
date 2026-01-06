from typing import Any, Dict, List


def compute_charge_line_item_validation(
    utility_bill: Dict[str, Any],
    tolerance: float = 0.01,
) -> Dict[str, Any]:
    """
    For each charges_level_data category:
    - Calculate line item amounts for "UNITS @" charges (usage × rate)
    - Sum all line_items[].line_item_amount
    - Compare that sum to charge_category_total
    - Attach a line_item_charges_validation object with details.

    Args:
        utility_bill: Parsed JSON/dict in the ValleyViewBillExtract shape.
        tolerance: Allowed absolute difference before is_match becomes False.

    Returns:
        The same dict, mutated in-place and also returned, with
        charges_level_data[i]["line_item_charges_validation"] populated.
    """

    charges_level_data: List[Dict[str, Any]] = utility_bill.get(
        "charges_level_data", []
    )

    for charge in charges_level_data:
        line_items: List[Dict[str, Any]] = charge.get("line_items", [])

        # calculate line item amounts for "UNITS @" charges
        for item in line_items:
            line_item_name = item.get("line_item_name", "")

            # Check if this is a "X UNITS @" line item
            if "UNITS @" in line_item_name.upper():
                usage = item.get("usage")
                rate = item.get("rate")

                # Only recalculate if we have both usage and rate
                if usage is not None and rate is not None:
                    # Calculate: quantity × rate
                    calculated_amount = usage * rate
                    item["line_item_amount"] = round(calculated_amount, 2)

        # Sum up all line_item_amount values (treat None as 0)
        sum_line_items = sum(
            (item.get("line_item_amount") or 0.0) for item in line_items
        )

        charge_category_total = charge.get("charge_category_total")

        # Default values if charge_category_total is missing
        if charge_category_total is None:
            difference = None
            is_match = None
        else:
            # Round to cents to avoid tiny float errors
            sum_line_items_rounded = round(sum_line_items, 2)
            difference = round(sum_line_items_rounded - charge_category_total, 2)
            is_match = abs(difference) <= tolerance

        # Store the validation result under the new key
        charge["line_item_charges_validation"] = {
            "sum_line_item_charges": round(sum_line_items, 2),
            "charge_category_total": charge_category_total,
            "difference": difference,
            "is_match": is_match,
        }

    return utility_bill


def compute_total_amount_validation(
    utility_bill: Dict[str, Any],
    tolerance: float = 0.01,
) -> Dict[str, Any]:
    """
    For Valley View Sewer District bills:
    - Calculate: previous_balance + payments_applied + current_billing
    - Compare that sum to total_amount_due
    - Attach a total_amount_validation object to statement_level_data.

    Args:
        utility_bill: Parsed JSON/dict in the ValleyViewBillExtract shape.
        tolerance: Allowed absolute difference before is_match becomes False.

    Returns:
        The same dict, mutated in-place and also returned, with
        statement_level_data["total_amount_validation"] populated.
    """

    statement_data = utility_bill.get("statement_level_data", {})

    # Get values (treat None as 0)
    previous_balance = statement_data.get("previous_balance") or 0.0
    payments_applied = statement_data.get("payments_applied") or 0.0
    current_billing = statement_data.get("current_billing") or 0.0

    # Calculate expected total
    # Note: payments_applied should already be negative if it was extracted correctly
    calculated_total = previous_balance + payments_applied + current_billing

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
        "current_billing": round(current_billing, 2),
        "calculated_total": round(calculated_total, 2),
        "total_amount_due": total_amount_due,
        "difference": difference,
        "is_match": is_match,
    }

    return utility_bill


def postprocess_valley_view(
    utility_bill: Dict[str, Any],
    tolerance: float = 0.01,
) -> Dict[str, Any]:
    """
    Combined post-processing for Valley View Sewer District:
    - Validates charge line item amounts per charge category
    - Validates total amount due calculation
    """
    utility_bill = compute_charge_line_item_validation(utility_bill, tolerance)
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
    # Check charge_line_item_validation for each charge category
    charges_level_data = utility_bill.get("charges_level_data", [])
    for charge in charges_level_data:
        validation = charge.get("line_item_charges_validation", {})
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
