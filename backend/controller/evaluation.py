from fastapi import APIRouter, HTTPException, UploadFile, File
from typing import List, Optional
from pydantic import BaseModel
import logging
import os
from uuid import uuid4

from backend.schemas import (
    Transaction,
    Rule,
    RuleEvaluationResult,
    BatchEvaluationResponse,
)
from backend.services.rule_evaluation_service import RuleEvaluationService
from backend.services.database_service import DatabaseService
from backend.services.transaction_loader import TransactionLoaderService

logger = logging.getLogger(__name__)

router = APIRouter()

# Upload directory for CSV files
UPLOAD_DIR = "data/uploads"
os.makedirs(UPLOAD_DIR, exist_ok=True)


class EvaluationRequest(BaseModel):
    """Request model for transaction evaluation."""

    transaction: Transaction
    rules: Optional[List[Rule]] = None
    rule_ids: Optional[List[str]] = None


class SingleRuleEvaluationRequest(BaseModel):
    """Request model for evaluating a transaction against a single rule."""

    transaction: Transaction
    rule: Rule


@router.post("/evaluate", response_model=BatchEvaluationResponse)
async def evaluate_transaction(request: EvaluationRequest):
    """
    Evaluate a transaction against multiple compliance rules.

    Args:
        request: EvaluationRequest containing:
            - transaction: Transaction object with all required fields
            - rules: Optional list of Rule objects to evaluate against
            - rule_ids: Optional list of rule IDs to load from database (future feature)

    Returns:
        BatchEvaluationResponse with:
            - transaction_id
            - total_rules_evaluated
            - violated_rules (list)
            - passed_rules (list)
            - overall_risk_level (low/medium/high)
            - requires_action (boolean)

    Example:
        POST /api/evaluation/evaluate
        {
            "transaction": {
                "transaction_id": "ad66338d-b17f-47fc-a966-1b4395351b41",
                "amount": 590012.92,
                "currency": "HKD",
                ...
            },
            "rules": [
                {
                    "rule_id": "...",
                    "statement": "High-value transactions require enhanced due diligence",
                    "jurisdiction": ["HK"],
                    "source_url": "https://...",
                    "suggested_action": "enhanced due diligence"
                }
            ]
        }
    """
    try:
        # Validate that either rules or rule_ids is provided
        if not request.rules and not request.rule_ids:
            raise HTTPException(
                status_code=400,
                detail="Either 'rules' or 'rule_ids' must be provided",
            )

        # Use provided rules or load from database (future feature)
        rules = request.rules
        if request.rule_ids:
            # TODO: Load rules from database by IDs
            raise HTTPException(
                status_code=501, detail="Loading rules by ID not yet implemented"
            )

        # Initialize evaluation service
        service = RuleEvaluationService()

        # Evaluate transaction against all rules
        result = service.evaluate_transaction_against_rules(request.transaction, rules)

        # Store evaluation results in database
        if rules:  # Only store if rules are provided
            try:
                db_service = DatabaseService()
                db_service.store_complete_evaluation(
                    transaction=request.transaction,
                    rules=rules,
                    batch_response=result,
                )
                logger.info(
                    f"Stored evaluation results for transaction {request.transaction.transaction_id}"
                )
            except Exception as db_error:
                # Log database error but don't fail the request
                logger.error(f"Failed to store evaluation in database: {db_error}")
                # You could optionally add a flag to the response indicating storage failed

        return result

    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Evaluation failed: {str(e)}")


