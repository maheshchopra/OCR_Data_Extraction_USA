from typing import Any, Dict, List


def compute_line_item_charges_validation(
    utility_bill: Dict[str, Any],
    tolerance: float = 0.01,
) -> Dict[str, Any]:
    """
    For CenTrio bills:
    - Sum all service_charges[].charge_amount from charges_level_data
    - Compare that sum to subtotal
    - Attach a line_item_charges_validation object with details.

    Args:
        utility_bill: Parsed JSON/dict in the CenTrioBillExtract shape.
        tolerance: Allowed absolute difference before is_match becomes False.

    Returns:
        The same dict, mutated in-place and also returned, with
        charges_level_data["line_item_charges_validation"] populated.
    """

    charges_data: Dict[str, Any] = utility_bill.get("charges_level_data", {})
    service_charges: List[Dict[str, Any]] = charges_data.get("service_charges", [])
    taxes: List[Dict[str, Any]] = charges_data.get("taxes", [])

    # Sum up all charge_amount values from service_charges (treat None as 0)
    sum_service_charges = sum(
        (item.get("charge_amount") or 0.0) for item in service_charges
    )

    sum_taxes = sum((item.get("tax_amount") or 0.0) for item in taxes)

    # Total line items = service charges + taxes
    sum_line_items = sum_service_charges + sum_taxes

    subtotal = charges_data.get("subtotal")

    # Default values if subtotal is missing
    if subtotal is None:
        difference = None
        is_match = None
    else:
        # Round to cents to avoid tiny float errors
        sum_line_items_rounded = round(sum_line_items, 2)
        difference = round(sum_line_items_rounded - subtotal, 2)
        is_match = abs(difference) <= tolerance

    # Store the validation result
    charges_data["line_item_charges_validation"] = {
        "sum_service_charges": round(sum_service_charges, 2),
        "sum_taxes": round(sum_taxes, 2),
        "subtotal": subtotal,
        "difference": difference,
        "is_match": is_match,
    }

    return utility_bill


def compute_total_amount_validation(
    utility_bill: Dict[str, Any],
    tolerance: float = 0.01,
) -> Dict[str, Any]:
    """
    For CenTrio bills:
    - Sum balance + service charges + taxes + account charges
    - Compare that sum to total_amount_due
    - Attach a total_amount_validation object to statement_level_data.

    Args:
        utility_bill: Parsed JSON/dict in the CenTrioBillExtract shape.
        tolerance: Allowed absolute difference before is_match becomes False.

    Returns:
        The same dict, mutated in-place and also returned, with
        statement_level_data["total_amount_validation"] populated.
    """

    statement_data = utility_bill.get("statement_level_data", {})
    charges_data: Dict[str, Any] = utility_bill.get("charges_level_data", {})

    # Get balance (treat None as 0)
    balance = statement_data.get("balance") or 0.0

    # Sum all service charges
    service_charges: List[Dict[str, Any]] = charges_data.get("service_charges", [])
    sum_service_charges = sum(
        (item.get("charge_amount") or 0.0) for item in service_charges
    )

    # Sum all taxes
    taxes: List[Dict[str, Any]] = charges_data.get("taxes", [])
    sum_taxes = sum((item.get("tax_amount") or 0.0) for item in taxes)

    # Sum all account charges
    account_charges: List[Dict[str, Any]] = charges_data.get("account_charges", [])
    sum_account_charges = sum(
        (item.get("charge_amount") or 0.0) for item in account_charges
    )

    # Calculate expected total
    calculated_total = balance + sum_service_charges + sum_taxes + sum_account_charges

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
        "sum_service_charges": round(sum_service_charges, 2),
        "sum_taxes": round(sum_taxes, 2),
        "sum_account_charges": round(sum_account_charges, 2),
        "calculated_total": round(calculated_total, 2),
        "total_amount_due": total_amount_due,
        "difference": difference,
        "is_match": is_match,
    }

    return utility_bill


def postprocess_centrio(
    utility_bill: Dict[str, Any],
    tolerance: float = 0.01,
) -> Dict[str, Any]:
    """
    Combined post-processing for CenTrio:
    - Validates line item charges (service charges sum vs subtotal)
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
