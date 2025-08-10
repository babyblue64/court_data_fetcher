#! /usr/bin/env python3

from sqlalchemy.orm import declarative_base, sessionmaker

Base = declarative_base()

from sqlalchemy import Column, String, Integer, Text, DateTime
from datetime import datetime, timezone

class Case(Base):
    __tablename__ = 'cases'

    id = Column(Integer, primary_key=True, index=True)
    job_id = Column(String, index=True, unique=True)
    case_type = Column(String)
    case_number = Column(String)
    case_year = Column(String)
    petitioner = Column(Text)
    respondent = Column(Text)
    filing_date = Column(String)
    next_hearing_date = Column(String)
    created_at = Column(DateTime, default=datetime.now(timezone.utc))

from sqlalchemy import create_engine

DATABASE_URL = "postgresql://postgres:password@localhost:5432/postgres"

engine = create_engine(DATABASE_URL)
SessionLocal = sessionmaker(bind=engine, autoflush=False, autocommit=False)

def init_db():
    Base.metadata.create_all(bind=engine)

def get_db():
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()