from sqlalchemy import create_engine
from sqlalchemy.orm import declarative_base, registry, sessionmaker
from src.core.config import settings
from typing import Generator

Base: registry = declarative_base()

engine = create_engine(settings.DATABASE_URL)
SessionLocal = sessionmaker(bind=engine)

def get_session() -> Generator:
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()