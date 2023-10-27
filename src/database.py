import os, sys
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker, declarative_base

DATABASE_URL = "postgresql://postgres:password@db:5432/unb_db"

engine = create_engine(DATABASE_URL)
if "pytest" in sys.modules:
  engine = create_engine(f"sqlite:///../{os.getenv('TEST_DATABASE_URI', default='unbtv-testing.db')}", connect_args={"check_same_thread": False})  
else:
  engine = create_engine(f"sqlite:///../{os.getenv('DATABASE_URI', default='unbtv.db')}", connect_args={"check_same_thread": False})

SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)

Base = declarative_base()

def get_db():
    db = SessionLocal()
    try:
        yield db  # Aqui está a correção. Você deve ceder a sessão.
    except Exception as e:
        raise e
    finally:
        db.close()
