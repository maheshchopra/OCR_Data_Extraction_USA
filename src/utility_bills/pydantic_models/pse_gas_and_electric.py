from pydantic import BaseModel, Field
from typing import Optional, List


class LineItemCharge(BaseModel):
    """Individual line item charge within a meter/service."""

    line_item_charge_name: Optional[str] = None
    line_item_charge_amount: Optional[float] = None
    rate: Optional[str] = None
    usage: Optional[float] = None
    usage_unit_of_measurement: Optional[str] = None


class LineItemChargesValidation(BaseModel):
    """Validates that line items sum to current electric/gas charges."""

    sum_line_item_charges: Optional[float] = None
    current_charges: Optional[float] = None
    difference: Optional[float] = None
    is_match: Optional[bool] = None


class TotalAmountValidation(BaseModel):
    """Validates total amount due calculation."""

    total_previous_charges: Optional[float] = None
    current_billing: Optional[float] = None
    calculated_total: Optional[float] = None
    total_amount_due: Optional[float] = None
    difference: Optional[float] = None
    is_match: Optional[bool] = None


class StatementLevelData(BaseModel):
    """Statement-level financial information."""

    bill_date: Optional[str] = None
    previous_balance: Optional[float] = None
    total_previous_charges: Optional[float] = None
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


class ElectricMeterLevelData(BaseModel):
    """Electric meter/service-level information including usage."""

    meter_number: Optional[str] = None
    rate_schedule: Optional[str] = None

    service_from_date: Optional[str] = None
    service_to_date: Optional[str] = None
    previous_reading: Optional[float] = None
    current_reading: Optional[float] = None

    multiplier: Optional[float] = None
    usage: Optional[float] = None
    usage_unit_of_measurement: Optional[str] = None
    meter_read_type: Optional[str] = None


class GasMeterLevelData(BaseModel):
    """Natural gas meter/service-level information including usage."""

    meter_number: Optional[str] = None
    rate_schedule: Optional[str] = None

    service_from_date: Optional[str] = None
    service_to_date: Optional[str] = None
    previous_reading: Optional[float] = None
    current_reading: Optional[float] = None

    turnup: Optional[float] = None
    pressure: Optional[float] = None
    temp: Optional[float] = None
    fpv: Optional[float] = None
    btu_factor: Optional[float] = None
    ccf: Optional[float] = None

    usage: Optional[float] = None
    usage_unit_of_measurement: Optional[str] = None
    meter_read_type: Optional[str] = None


class ElectricChargesLevelData(BaseModel):
    """Electric charges and credits (from 'Your Electric Charge Details' section)."""

    line_item_charges: List[LineItemCharge] = Field(default_factory=list)
    current_electric_charges: Optional[float] = None
    line_item_charges_validation: Optional[LineItemChargesValidation] = None


class GasChargesLevelData(BaseModel):
    """Natural gas charges and credits (from 'Your Natural Gas Charge Details' section)."""

    line_item_charges: List[LineItemCharge] = Field(default_factory=list)
    current_natural_gas_charges: Optional[float] = None
    line_item_charges_validation: Optional[LineItemChargesValidation] = None


class PSEGasAndElectricBillExtract(BaseModel):
    """Complete PSE combined gas and electric bill extraction."""

    statement_level_data: StatementLevelData
    account_level_data: AccountLevelData
    electric_meter_level_data: List[ElectricMeterLevelData] = Field(
        default_factory=list
    )
    gas_meter_level_data: List[GasMeterLevelData] = Field(default_factory=list)
    electric_charges_level_data: ElectricChargesLevelData
    gas_charges_level_data: GasChargesLevelData
