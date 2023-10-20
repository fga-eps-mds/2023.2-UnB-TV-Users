from fastapi import APIRouter, HTTPException, Response, status, Depends
from database import get_db
from sqlalchemy.orm import Session

import schema
import repository

user = APIRouter(
  prefix="/users"
)

@user.get("/", response_model=list[schema.User])
def read_users(skip: int = 0, limit: int = 100, db: Session = Depends(get_db)):
  users = repository.get_users(db, skip=skip, limit=limit)
  return users

@user.get("/{user_id}", response_model=schema.User)
def read_user(user_id: int, db: Session = Depends(get_db)):
  user = repository.get_user(db, user_id)
  if not user:
    raise HTTPException(status_code=404, detail="User not found")
  return user


@user.get("/email/{user_email}", response_model=schema.User)
def read_user_by_email(user_email: str, db: Session = Depends(get_db)):
  user = repository.get_user_by_email(db, user_email)
  if not user:
    raise HTTPException(status_code=404, detail="User not found")
  return user

@user.post("/")
def create_user(data: schema.UserCreate, db: Session = Depends(get_db)):
  user = repository.get_user_by_email(db, data.email)
  if user:
    raise HTTPException(status_code=400, detail="Email already registered")
  
  new_user = repository.create_user(db, data)
  return new_user

@user.patch("/{user_id}", response_model=schema.User)
def partial_update_user(user_id: int, data: schema.UserUpdate, db: Session = Depends(get_db)):
  db_user = repository.get_user(db, user_id)
  if not db_user:
    raise HTTPException(status_code=404, detail="User not found")

  updated_user = repository.update_user_basic_data(db, db_user, data)
  return updated_user

@user.delete("/{user_id}", response_model=schema.User)
def delete_user(user_id: int, db: Session = Depends(get_db)):
  db_user = repository.get_user(db, user_id)
  if not db_user:
    raise HTTPException(status_code=404, detail="User not found")

  repository.delete_user(db, db_user)
  return db_user