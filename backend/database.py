"""
Database configuration and session management for the SF Comparative Analysis application.
Handles PostgreSQL connection setup, session factory, and lifecycle management.
"""

from sqlalchemy import create_engine, event
from sqlalchemy.orm import sessionmaker, Session
from sqlalchemy.pool import QueuePool
from contextlib import contextmanager
from typing import Generator
import logging

from .config import get_settings

logger = logging.getLogger(__name__)


class DatabaseManager:
    """Manages database connections, sessions, and lifecycle."""
    
    def __init__(self):
        self.settings = get_settings()
        self.engine = None
        self.SessionLocal = None
        self._initialize()
    
    def _initialize(self):
        """Initialize database engine and session factory."""
        try:
            self.engine = create_engine(
                self.settings.database_url,
                echo=self.settings.db_echo,
                poolclass=QueuePool,
                pool_size=self.settings.db_pool_size,
                max_overflow=self.settings.db_max_overflow,
                pool_pre_ping=self.settings.db_pool_pre_ping,
                pool_recycle=3600,  # Recycle connections after 1 hour
            )
            
            self.SessionLocal = sessionmaker(
                autocommit=False,
                autoflush=False,
                bind=self.engine,
                expire_on_commit=False,
            )
            
            # Set connection timeout
            @event.listens_for(self.engine, "connect")
            def receive_connect(dbapi_connection, connection_record):
                dbapi_connection.settimeout(30)
            
            logger.info("✓ Database engine initialized successfully")
            
        except Exception as e:
            logger.warning(f"⚠ Database initialization warning: {str(e)}")
            logger.info("  API will operate in execution-only mode")
    
    def get_session(self) -> Session:
        """Get a new database session."""
        if self.SessionLocal is None:
            raise RuntimeError("Database not initialized. Check configuration.")
        return self.SessionLocal()
    
    @contextmanager
    def session_scope(self) -> Generator[Session, None, None]:
        """
        Provide a transactional scope for database operations.
        
        Usage:
            with db_manager.session_scope() as session:
                result = session.query(Model).first()
        """
        session = self.get_session()
        try:
            yield session
            session.commit()
        except Exception:
            session.rollback()
            raise
        finally:
            session.close()
    
    def create_all_tables(self):
        """Create all database tables."""
        if self.engine is None:
            raise RuntimeError("Database not initialized")
        
        # Import models to register them with Base
        from . import models  # noqa: F401
        
        models.Base.metadata.create_all(bind=self.engine)
        logger.info("✓ All database tables created")
    
    def drop_all_tables(self):
        """Drop all database tables (use with caution)."""
        if self.engine is None:
            raise RuntimeError("Database not initialized")
        
        from . import models  # noqa: F401
        
        models.Base.metadata.drop_all(bind=self.engine)
        logger.info("✓ All database tables dropped")
    
    def verify_connection(self) -> bool:
        """Verify database connection is working."""
        try:
            with self.session_scope() as session:
                session.execute("SELECT 1")
            logger.info("✓ Database connection verified")
            return True
        except Exception as e:
            logger.warning(f"✗ Database connection failed: {str(e)}")
            return False
    
    def close(self):
        """Close all database connections."""
        if self.engine:
            self.engine.dispose()
            logger.info("✓ Database connections closed")


# Global database manager instance
_db_manager = None


def get_db_manager() -> DatabaseManager:
    """Get or create the global database manager."""
    global _db_manager
    if _db_manager is None:
        _db_manager = DatabaseManager()
    return _db_manager


def get_db() -> Generator[Session, None, None]:
    """
    FastAPI dependency for database session.
    
    Usage:
        @app.get("/items")
        def get_items(db: Session = Depends(get_db)):
            return db.query(Item).all()
    """
    db_manager = get_db_manager()
    session = db_manager.get_session()
    try:
        yield session
    finally:
        session.close()


if __name__ == "__main__":
    # Test database connection
    db_manager = get_db_manager()
    if db_manager.verify_connection():
        print("✓ Database connection successful")
    else:
        print("✗ Database connection failed")
