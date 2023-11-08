from dotenv import load_dotenv
import os
from utils.google import GoogleSSO
from fastapi import Request, FastAPI, APIRouter, Depends
from sqlalchemy.orm import Session
from fastapi.responses import JSONResponse
from database import get_db
from repository.userRepository import get_or_create_user

os.environ["OAUTHLIB_INSECURE_TRANSPORT"] = "1"
CLIENT_ID = os.getenv("CLIENT_ID")
CLIENT_SECRET = os.getenv("CLIENT_SECRET")

app = FastAPI()


sso = GoogleSSO(
    client_id=CLIENT_ID,
    client_secret=CLIENT_SECRET,
    redirect_uri="http://localhost:8000/auth/callback",
    allow_insecure_http=True,
)

google = APIRouter(
  prefix="/auth"
)

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
            user_name = user_data.display_name
            
            user = await get_or_create_user(user_email, user_name, db)
            return {
            "display_name": user.name,
            "email": user.email,
        }
    else:
            return JSONResponse(status_code=400, content={"error": "Authentication failed"})
