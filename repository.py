# Referencia: https://fastapi.tiangolo.com/tutorial/sql-databases/#crud-utils
from sqlalchemy.orm import Session

import model
import schema

def get_user(db: Session, user_id: int):
  return db.query(model.User).filter(model.User.id == user_id).first()

def get_user_by_email(db: Session, email: str):
  return db.query(model.User).filter(model.User.email == email).first()

def get_users(db: Session, skip: int = 0, limit: int = 100):
  return db.query(model.User).offset(skip).limit(limit).all()

def create_user(db: Session, user: schema.UserCreate):
  db_user = model.User(email=user.email, hashed_password=user.password)
  db.add(db_user)
  db.commit()
  db.refresh(db_user)
  return db_user

def update_user_basic_data(db: Session, db_user: schema.User, user: schema.UserUpdate):
  user_data = user.dict(exclude_unset=True)
  for key, value in user_data.items():
    setattr(db_user, key, value)

  db.add(db_user)
  db.commit()
  db.refresh(db_user)
  return db_user

def delete_user(db: Session, db_user: schema.User):
  db.delete(db_user)
  db.commit()