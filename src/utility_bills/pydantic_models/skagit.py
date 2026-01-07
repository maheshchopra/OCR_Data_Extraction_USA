from pydantic import BaseModel, Field
from typing import Optional, List


class LineItemCharge(BaseModel):
    """Individual line item charge within a meter/service."""

    line_item_charge_name: Optional[str] = None
    line_item_charge_amount: Optional[float] = None
    usage: Optional[float] = None
    usage_unit: Optional[str] = None
    rate: Optional[str] = None
    is_tax: Optional[bool] = None
    tax_percentage: Optional[float] = None


class LineItemChargesValidation(BaseModel):
    """Used to validate the sum of the line item charges with the current service amount."""

    sum_line_item_charges: Optional[float] = None
    current_service_amount: Optional[float] = None
    difference: Optional[float] = None
    is_match: Optional[bool] = None


class TotalAmountValidation(BaseModel):
    """Used to validate the sum of (balance forward and current billing)
    with the total amount due.
    """

    previous_balance: Optional[float] = None
    payments_applied: Optional[float] = None
    balance: Optional[float] = None
    late_fee_applied: Optional[float] = None
    transfer_in: Optional[float] = None
    utility_charges: Optional[float] = None
    municipal_tax_electric: Optional[float] = None
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

    transfer_in: Optional[float] = None
    utility_charges: Optional[float] = None
    municipal_tax_electric: Optional[float] = None

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
    """Meter/service-level information including usage and charges."""

    service_address: Optional[str] = None
    service_name: Optional[str] = None
    meter_number: Optional[str] = None

    kwh_usage: Optional[float] = None
    kvarh_usage: Optional[float] = None
    kw_demand: Optional[float] = None

    connected_load: Optional[float] = None
    load_factor: Optional[float] = None
    power_factor: Optional[float] = None
    billing_demand: Optional[float] = None

    rate_schedule: Optional[str] = None
    service_dates: Optional[str] = None
    service_days: Optional[int] = None

    current_service_amount: Optional[float] = None
    line_item_charges: List[LineItemCharge] = Field(default_factory=list)
    line_item_charges_validation: Optional[LineItemChargesValidation] = None


class SkagitPUDBillExtract(BaseModel):
    """Complete Snohomish County PUD bill extraction."""

    statement_level_data: StatementLevelData
    account_level_data: AccountLevelData
    meter_level_data: List[MeterLevelData] = Field(default_factory=list)
