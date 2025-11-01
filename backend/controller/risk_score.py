from fastapi import APIRouter, HTTPException, status, UploadFile, File
import logging
from backend.schemas import Transaction, RiskOutput
from backend.tools.risk_score import RiskScore
from uuid import uuid4
from backend.services.transaction_loader import TransactionLoaderService
import os
import json

logger = logging.getLogger(__name__)

router = APIRouter()

UPLOAD_DIR = "data/uploads"


@router.post("/transaction-single", response_model=RiskOutput)
async def get_transaction_risk(transaction: Transaction):
    """
    EXAMPLE OUTPUT FORMAT:
    {
        "triggered_rules": {
            "booking_jurisdiction": [
                "jurisdiction with high AML scrutiny (e.g., CH, SG, HK)"
            ],
            "amount": [
                "amount > 500,000 in any currency"
            ],
            "product_type": [
                "product_type = fx_conversion or securities_trade with high amount"
            ],
            "beneficiary_country": [
                "beneficiary_country high-risk (IR, RU, CN) with cross-border flow"
            ],
            "swift_mt": [
                "missing MT code for wire transfers"
            ],
            "ordering_institution_bic": [
                "BIC not matching booking_jurisdiction"
            ],
            "beneficiary_institution_bic": [
                "BIC not matching beneficiary_country"
            ],
            "swift_f71_charges": [
                "charges field empty for large transfers"
            ],
            "fx_market_rate": [
                "market rate missing or zero for FX transactions"
            ],
            "fx_counterparty": [
                "counterparty unknown or blank"
            ],
            "kyc_last_completed": [
                "last KYC date older than 2 years"
            ],
            "kyc_due_date": [
                "kyc_due_date passed and not refreshed"
            ],
            "narrative": [
                "narrative contains unrelated or filler text"
            ],
            "sanctions_screening": [
                "screening result = potential or match with high-risk entities"
            ],
            "large_amount_cross_border": [
                "amount > 500000 and originator_country != beneficiary_country"
            ],
            "stale_kyc": [
                "kyc_due_date < today and kyc_last_completed < kyc_due_date"
            ]
        },
        "risk_score": 64.94
    }
    """
    try:
        risk_score = RiskScore()
        with open("backend/risk/detect_suspicious_v2.json", "r") as f:
            rules_json = json.load(f)
        transaction_dict = transaction.model_dump()
        result = risk_score.calculate_trans_risk(transaction_dict, rules_json)
        return result
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Error calculating transaction risk: {e}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR, detail=str(e)
        )


@router.post("/transaction-batch", response_model=RiskOutput)
async def get_transaction_risk(file: UploadFile = File(...)):
    try:
        if not file.filename.endswith(".csv"):
            raise HTTPException(status_code=400, detail="File must be a CSV file")

        file_id = str(uuid4())
        file_path = os.path.join(UPLOAD_DIR, f"{file_id}_{file.filename}")
        folder = os.path.dirname(file_path)
        if folder and not os.path.exists(folder):
            os.makedirs(folder, exist_ok=True)

        loader = TransactionLoaderService(file_path)
        transactions = loader.load_all_transactions()
        if not transactions:
            raise HTTPException(
                status_code=400, detail="No valid transactions found in CSV file"
            )
        risk_score = RiskScore()
        result = risk_score.calculate_batch_risk(transactions)
        return result
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Error calculating transaction risk: {e}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR, detail=str(e)
        )


@router.post("/format-risk", response_model=RiskOutput)
async def get_format_risk(format_doc: dict):
    """
    EXAMPLE FORMAT OUTPUT:
    {
        "triggered_rules": {
            "spelling_error_rate": [
                "High spelling error rate indicates poor document quality, potential carelessness, or AI-generated content. Frequent spelling mistakes may reduce credibility and suggest automated generation."
            ],
            "indentation_inconsistent": [
                "Inconsistent indentation may indicate careless formatting, automatic document generation, or manual tampering, reducing readability and trustworthiness."
            ]
        },
        "risk_score": 50.0
    }
    """
    try:
        risk_score = RiskScore()
        result = risk_score.get_risk_score(format_doc)
        return result
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Error calculating format risk: {e}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR, detail=str(e)
        )
