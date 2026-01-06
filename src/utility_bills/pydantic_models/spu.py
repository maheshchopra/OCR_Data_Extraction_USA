from pydantic import BaseModel, Field
from typing import Optional, List


class Adjustment(BaseModel):
    """The adjustments listed in the bill."""

    adjustment_name: Optional[str] = None
    adjustment_amount: Optional[float] = None
    adjustment_date: Optional[str] = None


class OtherCharge(BaseModel):
    """The other charges listed in the bill."""

    other_charge_name: Optional[str] = None
    other_charge_amount: Optional[float] = None


class LineItemCharge(BaseModel):
    """Individual line item charge within a meter/service."""

    line_item_charge_name: Optional[str] = None
    line_item_charge_amount: Optional[float] = None
    rate: Optional[str] = None
    service_from_date: Optional[str] = None
    service_through_date: Optional[str] = None
    usage: Optional[float] = None
    usage_unit_of_measurement: Optional[str] = None
    previous_reading: Optional[float] = None
    current_reading: Optional[float] = None
    meter_number: Optional[str] = None
    service_category: Optional[str] = None


class LineItemChargesValidation(BaseModel):
    """Used to validate the sum of the line item charges with the current service amount."""

    sum_line_item_charges: Optional[float] = None
    current_service_amount: Optional[float] = None
    difference: Optional[float] = None
    is_match: Optional[bool] = None


class TotalAmountValidation(BaseModel):
    """Used to validate the sum of (the balance, the sum of the current serivce amounts,
    the current adjustments, and the current other charges) with the total amount due.
    """

    balance: Optional[float] = None
    sum_current_service_amounts: Optional[float] = None
    current_adjustments: Optional[float] = None
    current_other_charges: Optional[float] = None
    calculated_total: Optional[float] = None
    total_amount_due: Optional[float] = None
    difference: Optional[float] = None
    is_match: Optional[bool] = None


class StatementLevelData(BaseModel):
    """Statement-level financial information."""

    bill_date: Optional[str]
    previous_balance: Optional[float]
    payments_applied: Optional[float]
    payment_date: Optional[str]
    late_fee_applied: Optional[float]
    late_fee_date: Optional[str]

    balance: Optional[float]
    current_billing: Optional[float]
    total_amount_due: Optional[float]
    total_amount_due_date: Optional[str]

    late_fee_by_duedate_percentage: Optional[float]
    late_fee_by_duedate: Optional[str]

    payment_amount: Optional[float]
    latefee_amount: Optional[float]

    total_amount_validation: Optional[TotalAmountValidation] = None


class AccountLevelData(BaseModel):
    """Account-level information (provider, customer, service address)."""

    provider: Optional[str]
    provider_website: Optional[str]
    provider_customer_service_phone: Optional[str]
    provider_customer_service_email: Optional[str]
    provider_address: Optional[str]

    account_number: Optional[str]
    account_type: Optional[str]
    customer_name: Optional[str]
    service_address: Optional[str]
    service_days: Optional[int]

    multiplier_value: Optional[float] = None


class MeterLevelData(BaseModel):
    """Meter/service-level information including usage and charges."""

    service_name: Optional[str] = None
    line_item_charges: List[LineItemCharge] = Field(default_factory=list)
    current_service_amount: Optional[float] = None
    line_item_charges_validation: Optional[LineItemChargesValidation] = None


class MiscellaneousLevelData(BaseModel):
    """Miscellaneous information including adjustments and other charges."""

    adjustments: List[Adjustment] = Field(default_factory=list)
    current_adjustments: Optional[float]
    other_charges: List[OtherCharge] = Field(default_factory=list)
    current_other_charges: Optional[float] = None


class SPUBillExtract(BaseModel):
    """Complete SPU bill extraction."""

    statement_level_data: StatementLevelData
    account_level_data: AccountLevelData
    meter_level_data: List[MeterLevelData] = Field(default_factory=list)
    miscellaneous_level_data: MiscellaneousLevelData
