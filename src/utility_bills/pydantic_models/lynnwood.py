from pydantic import BaseModel, Field
from typing import Optional, List


class LineItemChargesValidation(BaseModel):
    """Validates that the sum of all meter-level charges matches the current billing total."""

    sum_meter_charges: Optional[float] = None
    current_billing: Optional[float] = None
    difference: Optional[float] = None
    is_match: Optional[bool] = None


class MeterLevelData(BaseModel):
    """Individual service line items from the billing table."""

    service_name: Optional[str] = None
    meter_number: Optional[str] = None
    previous_read_date: Optional[str] = None
    current_read_date: Optional[str] = None
    previous_meter_reading: Optional[float] = None
    current_meter_reading: Optional[float] = None
    usage: Optional[float] = None
    usage_unit_of_measurement: Optional[str] = None
    charge: Optional[float] = None


class TotalAmountValidation(BaseModel):
    """Validates total amount due calculation."""

    previous_balance: Optional[float] = None
    payments_applied: Optional[float] = None
    current_billing: Optional[float] = None
    late_fee_applied: Optional[float] = None
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
    line_item_charges_validation: Optional[LineItemChargesValidation] = None


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

    bill_number: Optional[str] = None
    customer_number: Optional[str] = None
    route_number: Optional[str] = None
    daily_per_diem: Optional[float] = None


class MiscellaneousLevelData(BaseModel):
    """Miscellaneous information from the bill."""

    adjustments: Optional[float] = None


class LynnwoodBillExtract(BaseModel):
    """Complete City of Lynnwood utility bill extraction."""

    statement_level_data: StatementLevelData
    account_level_data: AccountLevelData
    meter_level_data: List[MeterLevelData] = Field(default_factory=list)
    miscellaneous_level_data: MiscellaneousLevelData
