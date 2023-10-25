from sqlalchemy import Boolean, Column, ForeignKey, Integer, String
from sqlalchemy.orm import relationship

from src.database import Base

class User(Base):
  __tablename__ = "users"

  display_name = Column(String, nullable=False)
  email = Column(String, unique=True, index=True, nullable=False, primary_key=True)
