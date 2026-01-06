from pydantic import BaseModel, Field
from typing import Optional, List


class LineItemCharge(BaseModel):
    """Individual charge line item from the CURRENT CHARGES section."""

    charge_name: Optional[str] = None
    charge_amount: Optional[float] = None


class LineItemChargesValidation(BaseModel):
    """Used to validate the sum of the line item charges with the current billing amount."""

    sum_line_item_charges: Optional[float] = None
    current_billing: Optional[float] = None
    difference: Optional[float] = None
    is_match: Optional[bool] = None


class TotalAmountValidation(BaseModel):
    """Used to validate the sum of (previous balance + current billing + adjustments) with the total amount due."""

    previous_balance: Optional[float] = None
    current_billing: Optional[float] = None
    adjustments: Optional[float] = None
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


class ChargesLevelData(BaseModel):
    """Charges and usage information for the billing period."""

    reading_date: Optional[str] = None
    previous_reading: Optional[float] = None
    current_reading: Optional[float] = None
    usage: Optional[float] = None
    charges: List[LineItemCharge] = Field(default_factory=list)

    line_item_charges_validation: Optional[LineItemChargesValidation] = None


class MiscellaneousLevelData(BaseModel):
    """Miscellaneous information including adjustments and service period."""

    adjustments: Optional[float] = None
    service_to_date: Optional[str] = None
    service_from_date: Optional[str] = None
    previous_amount_due: Optional[float] = None


class KentBillExtract(BaseModel):
    """Complete Kent utility bill extraction."""

    statement_level_data: StatementLevelData
    account_level_data: AccountLevelData
    charges_level_data: ChargesLevelData
    miscellaneous_level_data: MiscellaneousLevelData
