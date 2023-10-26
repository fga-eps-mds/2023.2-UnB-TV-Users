from sqlalchemy.orm import Session

from src.model import userModel
from src.repository import userRepository

def create_user(db: Session, email, display_name):
  db_user = userModel.User(display_name=display_name, email=email)
  db.add(db_user)
  db.commit()
  db.refresh(db_user)
  return db_user

def get_user_by_email(db: Session, email: str):
  return db.query(userModel.User).filter(userModel.User.email == email).first()

async def get_or_create_user(email: str, display_name: str, db: Session):

    user = userRepository.get_user_by_email(db, email)
    
    if user is None:
        user = userRepository.create_user(db, display_name=display_name, email=email)
    
    return user