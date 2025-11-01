import csv
from typing import List
from backend.schemas import Transaction


def load_first_n_transactions(csv_path: str, n: int) -> List[Transaction]:
    """
    Load the first N transactions from CSV.

    Args:
        csv_path: Path to the transactions CSV file
        n: Number of transactions to load

    Returns:
        List of Transaction objects (up to N transactions)
    """
    try:
        transactions = []
        with open(csv_path, "r", encoding="utf-8") as f:
            reader = csv.DictReader(f)
            for i, row in enumerate(reader):
                if i >= n:
                    break

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

                transactions.append(Transaction(**row))

        return transactions
    except FileNotFoundError:
        raise FileNotFoundError(f"CSV file not found: {csv_path}")
    except Exception as e:
        raise Exception(f"Error loading transactions: {e}")
