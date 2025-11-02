from uuid import UUID, uuid4
from pydantic import BaseModel, Field, ConfigDict
from typing import List, Literal, Optional


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
    ruleset_id: Optional[UUID] = Field(
        default=None,
        description="UUID linking this rule to a specific web crawl/extraction batch. Rules from the same crawl share the same ruleset_id.",
    )
