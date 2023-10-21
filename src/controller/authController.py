import os
from fastapi import APIRouter, HTTPException, Response, status, Depends
from utils import security, enumeration, send_mail
from database import get_db
from sqlalchemy.orm import Session
from datetime import datetime, timedelta
from constants import errorMessages
from random import randint
from starlette.responses import JSONResponse

from domain import userSchema, authSchema
from repository import userRepository

auth = APIRouter(
  prefix="/auth"
)

@auth.post('/register')
async def register(data: authSchema.UserCreate, db: Session = Depends(get_db)):
  # Verifica se connection é valido
  if (not enumeration.UserConnection.has_value(data.connection)):
    raise HTTPException(status_code=400, detail=errorMessages.INVALID_CONNECTION)

  # Validação de senha
  is_valid = security.validate_password(data.password.strip()) 
  if (not is_valid):
    raise HTTPException(status_code=400, detail=errorMessages.INVALID_PASSWORD)

  # Verifica se já existe um usuário com o email informado
  user = userRepository.get_user_by_email(db, data.email)
  if user:
    raise HTTPException(status_code=400, detail=errorMessages.EMAIL_ALREADY_REGISTERED)
  
  hashed_password = security.get_password_hash(data.password)
  
  activation_code = randint(100000, 999999)

  new_user = userRepository.create_user(db, name=data.name, connection=data.connection, email=data.email, password=hashed_password, activation_code=activation_code)
  
  res = await send_mail.send_verification_code(email=data.email, code=activation_code)

  return JSONResponse(status_code=201, content={ "status": "success" })

@auth.post("/login", response_model=authSchema.Token)
def login(data: authSchema.UserLogin, db: Session = Depends(get_db)):
  user = userRepository.get_user_by_email(db, data.email)
  if not user:
    raise HTTPException(status_code=404, detail=errorMessages.USER_NOT_FOUND)
  
  password_match = security.verify_password(data.password, user.password)
  if not password_match:
    raise HTTPException(status_code=404, detail=errorMessages.PASSWORD_NO_MATCH)

  if not user.is_active:
    raise HTTPException(status_code=401, detail=errorMessages.ACCOUNT_IS_NOT_ACTIVE)
  
  access_token = security.create_access_token(data={"sub": user.email})

  return JSONResponse(status_code=201, content={ "access_token": access_token, "token_type": "bearer" })

@auth.post('/resend-code')
async def send_new_code(data: authSchema.SendNewCode, db: Session = Depends(get_db)):
  user = userRepository.get_user_by_email(db, data.email)
  if not user:
    raise HTTPException(status_code=404, detail=errorMessages.USER_NOT_FOUND)

  if user.is_active:
    return JSONResponse(status_code=400, content={ "status": "error", "message": errorMessages.ACCOUNT_ALREADY_ACTIVE })

  res = await send_mail.send_verification_code(email=data.email, code=user.activation_code)
  if res.status_code != 200:
    return JSONResponse(status_code=400, content={ "status": "error", "message": errorMessages.ERROR_SENDING_EMAIL })

  return JSONResponse(status_code=201, content={ "status": "success" })

@auth.patch('/activate-account')
async def validate_account(data: authSchema.AccountValidation, db: Session = Depends(get_db)):
  user = userRepository.get_user_by_email(db, data.email)
  if not user:
    raise HTTPException(status_code=404, detail=errorMessages.USER_NOT_FOUND)

  if user.is_active:
    return JSONResponse(status_code=200, content={ "status": "error", "message": errorMessages.ACCOUNT_ALREADY_ACTIVE })
  
  if user.activation_code != data.code:
    raise HTTPException(status_code=404, detail=errorMessages.INVALID_CODE)

  userRepository.activate_account(db, user)
  return JSONResponse(status_code=200, content={ "status": "success" })