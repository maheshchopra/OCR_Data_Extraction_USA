from pydantic import BaseModel, Field
from typing import Optional, List


class UsageEntry(BaseModel):
    """Individual usage entry with value and unit of measurement."""

    value: Optional[float] = None
    unit_of_measurement: Optional[str] = None


class LineItemChargesValidation(BaseModel):
    """Used to validate the sum of all line item charges with the current charges."""

    sum_line_item_charges: Optional[float] = None
    current_charges: Optional[float] = None
    difference: Optional[float] = None
    is_match: Optional[bool] = None


class TotalAmountValidation(BaseModel):
    """Used to validate the total amount calculation."""

    balance: Optional[float] = None
    current_charges: Optional[float] = None
    calculated_total: Optional[float] = None
    total_amount_due: Optional[float] = None
    difference: Optional[float] = None
    is_match: Optional[bool] = None


class MeterLevelData(BaseModel):
    """Meter reading information from the METER READINGS table."""

    meter_number: Optional[str] = None
    service_from_date: Optional[str] = None
    service_to_date: Optional[str] = None
    service_days: Optional[int] = None
    previous_reading: Optional[float] = None
    current_reading: Optional[float] = None
    usage: List[UsageEntry] = Field(default_factory=list)


class LineItemCharge(BaseModel):
    """Individual line item charge for water/sewer services."""

    line_item_charge_name: Optional[str] = None
    line_item_charge_amount: Optional[float] = None
    rate: Optional[float] = None
    usage_cubic_feet: Optional[float] = None
    usage_gallons: Optional[float] = None


class ChargesLevelData(BaseModel):
    """Container for line item charges and their validation."""

    line_item_charges: List[LineItemCharge] = Field(default_factory=list)
    line_item_charges_validation: Optional[LineItemChargesValidation] = None


class StatementLevelData(BaseModel):
    """Statement-level financial information for Sammamish Plateau Water bills."""

    bill_date: Optional[str] = None
    previous_balance: Optional[float] = None
    payments_applied: Optional[float] = None
    payment_date: Optional[str] = None
    late_fee_applied: Optional[float] = None
    late_fee_date: Optional[str] = None

    balance: Optional[float] = None
    past_due_balance: Optional[float] = None
    current_charges: Optional[float] = None
    total_amount_due: Optional[float] = None
    total_amount_due_date: Optional[str] = None

    late_fee_by_duedate_percentage: Optional[float] = None
    late_fee_by_duedate: Optional[str] = None

    payment_amount: Optional[float] = None

    total_amount_validation: Optional[TotalAmountValidation] = None


class AccountLevelData(BaseModel):
    """Account-level information for Sammamish Plateau Water bills."""

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


class SammamishPlateauWaterBillExtract(BaseModel):
    """Complete Sammamish Plateau Water bill extraction."""

    statement_level_data: StatementLevelData
    account_level_data: AccountLevelData
    meter_level_data: List[MeterLevelData] = Field(default_factory=list)
    charges_level_data: ChargesLevelData
