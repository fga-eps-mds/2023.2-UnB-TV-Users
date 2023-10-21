import os
from fastapi import APIRouter, HTTPException, Response, status, Depends
from utils import password
from database import get_db
from sqlalchemy.orm import Session

from domain import userSchema
from repository import userRepository

auth = APIRouter(
  prefix="/auth"
)

@auth.post('/register')
def register(data: userSchema.UserCreate, db: Session = Depends(get_db)):
  is_valid = password.validate_password(data.password.strip()) 
  if (not is_valid):
    raise HTTPException(status_code=400, detail="Invalid password")

  user = userRepository.get_user_by_email(db, data.email)
  if user:
    raise HTTPException(status_code=400, detail="Email already registered")
  
  hashed_password = password.get_password_hash(data.password)

  new_user = userRepository.create_user(db, data.email, hashed_password)
  return new_user