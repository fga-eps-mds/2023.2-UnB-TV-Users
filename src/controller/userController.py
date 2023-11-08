from fastapi import APIRouter, HTTPException, Response, status, Depends, Header
from database import get_db
from sqlalchemy.orm import Session

from constants import errorMessages
from domain import userSchema
from repository import userRepository
from utils import security, enumeration
from starlette.responses import JSONResponse

from fastapi_filter import FilterDepends
from fastapi.encoders import jsonable_encoder

user = APIRouter(
  prefix="/users"
)

@user.get("/", response_model=list[userSchema.User])
def read_users(
  users_filter: userSchema.UserListFilter = FilterDepends(userSchema.UserListFilter),
  db: Session = Depends(get_db), 
  _: dict = Depends(security.verify_token),
):
  result = userRepository.get_users(db, users_filter)

  users = result['users']
  total = result['total']

  response_content = jsonable_encoder(users)

  return JSONResponse(content=response_content, headers={"X-Total-Count": str(total)})

@user.get("/{user_id}", response_model=userSchema.User)
async def read_user(user_id: int, db: Session = Depends(get_db), token: dict = Depends(security.verify_token)):
  user = userRepository.get_user(db, user_id)
  if not user:
    raise HTTPException(status_code=404, detail=errorMessages.USER_NOT_FOUND)
  return user

@user.get("/email/{user_email}", response_model=userSchema.User)
async def read_user_by_email(user_email: str, db: Session = Depends(get_db), token: dict = Depends(security.verify_token)):
  user = userRepository.get_user_by_email(db, user_email)
  if not user:
    raise HTTPException(status_code=404, detail=errorMessages.USER_NOT_FOUND)
  return user

@user.patch("/{user_id}", response_model=userSchema.User)
async def partial_update_user(user_id: int, data: userSchema.UserUpdate, db: Session = Depends(get_db), token: dict = Depends(security.verify_token)):
  # Validação do valor de connection
  if data.connection and not enumeration.UserConnection.has_value(data.connection):
    raise HTTPException(status_code=400, detail=errorMessages.INVALID_CONNECTION)
    
  db_user = userRepository.get_user(db, user_id)
  if not db_user:
    raise HTTPException(status_code=404, detail=errorMessages.USER_NOT_FOUND)

  if data.email:
    user = userRepository.get_user_by_email(db, data.email)
    if user: 
      raise HTTPException(status_code=404, detail=errorMessages.EMAIL_ALREADY_REGISTERED)

  updated_user = userRepository.update_user(db, db_user, data)
  return updated_user

@user.delete("/{user_id}", response_model=userSchema.User)
async def delete_user(user_id: int, db: Session = Depends(get_db), token: dict = Depends(security.verify_token)):
  db_user = userRepository.get_user(db, user_id)
  if not db_user:
    raise HTTPException(status_code=404, detail=errorMessages.USER_NOT_FOUND)

  userRepository.delete_user(db, db_user)
  return db_user

@user.patch("/role/{user_id}")
def atualiza_role(user_id: int, db: Session = Depends(get_db), token: dict = Depends(security.verify_token)):
  user = userRepository.get_user_by_email(db, email=token['email'])
  if user.role != enumeration.UserRole.ADMIN.value:
    raise HTTPException(status_code=401, detail=errorMessages.NO_PERMISSION)

  # Verificar se o usuario existe
  user = userRepository.get_user(db, user_id)

  if not user:
    raise HTTPException(status_code=404, detail="Esse usuario nao existe")
  
  new_role = enumeration.UserRole.ADMIN.value if user.role == enumeration.UserRole.USER.value else enumeration.UserRole.USER.value
  user = userRepository.update_user_role(db, db_user=user, role=new_role)

  return user