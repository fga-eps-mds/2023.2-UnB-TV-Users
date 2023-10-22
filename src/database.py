import os, sys
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker, declarative_base

if "pytest" in sys.modules:
  
  engine = create_engine(os.getenv("TEST_DATABASE_URI"))
else:
  engine = create_engine(f"sqlite:///./{os.getenv('DATABASE_URI', default='users.db')}", connect_args={"check_same_thread": False})

SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)

Base = declarative_base()

def get_db():
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()