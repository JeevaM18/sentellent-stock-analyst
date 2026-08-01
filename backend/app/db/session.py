import os
from sqlalchemy import create_engine, text
from sqlalchemy.orm import sessionmaker

from app.db.base import Base
import app.models  # Import all models to register them with Base.metadata

DATABASE_URL = os.getenv(
    "DATABASE_URL",
    "postgresql+psycopg://jeeva:jeevapassword@127.0.0.1:5432/stock_analyst"
)

# Convert postgresql:// to postgresql+psycopg:// if needed for psycopg v3
if DATABASE_URL.startswith("postgresql://") and not DATABASE_URL.startswith("postgresql+psycopg://"):
    DATABASE_URL = DATABASE_URL.replace("postgresql://", "postgresql+psycopg://", 1)

# Handle container vs host OS resolution
if "@db:5432" in DATABASE_URL and not os.path.exists("/.dockerenv"):
    DATABASE_URL = DATABASE_URL.replace("@db:5432", "@127.0.0.1:5432")

if "@localhost:5432" in DATABASE_URL:
    DATABASE_URL = DATABASE_URL.replace("@localhost:5432", "@127.0.0.1:5432")

engine = create_engine(DATABASE_URL, pool_pre_ping=True, pool_size=10, max_overflow=20)
SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)


def get_db():
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()


def test_db_connection():
    """Test database connection, verify pgvector extension, and create/verify all 9 tables."""
    try:
        with engine.connect() as conn:
            # Enable pgvector extension if not present
            conn.execute(text("CREATE EXTENSION IF NOT EXISTS vector;"))
            conn.commit()
            
            # Create all tables registered in Base.metadata
            Base.metadata.create_all(bind=engine)

            tables = list(Base.metadata.tables.keys())
            return {
                "status": "connected",
                "database": "postgresql",
                "pgvector": "enabled",
                "registered_tables_count": len(tables),
                "tables": tables,
            }
    except Exception as e:
        return {"status": "error", "message": str(e)}
