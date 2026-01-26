from pydantic import BaseModel, Field
from typing import List, Optional


class ProviderWebsite(BaseModel):
    type: str = ""
    link: str = ""


class ProviderPhone(BaseModel):
    type: str = ""
    phone: str = ""
    time: str = ""


class ProviderEmail(BaseModel):
    type: str = ""
    email: str = ""


class ProviderAddress(BaseModel):
    type: str = ""
    address_line1: str = ""
    address_line2: str = ""
    city_state_zip: str = ""


class CustomerName(BaseModel):
    type: str = ""
    name: str = ""


class Payment(BaseModel):
    payment_details: str = ""
    payment_date: str = ""
    payment_amount: Optional[float] = None


class LateFee(BaseModel):
    late_fee_details: str = ""
    late_fee_date: str = ""
    late_fee_amount: Optional[float] = None


class Adjustment(BaseModel):
    adjustment_details: str = ""
    adjustment_date: str = ""
    adjustment_amount: Optional[float] = None


class StatementLevelData(BaseModel):
    provider: str = ""
    provider_website: List[ProviderWebsite] = Field(default_factory=list)
    provider_customer_service_phone: List[ProviderPhone] = Field(default_factory=list)
    provider_customer_service_email: List[ProviderEmail] = Field(default_factory=list)
    provider_address: List[ProviderAddress] = Field(default_factory=list)

    account_number: str = ""
    invoice_number: str = ""
    customer_number: str = ""
    customer_name: List[CustomerName] = Field(default_factory=list)

    service_address: str = ""
    service_city_state_zip: str = ""
    billing_address: str = ""
    billing_city_state_zip: str = ""

    bill_date: str = ""
    previous_balance: Optional[float] = None
    payments_applied: List[Payment] = Field(default_factory=list)
    total_payments_applied: Optional[float] = None
    payments_cutoff_date: str = ""

    late_fees_applied: List[LateFee] = Field(default_factory=list)
    total_late_fees_applied: Optional[float] = None

    adjustments_applied: List[Adjustment] = Field(default_factory=list)
    total_adjustments_applied: Optional[float] = None

    balance_forward: Optional[float] = None
    current_charges: Optional[float] = None
    total_amount_due: Optional[float] = None
    total_amount_due_date: str = ""

    late_fee_by_duedate_percentage: Optional[float] = None
    late_fee_by_duedate_amount: Optional[float] = None
    late_fee_by_duedate_details: str = ""
    grace_period_days: Optional[int] = None
    autopayment: Optional[bool] = None
    notes: str = ""


class Usage(BaseModel):
    multiplier: Optional[int] = None
    usage: Optional[float] = None
    uom: str = ""
    factor: Optional[float] = None


class MeterReading(BaseModel):
    service_from_date: str = ""
    service_to_date: str = ""
    previous_reading: Optional[float] = None
    current_reading: Optional[float] = None
    previous_reading_type: str = ""
    current_reading_type: str = ""
    usages: List[Usage] = Field(default_factory=list)


class MeterLevelData(BaseModel):
    meter_id: str = ""
    meter_number: str = ""
    meter_size: str = ""
    meter_category: str = ""
    meter_information: str = ""
    meter_reading: List[MeterReading] = Field(default_factory=list)


class LineItemCharge(BaseModel):
    line_item_charge_name: str = ""
    line_item_charge_amount: Optional[float] = None
    line_item_charge_notes: Optional[str] = None
    rate: Optional[float] = None
    rate_type: Optional[str] = None
    service_from_date: Optional[str] = None
    service_to_date: Optional[str] = None
    usage: Optional[float] = None
    usage_unit_of_measurement: Optional[str] = None
    applies_to_meters: List[str] = Field(default_factory=list)


class ChargeGroup(BaseModel):
    group_name: str = ""
    line_item_charges: List[LineItemCharge] = Field(default_factory=list)
    group_subtotal: Optional[float] = None


class Tax(BaseModel):
    tax_name: str = ""
    tax_authority: str = ""
    rate: Optional[float] = None
    taxable_amount: Optional[float] = None
    tax_amount: Optional[float] = None


class ServiceLevelData(BaseModel):
    service_name: str = ""
    service_provider: str = ""
    service_type: str = ""
    service_address: str = ""
    service_from_date: str = ""
    service_to_date: str = ""
    service_days: Optional[int] = None
    service_notes: str = ""
    meter_level_data: List[MeterLevelData] = Field(default_factory=list)
    charge_groups: List[ChargeGroup] = Field(default_factory=list)
    taxes: List[Tax] = Field(default_factory=list)
    service_charges: Optional[float] = None


class StandardUtilityBill(BaseModel):
    """Standard uniform template for all utility bills."""

    schema_version: str = "1.0"
    currency: str = "USD"
    statement_level_data: StatementLevelData
    service_level_data: List[ServiceLevelData] = Field(default_factory=list)
