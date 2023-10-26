from dotenv import load_dotenv
import os
from src.utils.google import GoogleSSO
from fastapi import Request, FastAPI, APIRouter, Depends
from src.repository import userRepository
from sqlalchemy.orm import Session
from fastapi.responses import JSONResponse
from src.database import get_db

load_dotenv()


os.environ["OAUTHLIB_INSECURE_TRANSPORT"] = "1"
CLIENT_ID = os.getenv("CLIENT_ID")
CLIENT_SECRET = os.getenv("CLIENT_SECRET")

app = FastAPI()


sso = GoogleSSO(
    client_id=CLIENT_ID,
    client_secret=CLIENT_SECRET,
    redirect_uri="http://localhost:5000/auth/callback",
    allow_insecure_http=True,
)

google = APIRouter(
  prefix="/auth"
)

async def get_or_create_user(email: str, display_name: str, db: Session):

    user = userRepository.get_user_by_email(db, email)
    
    if user is None:
        user = userRepository.create_user(db, display_name=display_name, email=email)
    
    return user

@google.get("/login")
async def auth_init():
    """Initialize auth and redirect"""
    with sso:
        return await sso.get_login_redirect(params={"prompt": "consent", "access_type": "offline"})


@google.get("/callback")
async def auth_callback(request: Request, db: Session = Depends(get_db)):
    """Verify login"""
    user_data = None
    with sso:
        user_data = await sso.verify_and_process(request)
    
    if user_data:
            user_email = user_data.email
            user_display_name = user_data.display_name
            
            user = await get_or_create_user(user_email, user_display_name, db)
            return user
    else:
            return JSONResponse(status_code=400, content={"error": "Authentication failed"})
