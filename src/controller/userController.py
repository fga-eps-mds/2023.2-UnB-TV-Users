from fastapi import APIRouter, HTTPException, Response, status, Depends
from database import get_db
from sqlalchemy.orm import Session

from constants import errorMessages
from domain import userSchema
from repository import userRepository
from utils import security, enumeration

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
    raise HTTPException(status_code=404, detail=errorMessages.USER_NOT_FOUND)
  return user

@user.get("/email/{user_email}", response_model=userSchema.User)
def read_user_by_email(user_email: str, db: Session = Depends(get_db), token: dict = Depends(security.verify_token)):
  user = userRepository.get_user_by_email(db, user_email)
  if not user:
    raise HTTPException(status_code=404, detail=errorMessages.USER_NOT_FOUND)
  return user

@user.patch("/{user_id}", response_model=userSchema.User)
def partial_update_user(user_id: int, data: userSchema.UserUpdate, db: Session = Depends(get_db), token: dict = Depends(security.verify_token)):
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
def delete_user(user_id: int, db: Session = Depends(get_db), token: dict = Depends(security.verify_token)):
  db_user = userRepository.get_user(db, user_id)
  if not db_user:
    raise HTTPException(status_code=404, detail=errorMessages.USER_NOT_FOUND)

  userRepository.delete_user(db, db_user)
  return db_user

# db: sempre que tiver que alterar o banco
@user.patch("/role/{user_id}")
def atualiza_role(user_id: int, data: userSchema.UserUpdateRole, db: Session = Depends(get_db), token: dict = Depends(security.verify_token)):
  # Verificar se a role é valida
  # https://developer.mozilla.org/en-US/docs/Web/HTTP/Status
  if not(enumeration.UserRole.has_value(data.role)):
    # 400: bad request: envia dados errados, invalidos
    # 404: not found: não encontrou
    # 401: not authorized
    raise HTTPException(status_code=400, detail="O individuo enviou uma role invalida")
  
  user = userRepository.get_user_by_email(db, email=token['email'])
  if user.role != enumeration.UserRole.ADMIN.value:
    raise HTTPException(status_code=401, detail=errorMessages.NO_PERMISSION)

  # Verificar se o usuario existe
  user = userRepository.get_user(db, user_id)
  # user == None
  if not user:
    raise HTTPException(status_code=404, detail="Esse usuario nao existe")
  
  user = userRepository.update_user_role(db, db_user=user, role=data.role)
  return user