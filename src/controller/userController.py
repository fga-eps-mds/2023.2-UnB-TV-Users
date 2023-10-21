from fastapi import APIRouter, HTTPException, Response, status, Depends
from database import get_db
from sqlalchemy.orm import Session

from constants import errors
from domain import userSchema
from repository import userRepository
from utils import security

user = APIRouter(
  prefix="/users"
)

@user.get("/", response_model=list[userSchema.User])
def read_users(skip: int = 0, limit: int = 100, db: Session = Depends(get_db), token: dict = Depends(security.verify_token)):
  users = userRepository.get_users(db, skip=skip, limit=limit)
  return users

@user.get("/{user_id}", response_model=userSchema.User)
def read_user(user_id: int, db: Session = Depends(get_db), token: dict = Depends(security.verify_token)):
  user = userRepository.get_user(db, user_id)
  if not user:
    raise HTTPException(status_code=404, detail=errors.USER_NOT_FOUND)
  return user


@user.get("/email/{user_email}", response_model=userSchema.User)
def read_user_by_email(user_email: str, db: Session = Depends(get_db), token: dict = Depends(security.verify_token)):
  user = userRepository.get_user_by_email(db, user_email)
  if not user:
    raise HTTPException(status_code=404, detail=errors.USER_NOT_FOUND)
  return user

@user.patch("/{user_id}", response_model=userSchema.User)
def partial_update_user(user_id: int, data: userSchema.UserUpdate, db: Session = Depends(get_db), token: dict = Depends(security.verify_token)):
  db_user = userRepository.get_user(db, user_id)
  if not db_user:
    raise HTTPException(status_code=404, detail=errors.USER_NOT_FOUND)

  updated_user = userRepository.update_user_basic_data(db, db_user, data)
  return updated_user

@user.delete("/{user_id}", response_model=userSchema.User)
def delete_user(user_id: int, db: Session = Depends(get_db), token: dict = Depends(security.verify_token)):
  db_user = userRepository.get_user(db, user_id)
  if not db_user:
    raise HTTPException(status_code=404, detail=errors.USER_NOT_FOUND)

  userRepository.delete_user(db, db_user)
  return db_user