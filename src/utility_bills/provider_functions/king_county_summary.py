from typing import Any, Dict


def postprocess_king_county_summary(
    utility_bill: Dict[str, Any],
    tolerance: float = 0.01,
) -> Dict[str, Any]:
    """
    Post-processing for King County account summary.

    Since account summaries don't show detailed charges or calculations,
    we don't perform complex validation. We just capture the information shown.

    Args:
        utility_bill: Parsed JSON/dict in the KingCountySummaryBillExtract shape.
        tolerance: Not used, kept for signature consistency.

    Returns:
        The same dict unchanged (no validation needed for summaries).
    """
    # Account summaries are simple - no validation needed
    # Just return the data as extracted
    return utility_bill


def check_validation_passed(utility_bill: Dict[str, Any]) -> bool:
    """
    Check if the extraction is valid.

    For account summaries, we just verify that key fields are present.

    Args:
        utility_bill: The extracted utility bill dictionary.

    Returns:
        True if key fields are present, False otherwise.
    """

    # Check that we got the essential information
    statement_data = utility_bill.get("statement_level_data", {})
    account_data = utility_bill.get("account_level_data", {})

    # Require at least account number and some financial data
    has_account_number = account_data.get("account_number") is not None
    has_total_due = statement_data.get("total_amount_due") is not None

    # Consider it valid if we have these basic fields
    return has_account_number and has_total_due
