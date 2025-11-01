from uuid import UUID
from pydantic import BaseModel, Field, ConfigDict
from typing import Literal
from datetime import datetime, timezone


class RuleEvaluationResult(BaseModel):
    """Result of evaluating a transaction against a rule."""

    model_config = ConfigDict(from_attributes=True)
    transaction_id: str
    rule_id: UUID
    rule_statement: str
    conditions_met: bool
    confidence_score: float = Field(ge=0.0, le=1.0)
    reasoning: str
    suggested_action: Literal[
        "enhanced due diligence", "transaction blocking", "escalation"
    ]
    evaluated_at: datetime = Field(default_factory=lambda: datetime.now(timezone.utc))
