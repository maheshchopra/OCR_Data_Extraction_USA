from pydantic import BaseModel, Field
from typing import Optional, List


class LineItemChargesValidation(BaseModel):
    """Used to validate the sum of service charges with the total new charges."""

    water_total: Optional[float] = None
    sewer_total: Optional[float] = None
    storm_water_total: Optional[float] = None
    calculated_total: Optional[float] = None
    total_new_charges: Optional[float] = None
    difference: Optional[float] = None
    is_match: Optional[bool] = None


class TotalAmountValidation(BaseModel):
    """Used to validate the sum of (previous balance, payments, balance forward, and current billing)
    with the total amount due.
    """

    previous_balance: Optional[float] = None
    payments_applied: Optional[float] = None
    balance: Optional[float] = None
    current_billing: Optional[float] = None
    calculated_total: Optional[float] = None
    total_amount_due: Optional[float] = None
    difference: Optional[float] = None
    is_match: Optional[bool] = None


class StatementLevelData(BaseModel):
    """Statement-level financial information."""

    bill_date: Optional[str] = None
    previous_balance: Optional[float] = None
    payments_applied: Optional[float] = None
    payment_date: Optional[str] = None
    late_fee_applied: Optional[float] = None
    late_fee_date: Optional[str] = None

    balance: Optional[float] = None
    current_billing: Optional[float] = None
    total_amount_due: Optional[float] = None
    total_amount_due_date: Optional[str] = None

    late_fee_by_duedate_percentage: Optional[float] = None
    late_fee_by_duedate: Optional[str] = None

    payment_amount: Optional[float] = None
    latefee_amount: Optional[float] = None

    billing_period: Optional[str] = None

    total_amount_validation: Optional[TotalAmountValidation] = None


class AccountLevelData(BaseModel):
    """Account-level information (provider, customer, service address)."""

    provider: Optional[str] = None
    provider_website: Optional[str] = None
    provider_customer_service_phone: Optional[str] = None
    provider_customer_service_email: Optional[str] = None
    provider_address: Optional[str] = None

    account_number: Optional[str] = None
    account_type: Optional[str] = None
    customer_name: Optional[str] = None
    service_address: Optional[str] = None
    service_days: Optional[int] = None

    multiplier_value: Optional[float] = None


class ChargesLevelData(BaseModel):
    """Charges-level information for water, sewer, and stormwater services."""

    water_total: Optional[float] = None
    sewer_total: Optional[float] = None
    storm_water_total: Optional[float] = None
    total_new_charges: Optional[float] = None

    line_item_charges_validation: Optional[LineItemChargesValidation] = None


class AuburnBillExtract(BaseModel):
    """Complete City of Auburn bill extraction."""

    statement_level_data: StatementLevelData
    account_level_data: AccountLevelData
    charges_level_data: ChargesLevelData
