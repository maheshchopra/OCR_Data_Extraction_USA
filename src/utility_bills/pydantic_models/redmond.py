from pydantic import BaseModel, Field
from typing import Optional, List


class CurrentCharge(BaseModel):
    """Individual charge from the Current Charges section."""

    charge_type: Optional[str] = None
    charge_amount: Optional[float] = None


class LineItemChargesValidation(BaseModel):
    """Validates that line items sum to current electric/gas charges."""

    sum_line_item_charges: Optional[float] = None
    current_charges: Optional[float] = None
    difference: Optional[float] = None
    is_match: Optional[bool] = None


class TotalAmountValidation(BaseModel):
    """Validates total amount due calculation."""

    previous_balance: Optional[float] = None
    payments_applied: Optional[float] = None
    adjustments_and_additional_charges: Optional[float] = None
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
    """Charges and service information for the billing period."""

    current_charges: List[CurrentCharge] = Field(default_factory=list)

    line_item_charges_validation: Optional[LineItemChargesValidation] = None


class MiscellaneousLevelData(BaseModel):
    """Miscellaneous charges and adjustments."""

    adjustments_and_additional_charges: Optional[float] = None


class RedmondBillExtract(BaseModel):
    """Complete City of Redmond utility bill extraction."""

    statement_level_data: StatementLevelData
    account_level_data: AccountLevelData
    charges_level_data: ChargesLevelData
    miscellaneous_level_data: MiscellaneousLevelData
