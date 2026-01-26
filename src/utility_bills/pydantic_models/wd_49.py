from pydantic import BaseModel, Field
from typing import Optional, List


class LineItem(BaseModel):
    """Individual line item charge from the charges section."""

    description: Optional[str] = None
    amount: Optional[float] = None
    rate: Optional[str] = None
    tier_range: Optional[str] = None
    charge_type: Optional[str] = None


class LineItemChargesValidation(BaseModel):
    """Validates that the sum of all line item charges matches the total charges."""

    sum_line_items: Optional[float] = None
    total_charges: Optional[float] = None
    difference: Optional[float] = None
    is_match: Optional[bool] = None


class TotalAmountValidation(BaseModel):
    """Validates total amount due calculation."""

    previous_balance: Optional[float] = None
    payments_applied: Optional[float] = None
    taxable_charges: Optional[float] = None
    sum_line_items: Optional[float] = None
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

    billing_period_start: Optional[str] = None
    billing_period_end: Optional[str] = None

    taxable_charges: Optional[float] = None

    total_amount_validation: Optional[TotalAmountValidation] = None


class AccountLevelData(BaseModel):
    """Account-level information (provider, customer, service address)."""

    provider: Optional[str] = None
    provider_website: Optional[str] = None
    provider_customer_service_phone: Optional[str] = None
    provider_customer_service_email: Optional[str] = None
    provider_address: Optional[str] = None
    provider_street_address: Optional[str] = None

    account_number: Optional[str] = None
    account_type: Optional[str] = None
    customer_name: Optional[str] = None
    service_address: Optional[str] = None

    ccf_to_gallons_conversion: Optional[float] = None


class MeterLevelData(BaseModel):
    """Meter reading and usage information."""

    meter_number: Optional[str] = None
    read_date: Optional[str] = None
    current_reading: Optional[float] = None
    prior_reading: Optional[float] = None
    usage: Optional[float] = None
    usage_unit: Optional[str] = None
    total_usage: Optional[float] = None


class ChargesLevelData(BaseModel):
    """All line item charges from the bill."""

    line_items: List[LineItem] = Field(default_factory=list)
    taxable_charges: Optional[float] = None
    total_charges: Optional[float] = None

    line_item_charges_validation: Optional[LineItemChargesValidation] = None


class WaterDistrict49BillExtract(BaseModel):
    """Complete King County Water District 49 utility bill extraction."""

    statement_level_data: StatementLevelData
    account_level_data: AccountLevelData
    meter_level_data: MeterLevelData
    charges_level_data: ChargesLevelData
