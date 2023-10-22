import os, sys
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker, declarative_base

def get_uri():
  return os.getenv("TEST_DATABASE_URI") if "pytest" in sys.modules else os.getenv("DATABASE_URI")

engine = create_engine(get_uri())
SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)

Base = declarative_base()

def get_db():
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()