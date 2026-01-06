from pydantic import BaseModel, Field
from typing import Optional, List


class LineItemCharge(BaseModel):
    """Individual line item charge within an electric service meter."""

    line_item_charge_name: Optional[str] = None
    line_item_charge_amount: Optional[float] = None
    rate: Optional[str] = None
    service_from_date: Optional[str] = None
    service_through_date: Optional[str] = None
    usage: Optional[float] = None
    usage_unit_of_measurement: Optional[str] = None
    previous_reading: Optional[float] = None
    current_reading: Optional[float] = None
    kwh_multiplier: Optional[float] = None
    meter_number: Optional[str] = None
    service_category: Optional[str] = None


class LineItemChargesValidation(BaseModel):
    """Used to validate the sum of the line item charges with the current service amount."""

    sum_line_item_charges: Optional[float] = None
    current_service_amount: Optional[float] = None
    difference: Optional[float] = None
    is_match: Optional[bool] = None


class TotalAmountValidation(BaseModel):
    """Used to validate the total amount calculation."""

    balance: Optional[float] = None
    sum_current_service_amounts: Optional[float] = None
    calculated_total: Optional[float] = None
    total_amount_due: Optional[float] = None
    difference: Optional[float] = None
    is_match: Optional[bool] = None


class StatementLevelData(BaseModel):
    """Statement-level financial information for Seattle City Light bills."""

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

    total_amount_validation: Optional[TotalAmountValidation] = None


class MeterLevelData(BaseModel):
    """Meter/service-level information for electric service including usage and charges."""

    service_name: Optional[str] = None
    line_item_charges: List[LineItemCharge] = Field(default_factory=list)
    current_service_amount: Optional[float] = None
    line_item_charges_validation: Optional[LineItemChargesValidation] = None


class AccountLevelData(BaseModel):
    """Account-level information for Seattle City Light bills."""

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


class SeattleCityLightBillExtract(BaseModel):
    """Complete Seattle City Light bill extraction (statement and account level only)."""

    statement_level_data: StatementLevelData
    account_level_data: AccountLevelData
    meter_level_data: List[MeterLevelData] = Field(default_factory=list)
