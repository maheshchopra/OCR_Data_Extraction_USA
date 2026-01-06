from pydantic import BaseModel, Field
from typing import Optional, List


class LineItemCharge(BaseModel):
    """Individual line item charge within a service."""

    line_item_charge_name: Optional[str] = None
    line_item_charge_amount: Optional[float] = None


class LineItemChargesValidation(BaseModel):
    """Validates that line items sum to service total for a specific service."""

    sum_line_item_charges: Optional[float] = None
    service_total: Optional[float] = None
    difference: Optional[float] = None
    is_match: Optional[bool] = None


class Service(BaseModel):
    """A service category with its line items and total."""

    service_name: Optional[str] = None
    line_item_charges: List[LineItemCharge] = Field(default_factory=list)
    service_total: Optional[float] = None
    line_item_charges_validation: Optional[LineItemChargesValidation] = None


class ChargesLevelData(BaseModel):
    """All service charges from the bill."""

    services: List[Service] = Field(default_factory=list)
    current_service_charges: Optional[float] = None


class TotalAmountValidation(BaseModel):
    """Validates total amount due calculation."""

    previous_balance: Optional[float] = None
    payments_applied: Optional[float] = None
    current_billing: Optional[float] = None
    other_charges_and_adjustments: Optional[float] = None
    calculated_total: Optional[float] = None
    total_amount_due: Optional[float] = None
    difference: Optional[float] = None
    is_match: Optional[bool] = None


class StatementLevelData(BaseModel):
    """Statement-level financial information."""

    bill_date: Optional[str] = None
    previous_balance: Optional[float] = None
    total_previous_charges: Optional[float] = None
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


class MiscellaneousLevelData(BaseModel):
    """Miscellaneous information from the bill."""

    other_charges_and_adjustments: Optional[float] = None
    service_period_text: Optional[str] = None
    conversion_note: Optional[str] = None


class BellevueBillExtract(BaseModel):
    """Complete City of Bellevue utility bill extraction."""

    statement_level_data: StatementLevelData
    account_level_data: AccountLevelData
    charges_level_data: ChargesLevelData
    miscellaneous_level_data: MiscellaneousLevelData
