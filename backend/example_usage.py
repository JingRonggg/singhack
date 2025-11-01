"""
Example Usage: Transaction Evaluation with Rules

This script demonstrates how to:
1. Load transactions from CSV
2. Create compliance rules
3. Evaluate transactions against rules using semantic AI analysis
4. Analyze results and determine risk levels

Requirements:
- Set GROQ_API_KEY environment variable
- Run: uv sync
- Run: uv run python example_usage.py
"""

from backend.services import RuleEvaluationService
from backend.schemas import Rule
from backend.util import load_single_transaction, load_first_n_transactions
from backend.config import config
from uuid import uuid4


def example_single_rule_evaluation():
    """Example: Evaluate one transaction against one rule."""
    print("\n" + "=" * 80)
    print("EXAMPLE 1: Evaluate Single Transaction Against Single Rule")
    print("=" * 80 + "\n")

    # Initialize service
    service = RuleEvaluationService()

    # Load a transaction from CSV
    transaction = load_single_transaction(
        config.TRANSACTIONS_CSV, "ad66338d-b17f-47fc-a966-1b4395351b41"
    )

    if transaction is None:
        print("Transaction not found!")
        return

    print(f"Loaded transaction: {transaction.transaction_id}")
    print(f"  Amount: {transaction.amount} {transaction.currency}")
    print(f"  Jurisdiction: {transaction.booking_jurisdiction}")
    print(f"  Customer Risk: {transaction.customer_risk_rating}")
    print(f"  Is PEP: {transaction.customer_is_pep}\n")

    # Create a compliance rule
    rule = Rule(
        rule_id=uuid4(),
        statement="High-value transactions (>500,000) from/to high-risk jurisdictions should require enhanced due diligence",
        jurisdiction=["HK", "SG", "CH"],
        source_url="https://www.hkma.gov.hk/compliance/",
        suggested_action="enhanced due diligence",
    )

    print(f"Rule: {rule.statement}\n")

    # Evaluate
    print("Evaluating...")
    result = service.evaluate_transaction_against_rule(transaction, rule)

    print("Result:")
    print(f"  Conditions Met: {result.conditions_met}")
    print(f"  Confidence: {result.confidence_score:.2%}")
    print(f"  Suggested Action: {result.suggested_action}")
    print(f"  Reasoning: {result.reasoning}\n")


def example_batch_rule_evaluation():
    """Example: Evaluate one transaction against multiple rules."""
    print("\n" + "=" * 80)
    print("EXAMPLE 2: Evaluate Single Transaction Against Multiple Rules")
    print("=" * 80 + "\n")

    # Initialize service
    service = RuleEvaluationService()

    # Load a transaction
    transaction = load_single_transaction(
        config.TRANSACTIONS_CSV, "ad66338d-b17f-47fc-a966-1b4395351b41"
    )

    if transaction is None:
        print("Transaction not found!")
        return

    # Create multiple rules
    rules = [
        Rule(
            rule_id=uuid4(),
            statement="Transactions where customer is marked as PEP (Politically Exposed Person) require enhanced due diligence",
            jurisdiction=["HK", "SG", "CH"],
            source_url="https://www.hkma.gov.hk/pep/",
            suggested_action="enhanced due diligence",
        ),
        Rule(
            rule_id=uuid4(),
            statement="Transactions exceeding 1 million in any currency to beneficiaries in non-FATF countries require escalation",
            jurisdiction=["HK", "SG", "CH"],
            source_url="https://www.fatf-gafi.org/",
            suggested_action="escalation",
        ),
        Rule(
            rule_id=uuid4(),
            statement="Transactions with sanctions screening status of 'potential' should be blocked immediately",
            jurisdiction=["HK", "SG", "CH"],
            source_url="https://www.ofac.treasury.gov/",
            suggested_action="transaction blocking",
        ),
    ]

    print(f"Evaluating transaction {transaction.transaction_id}")
    print(f"Against {len(rules)} rules...\n")

    # Batch evaluate
    batch_result = service.evaluate_transaction_against_rules(transaction, rules)

    print(f"Overall Risk Level: {batch_result.overall_risk_level.upper()}")
    print(f"Requires Action: {batch_result.requires_action}")
    print(f"Total Rules Evaluated: {batch_result.total_rules_evaluated}\n")

    print(f"Violated Rules ({len(batch_result.violated_rules)}):")
    for result in batch_result.violated_rules:
        print(f"  ✗ {result.rule_statement[:60]}...")
        print(f"    Confidence: {result.confidence_score:.2%}")
        print(f"    Action: {result.suggested_action}\n")

    print(f"Passed Rules ({len(batch_result.passed_rules)}):")
    for result in batch_result.passed_rules:
        print(f"  ✓ {result.rule_statement[:60]}...\n")


def example_evaluate_multiple_transactions():
    """Example: Evaluate first N transactions from CSV."""
    print("\n" + "=" * 80)
    print("EXAMPLE 3: Evaluate Multiple Transactions from CSV")
    print("=" * 80 + "\n")

    # Initialize service
    service = RuleEvaluationService()

    # Load first 3 transactions
    transactions = load_first_n_transactions(config.TRANSACTIONS_CSV, 3)
    print(f"Loaded {len(transactions)} transactions from CSV\n")

    # Create a simple rule
    rule = Rule(
        rule_id=uuid4(),
        statement="Customer with High risk rating should trigger enhanced due diligence",
        jurisdiction=["HK", "SG", "CH"],
        source_url="https://www.hkma.gov.hk/risk/",
        suggested_action="enhanced due diligence",
    )

    print(f"Rule: {rule.statement}\n")

    # Evaluate each transaction
    high_risk_count = 0
    for transaction in transactions:
        result = service.evaluate_transaction_against_rule(transaction, rule)

        if result.conditions_met:
            print(f"⚠️  {transaction.transaction_id}: VIOLATION")
            print(
                f"   Customer: {transaction.customer_id}, Risk: {transaction.customer_risk_rating}"
            )
            high_risk_count += 1
        else:
            print(f"✓  {transaction.transaction_id}: OK")

    print(f"\nTotal Violations: {high_risk_count}/{len(transactions)}")


if __name__ == "__main__":
    try:
        # Run all examples
        example_single_rule_evaluation()
        example_batch_rule_evaluation()
        example_evaluate_multiple_transactions()

        print("\n" + "=" * 80)
        print("All examples completed successfully!")
        print("=" * 80 + "\n")

    except Exception as e:
        print(f"\nError: {e}")
        print("\nMake sure GROQ_API_KEY environment variable is set:")
        print("export GROQ_API_KEY=your_api_key_here")
        print("\nThen install dependencies:")
        print("uv sync")
        print("\nAnd run this script:")
        print("uv run python backend/example_usage.py")
