from pydantic import BaseModel, Field
from typing import Optional, List


class LineItemCharge(BaseModel):
    """Individual line item within a charge category."""

    line_item_name: Optional[str] = None
    line_item_amount: Optional[float] = None
    usage: Optional[float] = None
    unit_of_measurement: Optional[str] = None
    rate: Optional[float] = None


class LineItemChargesValidation(BaseModel):
    """Used to validate the sum of the line item charges with the charge category total."""

    sum_line_item_charges: Optional[float] = None
    charge_category_total: Optional[float] = None
    difference: Optional[float] = None
    is_match: Optional[bool] = None


class TotalAmountValidation(BaseModel):
    """Used to validate the sum of (previous balance, payments applied, and current billing) with the total amount due."""

    previous_balance: Optional[float] = None
    payments_applied: Optional[float] = None
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
    """Charge category information including line items."""

    charge_category_name: Optional[str] = None
    charge_category_total: Optional[float] = None
    line_items: List[LineItemCharge] = Field(default_factory=list)
    line_item_charges_validation: Optional[LineItemChargesValidation] = None


class MiscellaneousLevelData(BaseModel):
    """Miscellaneous information including current period and notices."""

    current_period_covered: Optional[str] = None


class ValleyViewBillExtract(BaseModel):
    """Complete Valley View Sewer District bill extraction."""

    statement_level_data: StatementLevelData
    account_level_data: AccountLevelData
    charges_level_data: List[ChargesLevelData] = Field(default_factory=list)
    miscellaneous_level_data: MiscellaneousLevelData
