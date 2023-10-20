from typing import Union
from fastapi import FastAPI

from controller import user
from database import SessionLocal, engine 
import model

model.Base.metadata.create_all(bind=engine)

app = FastAPI()

app.include_router(prefix="/api", router=user)