@router.post("/evaluate-batch")
async def evaluate_batch_transactions(file: UploadFile = File(...)):
    """
    Evaluate multiple transactions from a CSV file against all compliance rules in the database.

    Args:
        file: CSV file containing transactions (must match Transaction schema)

    Returns:
        Batch evaluation results for all transactions

    Example:
        POST /api/evaluation/evaluate-batch
        - file: transactions.csv (multipart/form-data)
    """
    # Validate file type
    if not file.filename.endswith(".csv"):
        raise HTTPException(status_code=400, detail="File must be a CSV file")

    # Save uploaded CSV file
    file_id = str(uuid4())
    file_path = os.path.join(UPLOAD_DIR, f"{file_id}_{file.filename}")

    try:
        with open(file_path, "wb") as f:
            f.write(await file.read())

        # Fetch rules from the latest crawl/ruleset
        db_service = DatabaseService()
        rules_data = db_service.get_latest_rules(limit=1000)

        if not rules_data:
            raise HTTPException(
                status_code=400,
                detail="No rules found in database. Please add rules before evaluating transactions.",
            )

        # Convert database rules to Rule objects
        parsed_rules = [Rule(**rule) for rule in rules_data]
        logger.info(f"Loaded {len(parsed_rules)} rules from database")

        # Load all transactions from CSV
        loader = TransactionLoaderService(file_path)
        transactions = loader.load_all_transactions()

        if not transactions:
            raise HTTPException(
                status_code=400, detail="No valid transactions found in CSV file"
            )

        logger.info(f"Loaded {len(transactions)} transactions from CSV")

        # Initialize evaluation service
        service = RuleEvaluationService()

        # Store all rules once (not per transaction)
        logger.info(f"Storing {len(parsed_rules)} rules in database")
        for rule in parsed_rules:
            try:
                db_service.store_rule(rule)
            except Exception as rule_error:
                logger.warning(f"Failed to store rule {rule.rule_id}: {rule_error}")

        # Evaluate each transaction against all rules
        results = []
        for transaction in transactions:
            try:
                # Evaluate transaction against all rules
                result = service.evaluate_transaction_against_rules(
                    transaction, parsed_rules
                )

                # Store transaction and evaluation results in database
                try:
                    db_service.store_transaction(transaction)

                    # Store all individual rule evaluations
                    all_evaluations = result.violated_rules + result.passed_rules
                    for evaluation in all_evaluations:
                        db_service.store_rule_evaluation(evaluation)

                    # Note: batch_evaluations table is no longer used
                    # All data can be queried from rule_evaluations table

                    logger.info(
                        f"Stored evaluation results for transaction {transaction.transaction_id}"
                    )
                except Exception as db_error:
                    logger.error(
                        f"Failed to store evaluation in database for {transaction.transaction_id}: {db_error}"
                    )

                results.append(result)

            except Exception as e:
                logger.error(
                    f"Failed to evaluate transaction {transaction.transaction_id}: {e}"
                )
                # Continue with other transactions even if one fails
                results.append(
                    {"transaction_id": transaction.transaction_id, "error": str(e)}
                )

        return {
            "total_transactions": len(transactions),
            "successful_evaluations": len([r for r in results if "error" not in r]),
            "failed_evaluations": len([r for r in results if "error" in r]),
            "results": results,
        }

    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Batch evaluation failed: {e}")
        raise HTTPException(
            status_code=500, detail=f"Batch evaluation failed: {str(e)}"
        )
    finally:
        # Clean up uploaded file
        if os.path.exists(file_path):
            try:
                os.remove(file_path)
            except Exception as e:
                logger.warning(f"Failed to remove uploaded file {file_path}: {e}")


@router.post("/evaluate-single", response_model=RuleEvaluationResult)
async def evaluate_transaction_single_rule(request: SingleRuleEvaluationRequest):
    """
    Evaluate a transaction against a single compliance rule.

    Args:
        request: SingleRuleEvaluationRequest containing:
            - transaction: Transaction object
            - rule: Single Rule object

    Returns:
        RuleEvaluationResult with:
            - transaction_id
            - rule_id
            - rule_statement
            - conditions_met (boolean)
            - confidence_score (float 0.0-1.0)
            - reasoning (string)
            - suggested_action

    Example:
        POST /api/evaluation/evaluate-single
        {
            "transaction": { ... },
            "rule": {
                "rule_id": "...",
                "statement": "Transactions with PEP require enhanced due diligence",
                "jurisdiction": ["HK"],
                "source_url": "https://...",
                "suggested_action": "enhanced due diligence"
            }
        }
    """
    try:
        # Initialize evaluation service
        service = RuleEvaluationService()

        # Evaluate transaction against the rule
        result = service.evaluate_transaction_against_rule(
            request.transaction, request.rule
        )

        return result

    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Evaluation failed: {str(e)}")


@router.post("/health")
async def health_check():
    """
    Health check endpoint to verify the evaluation service is operational.

    Returns:
        Status message and service info
    """
    try:
        # Try to initialize the service to check API key is configured
        service = RuleEvaluationService()
        if service:
            return {
                "status": "healthy",
                "service": "rule_evaluation",
                "message": "Evaluation service is operational",
            }
    except Exception as e:
        raise HTTPException(
            status_code=503,
            detail=f"Service unavailable: {str(e)}",
        )
