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
                row["swift_f50_present"] = row["swift_f50_present"].upper() == "TRUE"
                row["swift_f59_present"] = row["swift_f59_present"].upper() == "TRUE"
                row["travel_rule_complete"] = (
                    row["travel_rule_complete"].upper() == "TRUE"
                )
                row["fx_indicator"] = row["fx_indicator"].upper() == "TRUE"
                row["is_advised"] = row["is_advised"].upper() == "TRUE"
                row["product_complex"] = row["product_complex"].upper() == "TRUE"
                row["suitability_assessed"] = (
                    row["suitability_assessed"].upper() == "TRUE"
                )
                row["product_has_va_exposure"] = (
                    row["product_has_va_exposure"].upper() == "TRUE"
                )
                row["va_disclosure_provided"] = (
                    row["va_disclosure_provided"].upper() == "TRUE"
                )
                row["cash_id_verified"] = row["cash_id_verified"].upper() == "TRUE"

                # Convert numeric fields
                row["amount"] = float(row["amount"])
                row["daily_cash_total_customer"] = float(
                    row["daily_cash_total_customer"]
                )
                row["daily_cash_txn_count"] = int(row["daily_cash_txn_count"])
                row["fx_applied_rate"] = float(row["fx_applied_rate"])
                row["fx_market_rate"] = float(row["fx_market_rate"])
                row["fx_spread_bps"] = float(row["fx_spread_bps"])

                transactions.append(Transaction(**row))

        return transactions
    except FileNotFoundError:
        raise FileNotFoundError(f"CSV file not found: {csv_path}")
    except Exception as e:
        raise Exception(f"Error loading transactions: {e}")
