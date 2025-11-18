"""
Database Migration Script - Add Alert System and Session Tracking Tables
Run this to create new tables: alert_preferences, favorite_spots, alert_history, surf_sessions

Usage:
    python migrations/add_alert_and_session_tables.py
"""
import asyncio
import sys
import os
from dotenv import load_dotenv

# Load environment variables FIRST
load_dotenv()

# Add parent directory to path for imports
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))

from database import engine, Base
import database  # Import to ensure all models are registered


async def run_migration():
    """Create all tables defined in database.py"""
    print("🔄 Running database migration...")
    print("📋 Creating tables:")
    print("   - alert_preferences")
    print("   - favorite_spots")
    print("   - alert_history")
    print("   - surf_sessions")
    print("   (Plus any existing tables if not already created)")
    
    async with engine.begin() as conn:
        # This creates ALL tables defined in Base.metadata
        # Tables that already exist will be skipped
        await conn.run_sync(Base.metadata.create_all)
    
    print("✅ Migration complete!")
    print("\nNew endpoints available:")
    print("   POST   /api/sessions              - Log new session")
    print("   GET    /api/sessions              - List user's sessions")
    print("   GET    /api/sessions/stats        - Get session statistics")
    print("   GET    /api/sessions/{id}         - Get specific session")
    print("   PATCH  /api/sessions/{id}         - Update session")
    print("   DELETE /api/sessions/{id}         - Delete session")


if __name__ == "__main__":
    asyncio.run(run_migration())
