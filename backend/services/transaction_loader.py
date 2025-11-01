import csv
from typing import Optional, List
from backend.schemas import Transaction


class TransactionLoaderService:
    """Service for loading transactions from CSV files."""

    def __init__(self, csv_path: str):
        """
        Initialize the transaction loader service.

        Args:
            csv_path: Path to the transactions CSV file
        """
        self.csv_path = csv_path

    def _parse_row(self, row: dict) -> Transaction:
        """
        Parse a CSV row into a Transaction object.

        Args:
            row: Dictionary from CSV DictReader

        Returns:
            Transaction object
        """
        # Convert boolean fields
        row["customer_is_pep"] = row["customer_is_pep"].upper() == "TRUE"
        row["edd_required"] = row["edd_required"].upper() == "TRUE"
        row["edd_performed"] = row["edd_performed"].upper() == "TRUE"
        row["sow_documented"] = row["sow_documented"].upper() == "TRUE"
        row["swift_f50_present"] = row["swift_f50_present"].upper() == "TRUE"
        row["swift_f59_present"] = row["swift_f59_present"].upper() == "TRUE"
        row["travel_rule_complete"] = row["travel_rule_complete"].upper() == "TRUE"
        row["fx_indicator"] = row["fx_indicator"].upper() == "TRUE"
        row["is_advised"] = row["is_advised"].upper() == "TRUE"
        row["product_complex"] = row["product_complex"].upper() == "TRUE"
        row["suitability_assessed"] = row["suitability_assessed"].upper() == "TRUE"
        row["product_has_va_exposure"] = (
            row["product_has_va_exposure"].upper() == "TRUE"
        )
        row["va_disclosure_provided"] = row["va_disclosure_provided"].upper() == "TRUE"
        row["cash_id_verified"] = row["cash_id_verified"].upper() == "TRUE"

        # Convert numeric fields
        row["amount"] = float(row["amount"])
        row["daily_cash_total_customer"] = float(row["daily_cash_total_customer"])
        row["daily_cash_txn_count"] = int(row["daily_cash_txn_count"])
        row["fx_applied_rate"] = float(row["fx_applied_rate"])
        row["fx_market_rate"] = float(row["fx_market_rate"])
        row["fx_spread_bps"] = float(row["fx_spread_bps"])

        return Transaction(**row)

    def load_single_transaction(self, transaction_id: str) -> Optional[Transaction]:
        """
        Load a single transaction from CSV by transaction ID.

        Args:
            transaction_id: UUID of the transaction to load

        Returns:
            Transaction object if found, None otherwise
        """
        try:
            with open(self.csv_path, "r", encoding="utf-8") as f:
                reader = csv.DictReader(f)
                for row in reader:
                    if row["transaction_id"] == transaction_id:
                        return self._parse_row(row)
            return None
        except FileNotFoundError:
            raise FileNotFoundError(f"CSV file not found: {self.csv_path}")
        except Exception as e:
            raise Exception(f"Error loading transaction: {e}")

    def load_first_n_transactions(self, n: int) -> List[Transaction]:
        """
        Load the first N transactions from CSV.

        Args:
            n: Number of transactions to load

        Returns:
            List of Transaction objects (up to N transactions)
        """
        try:
            transactions = []
            with open(self.csv_path, "r", encoding="utf-8") as f:
                reader = csv.DictReader(f)
                for i, row in enumerate(reader):
                    if i >= n:
                        break
                    transactions.append(self._parse_row(row))

            return transactions
        except FileNotFoundError:
            raise FileNotFoundError(f"CSV file not found: {self.csv_path}")
        except Exception as e:
            raise Exception(f"Error loading transactions: {e}")

    def load_all_transactions(self) -> List[Transaction]:
        """
        Load all transactions from CSV.

        Returns:
            List of all Transaction objects
        """
        try:
            transactions = []
            with open(self.csv_path, "r", encoding="utf-8") as f:
                reader = csv.DictReader(f)
                for row in reader:
                    transactions.append(self._parse_row(row))

            return transactions
        except FileNotFoundError:
            raise FileNotFoundError(f"CSV file not found: {self.csv_path}")
        except Exception as e:
            raise Exception(f"Error loading transactions: {e}")
