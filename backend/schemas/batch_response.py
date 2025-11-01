from pydantic import BaseModel, ConfigDict
from typing import List, Literal

from backend.schemas.evaluation_result import RuleEvaluationResult


class BatchEvaluationResponse(BaseModel):
    """Response from evaluating a transaction against multiple rules."""

    model_config = ConfigDict(from_attributes=True)
    transaction_id: str
    total_rules_evaluated: int
    violated_rules: List[RuleEvaluationResult]
    passed_rules: List[RuleEvaluationResult]
    overall_risk_level: Literal["low", "medium", "high"]
    requires_action: bool
