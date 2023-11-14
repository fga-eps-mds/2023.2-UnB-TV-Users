import uvicorn
from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from dotenv import load_dotenv
import os

from utils import dotenv

load_dotenv()
dotenv.validate_dotenv()

from controller import userController, authController, googleController, facebookController
from database import engine 
from model import userModel

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
    port = int(os.environ.get('PORT', 8000))
    uvicorn.run('main:app', reload=True, port=port, host="0.0.0.0")

