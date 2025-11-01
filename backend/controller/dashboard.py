"""Dashboard API endpoints for viewing transactions and evaluations."""

from fastapi import APIRouter, HTTPException, Query
from typing import Optional
from pydantic import BaseModel
import logging

from backend.services.database_service import DatabaseService

logger = logging.getLogger(__name__)

router = APIRouter()


class TransactionWithEvaluation(BaseModel):
    """Transaction with evaluation summary."""

    transaction_id: str
    booking_datetime: str
    amount: float
    currency: str
    originator_name: str
    beneficiary_name: str
    overall_risk_level: Optional[str] = None
    requires_action: Optional[bool] = None
    total_rules_evaluated: Optional[int] = None
    violated_rules_count: Optional[int] = None


class DashboardStats(BaseModel):
    """Dashboard statistics."""

    total_transactions: int
    transactions_requiring_action: int
    total_rule_violations: int


@router.get("/stats", response_model=DashboardStats)
async def get_dashboard_stats():
    """
    Get overall dashboard statistics.

    Returns:
        Dashboard statistics including:
        - Total transactions processed
        - Transactions requiring action
        - Total rule violations

    Example:
        GET /api/dashboard/stats
    """
    try:
        db_service = DatabaseService()
        stats = db_service.get_dashboard_stats()
        return DashboardStats(**stats)

    except Exception as e:
        logger.error(f"Failed to retrieve dashboard stats: {e}")
        raise HTTPException(
            status_code=500, detail=f"Failed to retrieve dashboard stats: {str(e)}"
        )


@router.get("/transactions")
async def get_all_transactions(
    limit: int = Query(default=100, ge=1, le=500),
    offset: int = Query(default=0, ge=0),
):
    """
    Get all transactions with their evaluation summaries.

    Args:
        limit: Maximum number of transactions to retrieve (1-500, default 100)
        offset: Number of transactions to skip (default 0)

    Returns:
        List of transactions with evaluation data

    Example:
        GET /api/dashboard/transactions?limit=50&offset=0
    """
    try:
        db_service = DatabaseService()
        transactions = db_service.get_transactions_with_evaluations(
            limit=limit, offset=offset
        )
        return {"transactions": transactions, "limit": limit, "offset": offset}

    except Exception as e:
        logger.error(f"Failed to retrieve transactions: {e}")
        raise HTTPException(
            status_code=500, detail=f"Failed to retrieve transactions: {str(e)}"
        )


@router.get("/transactions/high-risk")
async def get_high_risk_transactions(
    limit: int = Query(default=50, ge=1, le=200),
    offset: int = Query(default=0, ge=0),
):
    """
    Get high-risk transactions.

    Args:
        limit: Maximum number of transactions to retrieve (1-200, default 50)
        offset: Number of transactions to skip (default 0)

    Returns:
        List of high-risk transactions with their evaluation data

    Example:
        GET /api/dashboard/transactions/high-risk?limit=20
    """
    try:
        db_service = DatabaseService()
        transactions = db_service.get_high_risk_transactions(limit=limit, offset=offset)
        return {"transactions": transactions, "limit": limit, "offset": offset}

    except Exception as e:
        logger.error(f"Failed to retrieve high-risk transactions: {e}")
        raise HTTPException(
            status_code=500,
            detail=f"Failed to retrieve high-risk transactions: {str(e)}",
        )


@router.get("/transactions/requires-action")
async def get_transactions_requiring_action(
    limit: int = Query(default=50, ge=1, le=200),
    offset: int = Query(default=0, ge=0),
):
    """
    Get transactions that require action.

    Args:
        limit: Maximum number of transactions to retrieve (1-200, default 50)
        offset: Number of transactions to skip (default 0)

    Returns:
        List of transactions requiring action with their evaluation data

    Example:
        GET /api/dashboard/transactions/requires-action?limit=20
    """
    try:
        db_service = DatabaseService()
        transactions = db_service.get_transactions_requiring_action(
            limit=limit, offset=offset
        )
        return {"transactions": transactions, "limit": limit, "offset": offset}

    except Exception as e:
        logger.error(f"Failed to retrieve transactions requiring action: {e}")
        raise HTTPException(
            status_code=500,
            detail=f"Failed to retrieve transactions requiring action: {str(e)}",
        )


@router.get("/transactions/{transaction_id}")
async def get_transaction_details(transaction_id: str):
    """
    Get detailed information about a specific transaction including all evaluations.

    Args:
        transaction_id: The transaction ID to retrieve

    Returns:
        Transaction details with all rule evaluations

    Example:
        GET /api/dashboard/transactions/abc123
    """
    try:
        db_service = DatabaseService()

        # Get transaction
        transaction = db_service.get_transaction(transaction_id)
        if not transaction:
            raise HTTPException(
                status_code=404, detail=f"Transaction {transaction_id} not found"
            )

        # Get all evaluations for this transaction
        evaluations = db_service.get_transaction_evaluations(transaction_id)

        return {
            "transaction": transaction,
            "evaluations": evaluations,
            "total_evaluations": len(evaluations),
        }

    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Failed to retrieve transaction {transaction_id}: {e}")
        raise HTTPException(
            status_code=500,
            detail=f"Failed to retrieve transaction details: {str(e)}",
        )


@router.get("/transactions/{transaction_id}/evaluations")
async def get_transaction_evaluations(transaction_id: str):
    """
    Get all rule evaluation results for a specific transaction.

    Args:
        transaction_id: The transaction ID

    Returns:
        List of all rule evaluations for the transaction

    Example:
        GET /api/dashboard/transactions/abc123/evaluations
    """
    try:
        db_service = DatabaseService()
        evaluations = db_service.get_transaction_evaluations(transaction_id)

        return {
            "transaction_id": transaction_id,
            "evaluations": evaluations,
            "total": len(evaluations),
        }

    except Exception as e:
        logger.error(
            f"Failed to retrieve evaluations for transaction {transaction_id}: {e}"
        )
        raise HTTPException(
            status_code=500,
            detail=f"Failed to retrieve transaction evaluations: {str(e)}",
        )
