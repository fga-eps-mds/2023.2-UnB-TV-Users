import os
from fastapi import FastAPI, Request, HTTPException, Depends
from dotenv import load_dotenv
from src.utils.base import DiscoveryDocument, OpenID
from src.utils.facebook import create_provider
from typing import Any, Dict
from fastapi.middleware.cors import CORSMiddleware
import uvicorn

from src.controller import userController, authController, googleController, facebookController
from src.model import userModel
from src.database import engine

load_dotenv()


app = FastAPI()

userModel.Base.metadata.create_all(bind=engine)

origins = ["*"]

app.add_middleware(
    CORSMiddleware,
    allow_origins=origins,
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

