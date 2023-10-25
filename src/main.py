import uvicorn
from typing import Union
from fastapi import FastAPI
from dotenv import load_dotenv
from utils import dotenv
import sys
from fastapi.middleware.cors import CORSMiddleware

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

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

app.include_router(prefix="/api", router=userController.user)
app.include_router(prefix="/api", router=authController.auth)

@app.get("/")
async def root():
    return { "message": "Olá =)" }

if __name__ == '__main__':
  port = sys.argv[1]
  print(port)
  uvicorn.run('main:app', reload=True, port=int(port), host="0.0.0.0")