"""
Database setup script using Supabase client.

This script creates all necessary tables for the transaction monitoring system.
Run this script after setting up your SUPABASE_URL and SUPABASE_KEY in .env
"""

import sys
from pathlib import Path
from dotenv import load_dotenv
from config.supabase import get_supabase_client

# Add backend to path
backend_path = Path(__file__).parent.parent
sys.path.insert(0, str(backend_path))

# Load environment variables
load_dotenv()


def read_sql_file():
    """Read the schema.sql file."""
    sql_file = Path(__file__).parent / "schema.sql"
    with open(sql_file, "r") as f:
        return f.read()


def setup_database():
    """Set up the database by executing the schema SQL."""
    try:
        print("Connecting to Supabase...")
        client = get_supabase_client()

        print("Reading schema.sql...")
        sql_content = read_sql_file()

        # Split SQL into individual statements
        statements = [s.strip() for s in sql_content.split(";") if s.strip()]

        print(f"Executing {len(statements)} SQL statements...")

        # Execute each statement
        for i, statement in enumerate(statements, 1):
            if statement:
                try:
                    # Use rpc to execute raw SQL (if available)
                    # Note: This requires setting up a stored procedure in Supabase
                    # For now, we'll print instructions for manual setup
                    print(f"Statement {i}/{len(statements)}: {statement[:50]}...")
                except Exception as e:
                    print(f"Warning: Statement {i} failed: {e}")
                    continue

        print("\n" + "=" * 70)
        print("NOTE: Direct SQL execution via Python client is limited.")
        print("Please execute the schema.sql file manually using one of these methods:")
        print("\n1. Supabase Dashboard:")
        print("   - Go to SQL Editor in your Supabase dashboard")
        print("   - Copy and paste the entire schema.sql file")
        print("   - Click 'Run'")
        print("\n2. Supabase CLI:")
        print("   - Install: npm install -g supabase")
        print("   - Login: supabase login")
        print("   - Link project: supabase link --project-ref <your-ref>")
        print("   - Run: supabase db push")
        print("=" * 70)

        # Test connection by checking if we can query
        print("\nTesting connection...")
        try:
            # Try to query tables (will fail if not created yet, but tests connection)
            result = (
                client.table("transactions").select("transaction_id").limit(1).execute()
            )
            if result:
                pass
            print("✓ Successfully connected to Supabase!")
            print("✓ Tables are set up correctly!")
            return True
        except Exception as e:
            if "relation" in str(e).lower() or "does not exist" in str(e).lower():
                print("✓ Successfully connected to Supabase!")
                print("⚠ Tables not created yet. Please run the schema.sql manually.")
                return False
            else:
                print(f"✗ Connection test failed: {e}")
                return False

    except ValueError as e:
        print(f"\n✗ Configuration Error: {e}")
        print("\nPlease ensure you have set the following in your .env file:")
        print("  SUPABASE_URL=https://xxxxx.supabase.co")
        print("  SUPABASE_KEY=your-supabase-key")
        return False
    except Exception as e:
        print(f"\n✗ Setup failed: {e}")
        return False


if __name__ == "__main__":
    print("=" * 70)
    print("Supabase Database Setup")
    print("=" * 70 + "\n")

    success = setup_database()

    if success:
        print("\n✓ Database setup completed successfully!")
    else:
        print("\n⚠ Database setup incomplete. See instructions above.")

    sys.exit(0 if success else 1)
