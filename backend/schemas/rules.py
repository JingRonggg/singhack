from uuid import UUID, uuid4
from pydantic import BaseModel, Field, ConfigDict
from typing import List, Literal, Optional
from datetime import datetime, timezone


class Rule(BaseModel):
    """Individual rule statement that can be semantically compared against transactions."""

    """

    Temporal rule model with full audit history.
    Never delete rules - only create new versions and supersede old ones.
    """

    model_config = ConfigDict(from_attributes=True)
    rule_id: UUID = Field(default_factory=uuid4)
    statement: str = Field(
        description="Plain text rule statement that can be semantically compared against transaction fields"
    )
    jurisdiction: List[str] = Field(
        description="List of jurisdictions this rule applies to"
    )
    source_url: str = Field(description="Source URL where this rule was extracted from")
    suggested_action: Literal[
        "enhanced due diligence", "transaction blocking", "escalation"
    ] = Field(
        description="Suggested action to take when this rule is violated. Choose from: enhanced due diligence (additional KYC), transaction blocking (reject transaction), or escalation (escalate to compliance team).",
        example="enhanced due diligence",
    )

    effective_from: datetime = Field(default_factory=lambda: datetime.now(timezone.utc))
    effective_to: Optional[datetime] = Field(default=None)
    created_by: str = Field(..., max_length=100)
    created_at: datetime = Field(default_factory=lambda: datetime.now(timezone.utc))
    superseded_by: Optional[UUID] = Field(default=None)
    is_active: bool = Field(default=True)

    def supersede(
        self, new_rule_id: UUID, supersede_time: Optional[datetime] = None
    ) -> None:
        """Mark this rule as superseded by a newer version."""
        self.is_active = False
        self.superseded_by = new_rule_id
        self.effective_to = supersede_time or datetime.now(timezone.utc)

    def is_effective_at(self, check_time: datetime) -> bool:
        """Check if this rule was effective at a given time."""
        if check_time < self.effective_from:
            return False
        if self.effective_to and check_time >= self.effective_to:
            return False
        return True
