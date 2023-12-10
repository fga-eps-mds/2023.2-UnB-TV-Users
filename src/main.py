import uvicorn, sys
from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from dotenv import load_dotenv

from utils import dotenv

load_dotenv()
dotenv.validate_dotenv()

from controller import userController, authController
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
    expose_headers=["*"]
)

# Routers
app.include_router(prefix="/api", router=authController.auth)
app.include_router(prefix="/api", router=userController.user)

@app.get("/")
def read_root():
    return {"message": "UnB-TV!"}

if __name__ == '__main__': # pragma: no cover
  port = 8000
  if (len(sys.argv) == 2):
    port = sys.argv[1]

  uvicorn.run('main:app', reload=True, port=int(port), host="0.0.0.0")