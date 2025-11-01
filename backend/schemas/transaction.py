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
    swift_mt: str
    ordering_institution_bic: str
    beneficiary_institution_bic: str
    swift_f50_present: bool
    swift_f59_present: bool
    swift_f70_purpose: str
    swift_f71_charges: str
    travel_rule_complete: bool
    fx_indicator: bool
    fx_base_ccy: str
    fx_quote_ccy: str
    fx_applied_rate: float
    fx_market_rate: float
    fx_spread_bps: float
    fx_counterparty: str
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
    is_advised: bool
    product_complex: bool
    client_risk_profile: str
    suitability_assessed: bool
    suitability_result: str
    product_has_va_exposure: bool
    va_disclosure_provided: bool
    cash_id_verified: bool
    daily_cash_total_customer: float
    daily_cash_txn_count: int
    sanctions_screening: str
    suspicion_determined_datetime: str
    str_filed_datetime: str
