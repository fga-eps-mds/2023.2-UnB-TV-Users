# Referencia: https://fastapi.tiangolo.com/tutorial/sql-databases/#crud-utils
from sqlalchemy.orm import Session

from domain import userSchema
from model import userModel

def get_user(db: Session, user_id: int):
  return db.query(userModel.User).filter(userModel.User.id == user_id).first()

def get_user_by_email(db: Session, email: str):
  return db.query(userModel.User).filter(userModel.User.email == email).first()

def get_users(db: Session, skip: int = 0, limit: int = 100):
  return db.query(userModel.User).offset(skip).limit(limit).all()

def create_user(db: Session, name, connection, email, hashed_password):
  db_user = userModel.User(name=name, connection=connection, email=email, password=hashed_password)
  db.add(db_user)
  db.commit()
  db.refresh(db_user)
  return db_user

def update_user_basic_data(db: Session, db_user: userSchema.User, user: userSchema.UserUpdate):
  user_data = user.dict(exclude_unset=True)
  for key, value in user_data.items():
    setattr(db_user, key, value)

  db.add(db_user)
  db.commit()
  db.refresh(db_user)
  return db_user

def delete_user(db: Session, db_user: userSchema.User):
  db.delete(db_user)
  db.commit()