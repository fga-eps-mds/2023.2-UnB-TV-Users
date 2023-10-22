from sqlalchemy.orm import Session

from src.domain.models.userModel import userAuth
from src.application.userSchema import User

def create_user_from_model(db: Session, display_name, email):
    db_user = userAuth(display_name=display_name, email=email)
    db.add(db_user)
    db.commit()
    db.refresh(db_user)
    return db_user