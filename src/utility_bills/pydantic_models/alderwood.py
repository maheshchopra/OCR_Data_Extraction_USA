from pydantic import BaseModel, Field
from typing import Optional, List


class LineItemCharge(BaseModel):
    """Individual line item charge within a service category."""

    charge_description: Optional[str] = None
    rate: Optional[float] = None
    usage: Optional[float] = None
    charge_amount: Optional[float] = None


class LineItemChargesValidation(BaseModel):
    """Used to validate the sum of line item charges with the service total."""

    sum_line_item_charges: Optional[float] = None
    service_total: Optional[float] = None
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
    """Service charge category (Water or Sewer) with line items."""

    service_type: Optional[str] = None
    line_items: List[LineItemCharge] = Field(default_factory=list)
    service_total: Optional[float] = None
    line_item_charges_validation: Optional[LineItemChargesValidation] = None


class MeterLevelData(BaseModel):
    """Meter reading information from the Meter Information table."""

    meter_type: Optional[str] = None
    meter_number: Optional[str] = None
    read_date_present: Optional[str] = None
    read_date_previous: Optional[str] = None
    billing_days: Optional[int] = None
    meter_reading_present: Optional[float] = None
    meter_reading_previous: Optional[float] = None
    usage: Optional[float] = None
    usage_unit_of_measurement: Optional[str] = None
    usage_in_gallons: Optional[float] = None
    meter_size: Optional[float] = None
    meter_location: Optional[str] = None


class AlderwoodBillExtract(BaseModel):
    """Complete Alderwood Water & Wastewater District bill extraction."""

    statement_level_data: StatementLevelData
    account_level_data: AccountLevelData
    charges_level_data: List[ChargesLevelData] = Field(default_factory=list)
    meter_level_data: List[MeterLevelData] = Field(default_factory=list)
