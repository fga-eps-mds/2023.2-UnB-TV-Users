import os, sys
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker, declarative_base

if "pytest" in sys.modules:
  engine = create_engine(f"sqlite:///../{os.getenv('TEST_DATABASE_URI', default='unbtv-testing.db')}", connect_args={"check_same_thread": False})  
else:
  SQLALCHEMY_DATABASE_URL = "postgresql://kajfookqkwcfbw:04b047dba3c5c84846aaae6a2bfaa41d455b3c84c08530bd10253f4c806ebffc@ec2-44-215-40-87.compute-1.amazonaws.com:5432/dci6rl2d435oat"
  engine = create_engine(SQLALCHEMY_DATABASE_URL)

SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)

Base = declarative_base()

def get_db():
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()