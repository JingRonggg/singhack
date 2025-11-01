"""Supabase client configuration and initialization."""

import os
from typing import Optional
from supabase import create_client, Client
from dotenv import load_dotenv

# Load environment variables
load_dotenv()


class SupabaseConfig:
    """Supabase configuration and client management."""

    _instance: Optional[Client] = None

    @classmethod
    def get_client(cls) -> Client:
        """
        Get or create Supabase client instance (singleton pattern).

        Returns:
            Supabase client instance

        Raises:
            ValueError: If required environment variables are not set
        """
        if cls._instance is None:
            supabase_url = os.getenv("SUPABASE_URL")
            supabase_key = os.getenv("SUPABASE_KEY")

            if not supabase_url or not supabase_key:
                raise ValueError(
                    "SUPABASE_URL and SUPABASE_KEY environment variables must be set. "
                    "Please add them to your .env file."
                )

            cls._instance = create_client(supabase_url, supabase_key)

        return cls._instance

    @classmethod
    def reset_client(cls) -> None:
        """Reset the client instance (useful for testing)."""
        cls._instance = None


# Convenience function to get the client
def get_supabase_client() -> Client:
    """
    Get Supabase client instance.

    Returns:
        Supabase client instance
    """
    return SupabaseConfig.get_client()
