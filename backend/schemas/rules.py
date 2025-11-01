from uuid import UUID, uuid4
from pydantic import BaseModel, Field
from typing import Dict


class RulesSchema(BaseModel):
    """Schema for extracted rules from web content."""

    ruleset_id: UUID = Field(
        default_factory=uuid4, description="Unique identifier for the ruleset"
    )
    created_at: int = Field(description="Timestamp of ruleset creation", default=1)
    rules: Dict[str, str] = Field(
        description="Dictionary of rule numbers to rule descriptions"
    )
    source_urls: list[str] = Field(
        description="List of source URLs from which the rules were extracted"
    )


class RulesExtractionSchema(BaseModel):
    """Schema for LLM extraction - only includes fields the LLM should extract."""

    rules: Dict[str, str] = Field(
        description="Dictionary of rule numbers to rule descriptions"
    )
