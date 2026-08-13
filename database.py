import os
from pathlib import Path
from sqlalchemy import create_engine, text
from sqlalchemy.orm import sessionmaker, declarative_base
from sqlalchemy.engine.url import make_url

from config import DATABASE_URL

# Ensure uploads directory exists
UPLOAD_DIR = Path("uploads")
UPLOAD_DIR.mkdir(exist_ok=True)


def create_database_if_not_exists():
    """Attempt to create PostgreSQL database if running locally and missing."""
    if not (DATABASE_URL.startswith("postgresql") or DATABASE_URL.startswith("postgres")):
        return

    try:
        url = make_url(DATABASE_URL)
        database_name = url.database
        if not database_name:
            return

        admin_url = url.set(database="postgres")
        admin_engine = create_engine(admin_url, isolation_level="AUTOCOMMIT")

        with admin_engine.connect() as connection:
            result = connection.execute(
                text("SELECT 1 FROM pg_database WHERE datname = :database_name"),
                {"database_name": database_name}
            )
            if not result.scalar():
                connection.execute(text(f'CREATE DATABASE "{database_name}"'))
                print(f"Database '{database_name}' created successfully.")
        admin_engine.dispose()
    except Exception:
        # On managed cloud databases like Render PostgreSQL, database creation via admin connection is skipped
        pass


create_database_if_not_exists()

# Engine creation for PostgreSQL with pool connection liveness ping
engine = create_engine(DATABASE_URL, pool_pre_ping=True)


SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)
Base = declarative_base()


def get_db():
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()