from typing import Any, Dict
from . import scl


def postprocess_seattle_city_light_commercial(
    utility_bill: Dict[str, Any],
    tolerance: float = 0.01,
) -> Dict[str, Any]:
    """
    Post-processing for Seattle City Light commercial bills.

    Commercial bills have the same validation requirements as residential bills:
    - Line item charges per electric service should sum to current_service_amount
    - Total amount due should equal balance + sum of all current_service_amounts

    Since the data structure is identical (just extracted from a different bill format),
    we reuse the same validation logic from the standard SCL processor.

    Args:
        utility_bill: The extracted bill data dictionary
        tolerance: Allowed absolute difference for validation (default 0.01 = 1 cent)

    Returns:
        The processed data dictionary with validation fields populated
    """
    # Reuse the same validation logic as standard SCL bills
    return scl.postprocess_seattle_city_light(utility_bill, tolerance)


def check_validation_passed(utility_bill: Dict[str, Any]) -> bool:
    """
    Check if all validation checks passed for commercial bills.

    Since the data structure is identical to standard SCL bills,
    we reuse the same validation checker.

    Args:
        utility_bill: The extracted utility bill dictionary after post-processing.

    Returns:
        True if all validations passed (all is_match are True or None), False otherwise.
    """
    # Reuse the same validation checker as standard SCL bills
    return scl.check_validation_passed(utility_bill)
