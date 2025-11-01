from pydantic import BaseModel, ConfigDict


class Transaction(BaseModel):
    """Transaction data for rule evaluation."""

    model_config = ConfigDict(from_attributes=True)
    transaction_id: str
    booking_jurisdiction: str
    regulator: str
    booking_datetime: str
    value_date: str
    amount: float
    currency: str
    channel: str
    product_type: str
    originator_name: str
    originator_account: str
    originator_country: str
    beneficiary_name: str
    beneficiary_account: str
    beneficiary_country: str
    customer_id: str
    customer_type: str
    customer_risk_rating: str
    customer_is_pep: bool
    kyc_last_completed: str
    kyc_due_date: str
    edd_required: bool
    edd_performed: bool
    sow_documented: bool
    purpose_code: str
    narrative: str
    sanctions_screening: str
    daily_cash_total_customer: float
    daily_cash_txn_count: int
