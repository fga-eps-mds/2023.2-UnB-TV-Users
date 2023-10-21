import os
from fastapi import APIRouter, HTTPException, Response, status, Depends
from utils import security
from database import get_db
from sqlalchemy.orm import Session
from datetime import datetime, timedelta

from domain import userSchema, authSchema
from repository import userRepository

auth = APIRouter(
  prefix="/auth"
)

@auth.post('/register')
def register(data: userSchema.UserCreate, db: Session = Depends(get_db)):
  is_valid = security.validate_password(data.password.strip()) 
  if (not is_valid):
    raise HTTPException(status_code=400, detail="Invalid password")

  user = userRepository.get_user_by_email(db, data.email)
  if user:
    raise HTTPException(status_code=400, detail="Email already registered")
  
  hashed_password = security.get_password_hash(data.password)

  new_user = userRepository.create_user(db, data.email, hashed_password)
  return new_user

@auth.post("/login", response_model=authSchema.Token)
def login(data: userSchema.UserLogin, db: Session = Depends(get_db)):
  user = userRepository.get_user_by_email(db, data.email)
  if not user:
    raise HTTPException(status_code=404, detail="User not found")
  
  password_match = security.verify_password(data.password, user.password)
  if not password_match:
    raise HTTPException(status_code=404, detail="Invalid password")
  
  access_token = security.create_access_token(data={"sub": user.email})

  return { "access_token": access_token, "token_type": "bearer" }