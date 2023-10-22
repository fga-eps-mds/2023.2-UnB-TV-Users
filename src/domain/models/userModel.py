from sqlalchemy import Column, String, Integer
from src.database import Base

class userAuth(Base):
    __tablename__ = "users"

    id = Column(Integer, primary_key=True)
    display_name = Column(String(50), nullable=True)
    email = Column(String(50), nullable=False)