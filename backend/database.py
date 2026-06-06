from pathlib import Path

from sqlalchemy import create_engine
from sqlalchemy.engine import make_url
from sqlalchemy.orm import sessionmaker, declarative_base

from config import DATABASE_URL

# SQLite with WAL mode for better concurrency
connect_args = {"check_same_thread": False} if "sqlite" in DATABASE_URL else {}
engine = create_engine(DATABASE_URL, connect_args=connect_args, echo=False)

SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)

Base = declarative_base()


def get_db():
    """FastAPI dependency that provides a database session per request."""
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()


def init_db():
    """Create all tables. Called by seed.py and main.py startup."""
    Base.metadata.create_all(bind=engine)


def reset_sqlite_db_file():
    """Delete the SQLite database file so a fresh one is created on next init."""
    url = make_url(DATABASE_URL)
    if url.get_backend_name() != "sqlite" or not url.database or url.database == ":memory:":
        return False

    db_path = Path(url.database)
    if not db_path.is_absolute():
        db_path = (Path(__file__).resolve().parent / db_path).resolve()

    engine.dispose()
    if db_path.exists():
        db_path.unlink()
    return True
