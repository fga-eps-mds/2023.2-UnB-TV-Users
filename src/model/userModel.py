# Referencia: https://fastapi.tiangolo.com/tutorial/sql-databases/#create-the-database-models

from sqlalchemy import Boolean, Column, ForeignKey, Integer, String
from sqlalchemy.orm import relationship
from sqlalchemy.ext.declarative import declarative_base

Base = declarative_base()

from database import Base

class User(Base):
  __tablename__ = "users"
  __table_args__ = {'extend_existing': True}

  id = Column(Integer, primary_key=True, index=True)
  name = Column(String, nullable=False)
  connection = Column(String, nullable=False)
  role = Column(String, default="USER")
  email = Column(String, unique=True, index=True, nullable=False)
  password = Column(String, nullable=False)
  is_active = Column(Boolean, default=False)
  activation_code = Column(Integer, nullable=True)
  password_reset_code = Column(Integer, nullable=True)

  social_user = relationship("SocialUser", uselist=False, back_populates="user")

class SocialUser(User):
    __tablename__ = "social_users"
    
    social_id = Column(Integer, primary_key=True, index=True)
    social_name = Column(String, nullable=False)
    social_email = Column(String, unique=True, index=True, nullable=False)  
    social_provider = Column(String, nullable=True) 
    user_id = Column(Integer, ForeignKey('users.id'))

    user = relationship("User", back_populates="social_user")

  
