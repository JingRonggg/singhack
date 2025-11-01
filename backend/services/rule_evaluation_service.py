import json
from typing import List
from langchain_groq import ChatGroq
from langchain_core.messages import SystemMessage, HumanMessage

from backend.schemas import (
    Transaction,
    Rule,
    RuleEvaluationResult,
    BatchEvaluationResponse,
)
from backend.util.config import load_config


class RuleEvaluationService:
    """
    Service for evaluating transactions against compliance rules using semantic AI analysis.

    Uses LangChain + ChatGroq to perform semantic comparison between transaction data
    and rule statements.
    """

    def __init__(self, model: str = "openai/gpt-oss-120b", temperature: float = 0):
        """
        Initialize the rule evaluation service.

        Args:
            model: The Groq model to use for evaluation (default: openai/gpt-oss-120b)
            temperature: Temperature for LLM responses (0 = deterministic, default: 0)
        """
        config = load_config()
        api_key = config.get("GROQ_API_KEY")

        if not api_key:
            raise ValueError(
                "GROQ_API_KEY not found in environment. "
                "Please set it in your .env file or environment variables."
            )

        self.llm = ChatGroq(
            model=model,
            api_key=api_key,
            temperature=temperature,
        )

    def evaluate_transaction_against_rule(
        self, transaction: Transaction, rule: Rule
    ) -> RuleEvaluationResult:
        """
        Evaluate a single transaction against a single rule using semantic AI analysis.

        Args:
            transaction: The transaction to evaluate
            rule: The compliance rule to check against

        Returns:
            RuleEvaluationResult with conditions_met, confidence, reasoning, and suggested action
        """
        # Prepare transaction data as a structured summary
        transaction_summary = f"""
Transaction ID: {transaction.transaction_id}
Amount: {transaction.amount} {transaction.currency}
Originator: {transaction.originator_name} ({transaction.originator_country})
Originator Account: {transaction.originator_account}
Beneficiary: {transaction.beneficiary_name} ({transaction.beneficiary_country})
Beneficiary Account: {transaction.beneficiary_account}
Jurisdiction: {transaction.booking_jurisdiction}
Regulator: {transaction.regulator}
Channel: {transaction.channel}
Product Type: {transaction.product_type}
Booking DateTime: {transaction.booking_datetime}
Value Date: {transaction.value_date}

SWIFT Information:
SWIFT MT: {transaction.swift_mt}
Ordering Institution BIC: {transaction.ordering_institution_bic}
Beneficiary Institution BIC: {transaction.beneficiary_institution_bic}
SWIFT F50 Present: {transaction.swift_f50_present}
SWIFT F59 Present: {transaction.swift_f59_present}
SWIFT F70 Purpose: {transaction.swift_f70_purpose}
SWIFT F71 Charges: {transaction.swift_f71_charges}
Travel Rule Complete: {transaction.travel_rule_complete}

FX Information:
FX Indicator: {transaction.fx_indicator}
FX Base Currency: {transaction.fx_base_ccy}
FX Quote Currency: {transaction.fx_quote_ccy}
FX Applied Rate: {transaction.fx_applied_rate}
FX Market Rate: {transaction.fx_market_rate}
FX Spread (BPS): {transaction.fx_spread_bps}
FX Counterparty: {transaction.fx_counterparty}

Customer Information:
Customer ID: {transaction.customer_id}
Customer Type: {transaction.customer_type}
Customer Risk Rating: {transaction.customer_risk_rating}
Customer is PEP: {transaction.customer_is_pep}
KYC Last Completed: {transaction.kyc_last_completed}
KYC Due Date: {transaction.kyc_due_date}
EDD Required: {transaction.edd_required}
EDD Performed: {transaction.edd_performed}
Source of Wealth Documented: {transaction.sow_documented}

Suitability & Advisory:
Is Advised: {transaction.is_advised}
Product Complex: {transaction.product_complex}
Client Risk Profile: {transaction.client_risk_profile}
Suitability Assessed: {transaction.suitability_assessed}
Suitability Result: {transaction.suitability_result}
Product Has VA Exposure: {transaction.product_has_va_exposure}
VA Disclosure Provided: {transaction.va_disclosure_provided}

Cash & Screening:
Cash ID Verified: {transaction.cash_id_verified}
Daily Cash Total (Customer): {transaction.daily_cash_total_customer}
Daily Cash Transaction Count: {transaction.daily_cash_txn_count}
Purpose Code: {transaction.purpose_code}
Narrative: {transaction.narrative}
Sanctions Screening: {transaction.sanctions_screening}
Suspicion Determined DateTime: {transaction.suspicion_determined_datetime}
STR Filed DateTime: {transaction.str_filed_datetime}
        """.strip()

        # Create the evaluation prompt
        system_message = SystemMessage(
            content="""You are a compliance expert evaluating financial transactions against regulatory rules.

Your task is to analyze whether a transaction violates or triggers a compliance rule.

You must respond with a JSON object containing:
- conditions_met (boolean): true if the rule is violated/triggered, false otherwise
- confidence_score (float): your confidence level from 0.0 to 1.0
- reasoning (string): clear explanation of why the rule was or wasn't triggered

Be precise and thorough in your analysis. Consider all relevant transaction details."""
        )

        human_message = HumanMessage(
            content=f"""Evaluate this transaction against the following compliance rule:

RULE: {rule.statement}

TRANSACTION DETAILS:
{transaction_summary}

Does this transaction violate or trigger the rule? Provide your analysis in JSON format with:
- conditions_met: boolean
- confidence_score: float (0.0-1.0)
- reasoning: string"""
        )

        # Get LLM response
        response = self.llm.invoke([system_message, human_message])

        # Parse the JSON response
        try:
            # Extract JSON from response
            response_text = response.content.strip()

            # Sometimes LLMs wrap JSON in markdown code blocks
            if response_text.startswith("```"):
                # Remove markdown code block markers
                lines = response_text.split("\n")
                response_text = "\n".join(
                    line for line in lines if not line.strip().startswith("```")
                )

            result_data = json.loads(response_text)

            # Create the evaluation result
            return RuleEvaluationResult(
                transaction_id=transaction.transaction_id,
                rule_id=rule.rule_id,
                rule_statement=rule.statement,
                conditions_met=result_data["conditions_met"],
                confidence_score=float(result_data["confidence_score"]),
                reasoning=result_data["reasoning"],
                suggested_action=rule.suggested_action,
            )

        except (json.JSONDecodeError, KeyError) as e:
            # Fallback if JSON parsing fails
            raise Exception(
                f"Failed to parse LLM response. Error: {e}\n"
                f"Response was: {response.content}"
            )

    def evaluate_transaction_against_rules(
        self, transaction: Transaction, rules: List[Rule]
    ) -> BatchEvaluationResponse:
        """
        Evaluate a single transaction against multiple rules.

        Args:
            transaction: The transaction to evaluate
            rules: List of compliance rules to check

        Returns:
            BatchEvaluationResponse with violated rules, passed rules, and overall risk level
        """
        violated_rules = []
        passed_rules = []

        # Evaluate each rule
        for rule in rules:
            result = self.evaluate_transaction_against_rule(transaction, rule)

            if result.conditions_met:
                violated_rules.append(result)
            else:
                passed_rules.append(result)

        # Determine overall risk level
        overall_risk_level = self._determine_risk_level(violated_rules)

        # Determine if action is required
        requires_action = len(violated_rules) > 0

        return BatchEvaluationResponse(
            transaction_id=transaction.transaction_id,
            total_rules_evaluated=len(rules),
            violated_rules=violated_rules,
            passed_rules=passed_rules,
            overall_risk_level=overall_risk_level,
            requires_action=requires_action,
        )

    def _determine_risk_level(self, violated_rules: List[RuleEvaluationResult]) -> str:
        """
        Determine overall risk level based on violated rules.

        Logic:
        - If any blocking rules exist → "high"
        - Else if escalation rules > 0 OR violations > 2 → "high"
        - Else if violations > 1 → "medium"
        - Else → "low"

        Args:
            violated_rules: List of violated rules

        Returns:
            Risk level: "low", "medium", or "high"
        """
        if not violated_rules:
            return "low"

        # Check for blocking actions
        blocking_count = sum(
            1
            for rule in violated_rules
            if rule.suggested_action == "transaction blocking"
        )

        escalation_count = sum(
            1 for rule in violated_rules if rule.suggested_action == "escalation"
        )

        total_violations = len(violated_rules)

        # Apply risk determination logic
        if blocking_count > 0:
            return "high"
        elif escalation_count > 0 or total_violations > 2:
            return "high"
        elif total_violations > 1:
            return "medium"
        else:
            return "low"
