from pathlib import Path
from backend.util.config import load_config


class Config:
    """Application configuration loaded from environment variables."""

    def __init__(self):
        env_vars = load_config()

        # Path to transactions CSV file
        self.TRANSACTIONS_CSV = str(
            Path(__file__).parent.parent.parent
            / "transactions_mock_1000_for_participants.csv"
        )

        # API Keys from environment
        self.GROQ_API_KEY = env_vars.get("GROQ_API_KEY")


# Singleton instance
config = Config()


__all__ = ["config"]
