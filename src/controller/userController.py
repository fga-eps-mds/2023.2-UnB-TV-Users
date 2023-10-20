from fastapi import APIRouter, HTTPException, Response, status, Depends
from database import get_db
from sqlalchemy.orm import Session

from domain import userSchema
from repository import userRepository

user = APIRouter(
  prefix="/users"
)

@user.get("/", response_model=list[userSchema.User])
def read_users(skip: int = 0, limit: int = 100, db: Session = Depends(get_db)):
  users = userRepository.get_users(db, skip=skip, limit=limit)
  return users

@user.get("/{user_id}", response_model=userSchema.User)
def read_user(user_id: int, db: Session = Depends(get_db)):
  user = userRepository.get_user(db, user_id)
  if not user:
    raise HTTPException(status_code=404, detail="User not found")
  return user


@user.get("/email/{user_email}", response_model=userSchema.User)
def read_user_by_email(user_email: str, db: Session = Depends(get_db)):
  user = userRepository.get_user_by_email(db, user_email)
  if not user:
    raise HTTPException(status_code=404, detail="User not found")
  return user

@user.post("/")
def create_user(data: userSchema.UserCreate, db: Session = Depends(get_db)):
  user = userRepository.get_user_by_email(db, data.email)
  if user:
    raise HTTPException(status_code=400, detail="Email already registered")
  
  new_user = userRepository.create_user(db, data)
  return new_user

@user.patch("/{user_id}", response_model=userSchema.User)
def partial_update_user(user_id: int, data: userSchema.UserUpdate, db: Session = Depends(get_db)):
  db_user = userRepository.get_user(db, user_id)
  if not db_user:
    raise HTTPException(status_code=404, detail="User not found")

  updated_user = userRepository.update_user_basic_data(db, db_user, data)
  return updated_user

@user.delete("/{user_id}", response_model=userSchema.User)
def delete_user(user_id: int, db: Session = Depends(get_db)):
  db_user = userRepository.get_user(db, user_id)
  if not db_user:
    raise HTTPException(status_code=404, detail="User not found")

  userRepository.delete_user(db, db_user)
  return db_user