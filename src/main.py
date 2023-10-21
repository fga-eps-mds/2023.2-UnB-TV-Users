from typing import Union
from fastapi import FastAPI
from dotenv import load_dotenv

load_dotenv()

from controller import userController
from database import SessionLocal, engine 
from model import userModel

userModel.Base.metadata.create_all(bind=engine)

app = FastAPI()

app.include_router(prefix="/api", router=userController.user)