from pydantic import BaseModel, Field
from typing import Optional, List


class ServiceCharge(BaseModel):
    """Individual service charge."""

    charge_name: Optional[str] = None
    charge_amount: Optional[float] = None


class LineItemChargesValidation(BaseModel):
    """Used to validate the sum of service charges with the current charges total."""

    sum_service_charges: Optional[float] = None
    current_charges_total: Optional[float] = None
    difference: Optional[float] = None
    is_match: Optional[bool] = None


class TotalAmountValidation(BaseModel):
    """Used to validate the sum of (payments applied and current billing)
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

    service_period: Optional[str] = None
    cycle: Optional[str] = None

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


class MeterLevelData(BaseModel):
    """Meter-level information for usage readings."""

    meter_number: Optional[str] = None
    previous_reading: Optional[float] = None
    current_reading: Optional[float] = None
    usage: Optional[float] = None
    usage_unit_of_measurement: Optional[str] = None


class ChargesLevelData(BaseModel):
    """Charges-level information for all service charges."""

    service_charges: List[ServiceCharge] = Field(default_factory=list)
    current_charges_total: Optional[float] = None

    line_item_charges_validation: Optional[LineItemChargesValidation] = None


class FriscoBillExtract(BaseModel):
    """Complete City of Frisco bill extraction."""

    statement_level_data: StatementLevelData
    account_level_data: AccountLevelData
    meter_level_data: List[MeterLevelData] = Field(default_factory=list)
    charges_level_data: ChargesLevelData
