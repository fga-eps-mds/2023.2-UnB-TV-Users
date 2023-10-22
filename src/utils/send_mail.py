import os
from fastapi import BackgroundTasks
from fastapi_mail import FastMail, MessageSchema, ConnectionConfig, MessageType
from dotenv import load_dotenv
from pydantic import BaseModel, EmailStr
from starlette.responses import JSONResponse
from typing import List
from domain import authSchema

class EmailSchema(BaseModel):
  email: List[EmailStr]

conf = ConnectionConfig(
    MAIL_USERNAME = os.getenv("MAIL_USERNAME"),
    MAIL_PASSWORD = os.getenv("MAIL_PASSWORD"),
    MAIL_FROM = os.getenv("MAIL_FROM"),
    MAIL_PORT = os.getenv("MAIL_PORT"),
    MAIL_SERVER = os.getenv("MAIL_SERVER"),
    MAIL_FROM_NAME="UNB TV",
    MAIL_STARTTLS = True,
    MAIL_SSL_TLS = False,
    USE_CREDENTIALS = True,
    VALIDATE_CERTS = True
)

async def send_verification_code(email: str, code: int) -> JSONResponse:
  html = f"<p>Seja bem vindo ao UnB-TV! Para confirmar a criação da sua conta utilize o código <strong>{code}</strong></p>"

  message = MessageSchema(
    subject="Confirme a criação da sua conta",
    recipients=[email],
    body=html,
    subtype=MessageType.html
  )

  fm = FastMail(conf)
  
  try:
    await fm.send_message(message)
    return JSONResponse(status_code=200, content={ "status": "success" })
  except:
    return JSONResponse(status_code=400, content={ "status": "error" })

async def send_reset_password_code(email: str, code: int) -> JSONResponse:
  html = f"""
    <p>Foi feita uma solicitação de troca de senha. Caso você tenha feito essa solicitação, utilize o código <strong>{code}</strong para trocar a sua senha.</p>
    <p>Caso você não tenha feito essa solicitação, por favor ignore este email</p>
  """

  message = MessageSchema(
    subject="Confirme a troca da sua senha",
    recipients=[email],
    body=html,
    subtype=MessageType.html
  )

  fm = FastMail(conf)
  
  try:
    await fm.send_message(message)
    return JSONResponse(status_code=200, content={ "status": "success" })
  except:
    return JSONResponse(status_code=400, content={ "status": "error" })