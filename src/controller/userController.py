from src.constants import errorMessages
from src.repository import userRepository
from fastapi import APIRouter, HTTPException, Response, status, Depends
from src.domain.repositories import userSchema, authSchema
from sqlalchemy.orm import Session
from src.database import get_db
from src.utils import security


user = APIRouter(
  prefix="/users"
)

@user.get("/email/{user_email}", response_model=userSchema.User)
def read_user_by_email(user_email: str, db: Session = Depends(get_db)):
  user = userRepository.get_user_by_email(db, user_email)
  if not user:
    raise HTTPException(status_code=404, detail=errorMessages.USER_NOT_FOUND)
  return user