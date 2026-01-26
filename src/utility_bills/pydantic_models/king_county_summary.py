from pydantic import BaseModel, Field
from typing import Optional, List


class Charge(BaseModel):
    """Individual charge line item."""

    charge_name: Optional[str] = None
    charge_amount: Optional[float] = None


class StatementLevelData(BaseModel):
    """Statement-level financial information from account summary."""

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

    discount_early_payoff: Optional[float] = None
    billing_period: Optional[str] = None


class AccountLevelData(BaseModel):
    """Account-level information (provider, customer, service address)."""

    provider: Optional[str] = None
    provider_website: Optional[str] = None
    provider_customer_service_phone: Optional[str] = None
    provider_customer_service_email: Optional[str] = None
    provider_address: Optional[str] = None

    account_number: Optional[str] = None
    invoice_number: Optional[str] = None
    account_type: Optional[str] = None
    customer_name: Optional[str] = None
    service_address: Optional[str] = None

    site_number: Optional[str] = None
    service_location_district: Optional[str] = None


class ChargesLevelData(BaseModel):
    """Charges and service information (typically minimal for account summaries)."""

    charges: List[Charge] = Field(default_factory=list)


class KingCountySummaryBillExtract(BaseModel):
    """Complete King County account summary extraction."""

    statement_level_data: StatementLevelData
    account_level_data: AccountLevelData
    charges_level_data: ChargesLevelData
