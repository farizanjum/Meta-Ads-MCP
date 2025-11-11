#!/usr/bin/env python3
"""
Utility script to clear/reset the OAuth database.
Run this to start fresh with OAuth tokens.
"""
import sys
from pathlib import Path

# Add parent directory to path for imports
sys.path.insert(0, str(Path(__file__).parent.parent))

from src.auth.database import init_database, clear_oauth_tokens, reset_database

def main():
    """Main entry point."""
    print("Meta Ads MCP - Database Management")
    print("=" * 50)
    
    # Initialize database first
    init_database()
    
    if len(sys.argv) > 1 and sys.argv[1] == "--reset":
        # Full reset (drops and recreates tables)
        print("\n⚠️  WARNING: This will DELETE ALL DATA including tokens!")
        response = input("Are you sure? Type 'yes' to continue: ")
        if response.lower() == 'yes':
            success = reset_database()
            if success:
                print("✅ Database reset successfully!")
            else:
                print("❌ Database reset failed!")
                sys.exit(1)
        else:
            print("Cancelled.")
    else:
        # Just clear tokens (keeps tables)
        print("\n⚠️  This will delete all OAuth tokens from the database.")
        response = input("Continue? (y/n): ")
        if response.lower() == 'y':
            count = clear_oauth_tokens()
            print(f"✅ Cleared {count} OAuth token(s) from database!")
        else:
            print("Cancelled.")

if __name__ == "__main__":
    main()

