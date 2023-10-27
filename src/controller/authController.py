import os
from fastapi import APIRouter, HTTPException, Response, status, Depends
from src.database import get_db
from src.domain.repositories import userSchema, authSchema
from src.repository import userRepository
from src.utils import security
from src.constants import errorMessages
from utils import security, enumeration, send_mail
from database import get_db
from sqlalchemy.orm import Session
from datetime import datetime, timedelta
from constants import errorMessages
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
  
  activation_code = security.generate_six_digit_number_code()

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
  
  access_token = security.create_access_token(data={"id": user.id, "email": user.email})

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

@auth.post('/reset-password/request')
async def request_password_(data: authSchema.ResetPasswordRequest, db: Session = Depends(get_db)):
  user = userRepository.get_user_by_email(db, data.email)
  if not user:
    raise HTTPException(status_code=404, detail=errorMessages.USER_NOT_FOUND)

  if not user.is_active:
    raise HTTPException(status_code=404, detail=errorMessages.ACCOUNT_IS_NOT_ACTIVE)
  
  code = security.generate_six_digit_number_code()

  try:
    userRepository.set_user_reset_pass_code(db, user, code)
    await send_mail.send_reset_password_code(data.email, code)

    return JSONResponse(status_code=200, content={ "status": "success" })
  except:
    return JSONResponse(status_code=400, content={ "status": "error" })

@auth.post('/reset-password/verify')
def verify_reset_code(data: authSchema.ResetPasswordVerify, db: Session = Depends(get_db)):
  user = userRepository.get_user_by_email(db, data.email)
  if not user:
    raise HTTPException(status_code=404, detail=errorMessages.USER_NOT_FOUND)
  
  if not user.password_reset_code:
    raise HTTPException(status_code=404, detail=errorMessages.NO_RESET_PASSWORD_CODE)

  if user.password_reset_code != data.code:
    raise HTTPException(status_code=400, detail=errorMessages.INVALID_RESET_PASSWORD_CODE)

  return JSONResponse(status_code=200, content={ "status": "success" })

@auth.patch('/reset-password/change', response_model=userSchema.User)
def update_user_password(data: authSchema.ResetPasswordUpdate, db: Session = Depends(get_db)):
  user = userRepository.get_user_by_email(db, data.email)
  if not user:
    raise HTTPException(status_code=404, detail=errorMessages.USER_NOT_FOUND)
  
  if data.password and not security.validate_password(data.password):
    raise HTTPException(status_code=400, detail=errorMessages.INVALID_PASSWORD)

  if not user.password_reset_code:
    raise HTTPException(status_code=401, detail=errorMessages.INVALID_REQUEST)
    
  if data.code != user.password_reset_code:
    raise HTTPException(status_code=400, detail=errorMessages.INVALID_RESET_PASSWORD_CODE)
    
  hashed_password = security.get_password_hash(data.password)
  updated_user = userRepository.update_password(db, user, hashed_password)

  return updated_user
