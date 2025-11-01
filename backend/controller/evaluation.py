from fastapi import APIRouter, HTTPException
from typing import List, Optional
from pydantic import BaseModel

from backend.schemas import (
    Transaction,
    Rule,
    RuleEvaluationResult,
    BatchEvaluationResponse,
)
from backend.services.rule_evaluation_service import RuleEvaluationService

router = APIRouter()


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

        return result

    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Evaluation failed: {str(e)}")


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
