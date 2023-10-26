from dotenv import load_dotenv
import os
from src.utils.google import GoogleSSO
from fastapi import Request, FastAPI, APIRouter

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

@google.get("/login")
async def auth_init():
    """Initialize auth and redirect"""
    with sso:
        return await sso.get_login_redirect(params={"prompt": "consent", "access_type": "offline"})


@google.get("/callback")
async def auth_callback(request: Request):
    """Verify login"""
    with sso:
        user = await sso.verify_and_process(request)
    return user