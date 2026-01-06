from pydantic import BaseModel, Field
from typing import Optional, List


class Charge(BaseModel):
    """Individual service charge line item."""

    charge_name: Optional[str] = None
    charge_amount: Optional[float] = None


class LineItemChargesValidation(BaseModel):
    """Used to validate the sum of the charges with the current billing amount."""

    sum_charges: Optional[float] = None
    current_billing: Optional[float] = None
    difference: Optional[float] = None
    is_match: Optional[bool] = None


class TotalAmountValidation(BaseModel):
    """Used to validate the sum of (previous balance + current billing) with the total amount due."""

    previous_balance: Optional[float] = None
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
    customer_number: Optional[str] = None
    account_type: Optional[str] = None
    customer_name: Optional[str] = None
    billing_address: Optional[str] = None
    service_address: Optional[str] = None
    service_days: Optional[int] = None


class ChargesLevelData(BaseModel):
    """Charges and meter reading information for the billing period."""

    read_date_previous: Optional[str] = None
    read_date_present: Optional[str] = None
    previous_reading_high: Optional[float] = None
    current_reading_high: Optional[float] = None
    previous_reading_low: Optional[float] = None
    current_reading_low: Optional[float] = None
    current_consumption: Optional[float] = None
    consumption_unit: Optional[str] = None
    same_period_last_year: Optional[float] = None

    charges: List[Charge] = Field(default_factory=list)

    line_item_charges_validation: Optional[LineItemChargesValidation] = None


class EverettBillExtract(BaseModel):
    """Complete Everett Public Works utility bill extraction."""

    statement_level_data: StatementLevelData
    account_level_data: AccountLevelData
    charges_level_data: ChargesLevelData
