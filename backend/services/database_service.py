"""Database service for storing and retrieving transactions, rules, and evaluations."""

from typing import List, Optional, Dict, Any
import logging

from backend.config.supabase import get_supabase_client
from backend.schemas import (
    Transaction,
    Rule,
    RuleEvaluationResult,
    BatchEvaluationResponse,
)

logger = logging.getLogger(__name__)


class DatabaseService:
    """Service for database operations on transactions, rules, and evaluations."""

    def __init__(self):
        """Initialize database service with Supabase client."""
        self.client = get_supabase_client()

    def store_transaction(self, transaction: Transaction) -> Dict[str, Any]:
        """
        Store a transaction in the database.

        Args:
            transaction: Transaction object to store

        Returns:
            Stored transaction data from database

        Raises:
            Exception: If storage fails
        """
        try:
            # Convert transaction to dict for storage
            transaction_data = transaction.model_dump()

            # Insert or update transaction
            result = (
                self.client.table("transactions")
                .upsert(transaction_data, on_conflict="transaction_id")
                .execute()
            )

            logger.info(f"Stored transaction: {transaction.transaction_id}")
            return result.data[0] if result.data else {}

        except Exception as e:
            logger.error(
                f"Failed to store transaction {transaction.transaction_id}: {e}"
            )
            raise

    def store_rule(self, rule: Rule) -> Dict[str, Any]:
        """
        Store a rule in the database.

        Args:
            rule: Rule object to store

        Returns:
            Stored rule data from database

        Raises:
            Exception: If storage fails
        """
        try:
            # Convert rule to dict for storage
            rule_data = rule.model_dump()
            # Convert UUID to string for storage
            rule_data["rule_id"] = str(rule_data["rule_id"])

            # Insert or update rule
            result = (
                self.client.table("rules")
                .upsert(rule_data, on_conflict="rule_id")
                .execute()
            )

            logger.info(f"Stored rule: {rule.rule_id}")
            return result.data[0] if result.data else {}

        except Exception as e:
            logger.error(f"Failed to store rule {rule.rule_id}: {e}")
            raise

    def store_rule_evaluation(self, evaluation: RuleEvaluationResult) -> Dict[str, Any]:
        """
        Store a rule evaluation result in the database.

        Args:
            evaluation: RuleEvaluationResult object to store

        Returns:
            Stored evaluation data from database

        Raises:
            Exception: If storage fails
        """
        try:
            # Convert evaluation to dict for storage
            eval_data = evaluation.model_dump()
            # Convert UUID to string
            eval_data["rule_id"] = str(eval_data["rule_id"])

            # Insert or update evaluation
            result = (
                self.client.table("rule_evaluations")
                .upsert(eval_data, on_conflict="transaction_id,rule_id")
                .execute()
            )

            logger.info(
                f"Stored evaluation for transaction {evaluation.transaction_id} "
                f"and rule {evaluation.rule_id}"
            )
            return result.data[0] if result.data else {}

        except Exception as e:
            logger.error(
                f"Failed to store evaluation for transaction {evaluation.transaction_id}: {e}"
            )
            raise

    def store_batch_evaluation(
        self, transaction_id: str, batch_response: BatchEvaluationResponse
    ) -> Dict[str, Any]:
        """
        Store a batch evaluation summary in the database.

        Args:
            transaction_id: Transaction ID
            batch_response: BatchEvaluationResponse object

        Returns:
            Stored batch evaluation data from database

        Raises:
            Exception: If storage fails
        """
        try:
            batch_data = {
                "transaction_id": transaction_id,
                "total_rules_evaluated": batch_response.total_rules_evaluated,
                "violated_rules_count": len(batch_response.violated_rules),
                "passed_rules_count": len(batch_response.passed_rules),
                "overall_risk_level": batch_response.overall_risk_level,
                "requires_action": batch_response.requires_action,
            }

            # Insert or update batch evaluation
            result = (
                self.client.table("batch_evaluations")
                .upsert(batch_data, on_conflict="transaction_id")
                .execute()
            )

            logger.info(f"Stored batch evaluation for transaction {transaction_id}")
            return result.data[0] if result.data else {}

        except Exception as e:
            logger.error(
                f"Failed to store batch evaluation for transaction {transaction_id}: {e}"
            )
            raise

    def store_complete_evaluation(
        self,
        transaction: Transaction,
        rules: List[Rule],
        batch_response: BatchEvaluationResponse,
    ) -> None:
        """
        Store complete evaluation including transaction, rules, and all results.

        Args:
            transaction: Transaction object
            rules: List of Rule objects evaluated
            batch_response: BatchEvaluationResponse with all evaluation results

        Raises:
            Exception: If storage fails
        """
        try:
            # Store transaction
            self.store_transaction(transaction)

            # Store all rules
            for rule in rules:
                self.store_rule(rule)

            # Store all individual evaluations
            all_evaluations = (
                batch_response.violated_rules + batch_response.passed_rules
            )
            for evaluation in all_evaluations:
                self.store_rule_evaluation(evaluation)

            # Store batch evaluation summary
            self.store_batch_evaluation(transaction.transaction_id, batch_response)

            logger.info(
                f"Stored complete evaluation for transaction {transaction.transaction_id}"
            )

        except Exception as e:
            logger.error(
                f"Failed to store complete evaluation for transaction {transaction.transaction_id}: {e}"
            )
            raise

    def get_transaction(self, transaction_id: str) -> Optional[Dict[str, Any]]:
        """
        Retrieve a transaction by ID.

        Args:
            transaction_id: Transaction ID to retrieve

        Returns:
            Transaction data or None if not found
        """
        try:
            result = (
                self.client.table("transactions")
                .select("*")
                .eq("transaction_id", transaction_id)
                .execute()
            )

            return result.data[0] if result.data else None

        except Exception as e:
            logger.error(f"Failed to retrieve transaction {transaction_id}: {e}")
            raise

    def get_transaction_evaluations(self, transaction_id: str) -> List[Dict[str, Any]]:
        """
        Retrieve all rule evaluations for a transaction.

        Args:
            transaction_id: Transaction ID

        Returns:
            List of evaluation results
        """
        try:
            result = (
                self.client.table("rule_evaluations")
                .select("*")
                .eq("transaction_id", transaction_id)
                .execute()
            )

            return result.data if result.data else []

        except Exception as e:
            logger.error(
                f"Failed to retrieve evaluations for transaction {transaction_id}: {e}"
            )
            raise

    def get_all_transactions(
        self, limit: int = 100, offset: int = 0
    ) -> List[Dict[str, Any]]:
        """
        Retrieve all transactions with pagination.

        Args:
            limit: Maximum number of transactions to retrieve
            offset: Number of transactions to skip

        Returns:
            List of transactions
        """
        try:
            result = (
                self.client.table("transactions")
                .select("*")
                .order("booking_datetime", desc=True)
                .range(offset, offset + limit - 1)
                .execute()
            )

            return result.data if result.data else []

        except Exception as e:
            logger.error(f"Failed to retrieve transactions: {e}")
            raise

    def get_transactions_with_evaluations(
        self, limit: int = 100, offset: int = 0
    ) -> List[Dict[str, Any]]:
        """
        Retrieve transactions with their evaluation summaries.

        Args:
            limit: Maximum number of transactions to retrieve
            offset: Number of transactions to skip

        Returns:
            List of transactions with evaluation data
        """
        try:
            result = (
                self.client.table("transactions")
                .select(
                    """
                    *,
                    batch_evaluations(
                        total_rules_evaluated,
                        violated_rules_count,
                        passed_rules_count,
                        overall_risk_level,
                        requires_action
                    )
                """
                )
                .order("booking_datetime", desc=True)
                .range(offset, offset + limit - 1)
                .execute()
            )

            return result.data if result.data else []

        except Exception as e:
            logger.error(f"Failed to retrieve transactions with evaluations: {e}")
            raise

    def get_high_risk_transactions(
        self, limit: int = 50, offset: int = 0
    ) -> List[Dict[str, Any]]:
        """
        Retrieve high-risk transactions.

        Args:
            limit: Maximum number of transactions to retrieve
            offset: Number of transactions to skip

        Returns:
            List of high-risk transactions
        """
        try:
            result = (
                self.client.table("batch_evaluations")
                .select(
                    """
                    *,
                    transactions(*)
                """
                )
                .eq("overall_risk_level", "high")
                .order("created_at", desc=True)
                .range(offset, offset + limit - 1)
                .execute()
            )

            return result.data if result.data else []

        except Exception as e:
            logger.error(f"Failed to retrieve high-risk transactions: {e}")
            raise

    def get_transactions_requiring_action(
        self, limit: int = 50, offset: int = 0
    ) -> List[Dict[str, Any]]:
        """
        Retrieve transactions that require action.

        Args:
            limit: Maximum number of transactions to retrieve
            offset: Number of transactions to skip

        Returns:
            List of transactions requiring action
        """
        try:
            result = (
                self.client.table("batch_evaluations")
                .select(
                    """
                    *,
                    transactions(*)
                """
                )
                .eq("requires_action", True)
                .order("created_at", desc=True)
                .range(offset, offset + limit - 1)
                .execute()
            )

            return result.data if result.data else []

        except Exception as e:
            logger.error(f"Failed to retrieve transactions requiring action: {e}")
            raise

    def get_dashboard_stats(self) -> Dict[str, Any]:
        """
        Get dashboard statistics.

        Returns:
            Dictionary with dashboard statistics
        """
        try:
            # Get total transactions
            total_txns = (
                self.client.table("transactions").select("id", count="exact").execute()
            )

            # Get risk level distribution
            risk_distribution = (
                self.client.table("batch_evaluations")
                .select("overall_risk_level", count="exact")
                .execute()
            )

            risk_distribution  # type: ignore to supress ruff

            # Get transactions requiring action
            requires_action = (
                self.client.table("batch_evaluations")
                .select("id", count="exact")
                .eq("requires_action", True)
                .execute()
            )

            # Get violated rules count
            violated_rules = (
                self.client.table("rule_evaluations")
                .select("id", count="exact")
                .eq("conditions_met", True)
                .execute()
            )

            return {
                "total_transactions": total_txns.count,
                "transactions_requiring_action": requires_action.count,
                "total_rule_violations": violated_rules.count,
            }

        except Exception as e:
            logger.error(f"Failed to retrieve dashboard stats: {e}")
            raise
