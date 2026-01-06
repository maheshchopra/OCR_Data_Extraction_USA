from pydantic import BaseModel, Field
from typing import Optional, List


class LineItem(BaseModel):
    """Individual line item charge from the charges table."""

    date: Optional[str] = None
    invoice_number: Optional[str] = None
    description: Optional[str] = None
    quantity: Optional[float] = None
    rate: Optional[float] = None
    total: Optional[float] = None


class LineItemChargesValidation(BaseModel):
    """Validates that the sum of all line item charges matches the current charges total."""

    sum_line_items: Optional[float] = None
    current_charges: Optional[float] = None
    difference: Optional[float] = None
    is_match: Optional[bool] = None


class TotalAmountValidation(BaseModel):
    """Validates total amount due calculation."""

    previous_balance: Optional[float] = None
    payments_applied: Optional[float] = None
    current_billing: Optional[float] = None
    late_fee_applied: Optional[float] = None
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

    invoice_number: Optional[str] = None
    service_period: Optional[str] = None

    aging_30_60_days: Optional[float] = None
    aging_61_90_days: Optional[float] = None
    aging_91_plus_days: Optional[float] = None

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


class ChargesLevelData(BaseModel):
    """All line item charges from the bill."""

    line_items: List[LineItem] = Field(default_factory=list)
    current_charges: Optional[float] = None

    line_item_charges_validation: Optional[LineItemChargesValidation] = None


class RubatinoBillExtract(BaseModel):
    """Complete Rubatino Refuse Removal bill extraction."""

    statement_level_data: StatementLevelData
    account_level_data: AccountLevelData
    charges_level_data: ChargesLevelData
