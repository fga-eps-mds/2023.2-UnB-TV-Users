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

def create_user(db: Session, name, connection, email, password, activation_code):
  db_user = userModel.User(name=name, connection=connection, email=email, password=password, activation_code=activation_code)
  db.add(db_user)
  db.commit()
  db.refresh(db_user)
  return db_user

def update_user(db: Session, db_user: userSchema.User, user: userSchema.UserUpdate):
  user_data = user.dict(exclude_unset=True)
  for key, value in user_data.items():
    setattr(db_user, key, value)

  db.add(db_user)
  db.commit()
  db.refresh(db_user)
  return db_user

def update_user_role(db: Session, db_user: userSchema.User, role: str):
  db_user.role = role

  db.add(db_user)
  db.commit()
  db.refresh(db_user)
  return db_user

def update_password(db: Session, db_user: userSchema.User, new_password: str):
  db_user.password = new_password
  db_user.password_reset_code = None

  db.add(db_user)
  db.commit()
  db.refresh(db_user)
  return db_user

def activate_account(db: Session, db_user: userSchema.User):
  db_user.is_active = True
  db_user.activation_code = None
  db.add(db_user)
  db.commit()
  db.refresh(db_user)
  return db_user

def set_user_reset_pass_code(db: Session, db_user: userSchema.User, code: int):
  db_user.password_reset_code = code
  db.add(db_user)
  db.commit()
  db.refresh(db_user)
  return db_user

def delete_user(db: Session, db_user: userSchema.User):
  db.delete(db_user)
  db.commit()