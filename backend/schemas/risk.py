from pydantic import BaseModel
from typing import Dict, List


class RiskOutput(BaseModel):
    triggered_rules: Dict[str, List[str]]
    risk_score: float
