import os
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker, Session
from .models import Base

_engine = None
_SessionLocal = None


def init_db(db_path: str = "data/work-reportor.db"):
    global _engine, _SessionLocal
    os.makedirs(os.path.dirname(db_path), exist_ok=True)
    _engine = create_engine(f"sqlite:///{db_path}", echo=False)
    Base.metadata.create_all(_engine)
    _SessionLocal = sessionmaker(bind=_engine)


def get_session() -> Session:
    if _SessionLocal is None:
        raise RuntimeError("Database not initialized. Call init_db() first.")
    return _SessionLocal()


def get_db():
    session = get_session()
    try:
        yield session
    finally:
        session.close()
