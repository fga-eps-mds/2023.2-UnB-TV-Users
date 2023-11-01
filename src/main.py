from dotenv import load_dotenv
from fastapi.middleware.cors import CORSMiddleware
from controller import userController, authController, googleController, facebookController
from database import SessionLocal, engine 
from model import userModel

import uvicorn
from typing import Union
from fastapi import FastAPI
from dotenv import load_dotenv
from utils import dotenv
from fastapi.middleware.cors import CORSMiddleware

try:
  load_dotenv()
  dotenv.validate_dotenv()
except EnvironmentError as e:
  raise Exception(e)

userModel.Base.metadata.create_all(bind=engine)

app = FastAPI()
  
origins = ["*"]

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Routers
app.include_router(prefix="/api", router=authController.auth)
app.include_router(prefix="/api", router=userController.user)
app.include_router(router=googleController.google)
app.include_router(router=facebookController.facebook)

@app.get("/")
def read_root():
    return {"message": "UnB-TV!"}

if __name__ == '__main__':
  uvicorn.run('main:app', reload=True)

