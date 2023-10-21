import uvicorn
from typing import Union
from fastapi import FastAPI
from dotenv import load_dotenv
from utils import dotenv

try:
  load_dotenv()
  dotenv.validate_dotenv()
except EnvironmentError as e:
  raise Exception(e)

from controller import userController, authController
from database import SessionLocal, engine 
from model import userModel

userModel.Base.metadata.create_all(bind=engine)

app = FastAPI()

app.include_router(prefix="/api", router=userController.user)
app.include_router(prefix="/api", router=authController.auth)

if __name__ == '__main__':
  uvicorn.run('main:app', reload=True)