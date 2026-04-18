"""
Database initialization script for the SF Comparative Analysis application.
Creates tables, extensions, and indexes.

"""

import sys
import os
import argparse
from pathlib import Path

# Add parent directory to path for imports
sys.path.insert(0, str(Path(__file__).parent.parent))

from backend.database import get_db_manager
from backend.models import enable_pgvector_extension
import logging

logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger(__name__)


def initialize_database(drop_existing: bool = False):
    """
    Initialize the database with all tables and extensions.
    
    Args:
        drop_existing: If True, drop all tables before creating new ones
    """
    try:
        db_manager = get_db_manager()
        
        # Verify connection first
        logger.info("Verifying database connection...")
        if not db_manager.verify_connection():
            logger.error("✗ Failed to connect to database")
            logger.error("  Please verify your DATABASE_URL in .env file")
            return False
        
        # Enable pgvector extension (for vector similarity search)
        logger.info("Enabling pgvector extension...")
        try:
            enable_pgvector_extension(db_manager.engine)
        except Exception as e:
            logger.warning(f"  pgvector extension warning: {e}")
            logger.info("  Continuing without vector support (pgvector is optional)")
        
        # Drop existing tables if requested
        if drop_existing:
            logger.warning(" Dropping all existing tables...")
            db_manager.drop_all_tables()
            logger.info("✓ All tables dropped")
        
        # Create tables
        logger.info("Creating database tables...")
        db_manager.create_all_tables()
        logger.info("✓ All database tables created successfully")
        
        # Verify tables exist
        logger.info("Verifying table creation...")
        with db_manager.session_scope() as session:
            # Query metadata to verify tables
            inspector_result = session.execute("""
                SELECT table_name FROM information_schema.tables 
                WHERE table_schema = 'public'
            """)
            tables = [row[0] for row in inspector_result]
            
            if tables:
                logger.info(f"✓ Found {len(tables)} tables:")
                for table in sorted(tables):
                    logger.info(f"  - {table}")
            else:
                logger.error("✗ No tables found after creation")
                return False
        
        logger.info("\n" + "="*60)
        logger.info("✓ Database initialized successfully!")
        logger.info("="*60)
        logger.info("\nNext steps:")
        logger.info("1. Run: python scripts/seed_db.py")
        logger.info("   To seed sample data into the database")
        logger.info("\n2. Update your .env file with database credentials if needed")
        logger.info("\n3. Start the API server:")
        logger.info("   python main.py")
        
        return True
        
    except Exception as e:
        logger.error(f"✗ Database initialization failed: {str(e)}")
        logger.exception("Full error details:")
        return False


def main():
    """Main entry point."""
    parser = argparse.ArgumentParser(
        description="Initialize the SF Comparative Analysis database"
    )
    parser.add_argument(
        "--drop",
        action="store_true",
        help="Drop all existing tables before creating new ones (WARNING: destructive!)"
    )
    parser.add_argument(
        "--verify-only",
        action="store_true",
        help="Only verify connection without creating tables"
    )
    
    args = parser.parse_args()
    
    if args.verify_only:
        logger.info("Verifying database connection only...")
        db_manager = get_db_manager()
        if db_manager.verify_connection():
            logger.info("✓ Database connection verified")
            return 0
        else:
            logger.error("✗ Database connection failed")
            return 1
    
    if args.drop:
        response = input(
            "\n WARNING: This will DROP all tables and delete all data!\n"
            "Are you sure? Type 'yes' to continue: "
        )
        if response.lower() != "yes":
            logger.info("Cancelled.")
            return 1
    
    success = initialize_database(drop_existing=args.drop)
    return 0 if success else 1


if __name__ == "__main__":
    sys.exit(main())
