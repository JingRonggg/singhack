import csv
from typing import Optional
from backend.schemas import Transaction


def load_single_transaction(
    csv_path: str, transaction_id: str
) -> Optional[Transaction]:
    """
    Load a single transaction from CSV by transaction ID.

    Args:
        csv_path: Path to the transactions CSV file
        transaction_id: UUID of the transaction to load

    Returns:
        Transaction object if found, None otherwise
    """
    try:
        with open(csv_path, "r", encoding="utf-8") as f:
            reader = csv.DictReader(f)
            for row in reader:
                if row["transaction_id"] == transaction_id:
                    # Convert boolean fields
                    row["customer_is_pep"] = row["customer_is_pep"].upper() == "TRUE"
                    row["edd_required"] = row["edd_required"].upper() == "TRUE"
                    row["edd_performed"] = row["edd_performed"].upper() == "TRUE"
                    row["sow_documented"] = row["sow_documented"].upper() == "TRUE"

                    # Convert numeric fields
                    row["amount"] = float(row["amount"])
                    row["daily_cash_total_customer"] = float(
                        row["daily_cash_total_customer"]
                    )
                    row["daily_cash_txn_count"] = int(row["daily_cash_txn_count"])

                    return Transaction(**row)
        return None
    except FileNotFoundError:
        raise FileNotFoundError(f"CSV file not found: {csv_path}")
    except Exception as e:
        raise Exception(f"Error loading transaction: {e}")
