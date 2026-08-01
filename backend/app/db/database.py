import os
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker

DATABASE_URL = os.getenv(
    "DATABASE_URL",
    "postgresql+psycopg://jeeva:jeevapassword@127.0.0.1:5432/stock_analyst"
)

# Convert postgresql:// to postgresql+psycopg:// if needed
if DATABASE_URL and DATABASE_URL.startswith("postgresql://") and not DATABASE_URL.startswith("postgresql+psycopg://"):
    DATABASE_URL = DATABASE_URL.replace("postgresql://", "postgresql+psycopg://", 1)

# Handle container vs host OS resolution
if "@db:5432" in DATABASE_URL and not os.path.exists("/.dockerenv"):
    DATABASE_URL = DATABASE_URL.replace("@db:5432", "@127.0.0.1:5432")

if "@localhost:5432" in DATABASE_URL:
    DATABASE_URL = DATABASE_URL.replace("@localhost:5432", "@127.0.0.1:5432")

engine = create_engine(
    DATABASE_URL,
    pool_pre_ping=True,
    pool_size=10,
    max_overflow=20,
)

SessionLocal = sessionmaker(
    autoflush=False,
    autocommit=False,
    bind=engine,
)
