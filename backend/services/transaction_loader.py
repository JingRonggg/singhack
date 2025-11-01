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

        # Convert numeric fields
        row["amount"] = float(row["amount"])
        row["daily_cash_total_customer"] = float(row["daily_cash_total_customer"])
        row["daily_cash_txn_count"] = int(row["daily_cash_txn_count"])

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
