import os
from sqlalchemy import create_engine, text
from sqlalchemy.orm import sessionmaker, DeclarativeBase

DATABASE_URL = os.getenv(
    "DATABASE_URL",
    "postgresql://postgres:postgrespassword@localhost:5432/stock_analyst"
)

# Convert postgresql:// to postgresql+psycopg:// if needed for psycopg v3
if DATABASE_URL.startswith("postgresql://") and not DATABASE_URL.startswith("postgresql+psycopg://"):
    DATABASE_URL = DATABASE_URL.replace("postgresql://", "postgresql+psycopg://", 1)

engine = create_engine(DATABASE_URL, pool_pre_ping=True)
SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)


class Base(DeclarativeBase):
    pass


def get_db():
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()


def test_db_connection():
    """Test database connection and verify pgvector extension."""
    try:
        with engine.connect() as conn:
            # Enable pgvector extension if not present
            conn.execute(text("CREATE EXTENSION IF NOT EXISTS vector;"))
            conn.commit()
            result = conn.execute(text("SELECT 1;")).scalar()
            return {"status": "connected", "database": "postgresql", "pgvector": "enabled", "test_query": result}
    except Exception as e:
        return {"status": "error", "message": str(e)}
