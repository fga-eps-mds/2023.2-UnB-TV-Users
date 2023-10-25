import os
from fastapi import APIRouter, HTTPException, Response, status, Depends
from src.database import get_db
from sqlalchemy.orm import Session
from src.domain.repositories import userSchema, authSchema
from src.repository import userRepository
from src.utils import security
from src.constants import errorMessages
from starlette.responses import JSONResponse

auth = APIRouter(
  prefix="/auth"
)

@auth.post('/register')
async def register(data: authSchema.UserCreate, db: Session = Depends(get_db)):

  new_user = userRepository.create_user(db, display_name=data.display_name, email=data.email)

  return JSONResponse(status_code=201, content={ "status": "success" })

