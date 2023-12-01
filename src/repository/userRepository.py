from repository import userRepository

# Referencia: https://fastapi.tiangolo.com/tutorial/sql-databases/#crud-utils
from sqlalchemy import or_
from sqlalchemy.orm import Session

from domain import userSchema
from model import userModel

def get_user(db: Session, user_id: int):
  return db.query(userModel.User).filter(userModel.User.id == user_id).first()

def get_user_by_email(db: Session, email: str):
  return db.query(userModel.User).filter(userModel.User.email == email).first()

def get_user_by_email_social(db: Session, email: str):
  return db.query(userModel.SocialUser).filter(userModel.SocialUser.email == email).first()

def get_users(db: Session, users_filter: userSchema.UserListFilter):
  query = db.query(userModel.User)

  if (users_filter.name):
    query = query.filter(userModel.User.name == users_filter.name)
  elif (users_filter.email):
    query = query.filter(userModel.User.email == users_filter.email)
  elif (users_filter.name_or_email):
    query = query.filter(or_(userModel.User.name.ilike(f'%{users_filter.name_or_email}%'), userModel.User.email.ilike(f'%{users_filter.name_or_email}%')))

  if (users_filter.connection):
    query = query.filter(userModel.User.connection == users_filter.connection)

  total_count = query.count()
  query = query.order_by(userModel.User.name.asc())

  if (users_filter.offset):
    query = query.offset(users_filter.offset)

  if (users_filter.limit):
    query = query.limit(users_filter.limit)

  return { "users": query.all(), "total": total_count }

def create_user(db: Session, name, connection, email, password, activation_code):
  db_user = userModel.User(name=name, connection=connection, email=email, password=password, activation_code=activation_code,)
  db.add(db_user)
  db.commit()
  db.refresh(db_user)
  return db_user

def create_user_social(db: Session, name, email):
  db_user = userModel.SocialUser(
  name=name,
  email=email,)

  db.add(db_user)
  db.commit()
  db.refresh(db_user)
  return db_user

async def get_or_create_user(email: str, name: str, db: Session):

    user = userRepository.get_user_by_email(db, email)
    
    if user is None:
        user = userRepository.create_by_login(db, name=name, email=email)
    
    return user

def create_by_login(db: Session, name, email):

    db_user = userModel.User(
        name=name,
        email=email
    )
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
