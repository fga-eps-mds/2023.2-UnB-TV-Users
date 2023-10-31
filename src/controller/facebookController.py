from dotenv import load_dotenv
import os
from fastapi import FastAPI, APIRouter, HTTPException, Depends
from typing import Any, Dict, Optional
from utils.base import DiscoveryDocument, OpenID
from utils.facebook import create_provider
from starlette.requests import Request
from repository import userRepository
from database import get_db
from sqlalchemy.orm import Session
from repository.userRepository import get_or_create_user

load_dotenv()

os.environ["OAUTHLIB_INSECURE_TRANSPORT"] = "1"

FACEBOOK_CLIENT_ID = os.getenv("FACEBOOK_CLIENT_ID")
FACEBOOK_CLIENT_SECRET = os.getenv("FACEBOOK_CLIENT_SECRET")

app = FastAPI()

facebook = APIRouter(
  prefix=""
)

def convert_facebook(response: dict, session: Optional["httpx.AsyncClient"] = None) -> OpenID:
    """Convert user information returned by Facebook."""
    return OpenID(
        display_name=response.get("name"),
        id=response.get("id"),
        email=response.get("email"),
        picture=response.get("picture", {}).get("data", {}).get("url") if response.get("picture") else None
    )

discovery_document: DiscoveryDocument = {
    "authorization_endpoint": "https://www.facebook.com/v12.0/dialog/oauth",
    "token_endpoint": "https://graph.facebook.com/v12.0/oauth/access_token",
    "userinfo_endpoint": "https://graph.facebook.com/me?fields=id,name,email,picture",
}

GenericSSO = create_provider(name="facebook", discovery_document=discovery_document, response_convertor=convert_facebook)

sso = GenericSSO(
    client_id=FACEBOOK_CLIENT_ID,  # Replace with your App ID
    client_secret=FACEBOOK_CLIENT_SECRET,  # Replace with your App Secret
    redirect_uri="http://localhost:5000/callback",
    allow_insecure_http=True
)

@facebook.get("/facebook")
async def sso_login():
    """Generate login url and redirect."""
    with sso:
        return await sso.get_login_redirect()
    
@facebook.get("/callback")
async def sso_callback(request: Request, db: Session = Depends(get_db)):
    """Process login response from Facebook and return user info."""
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
        raise HTTPException(401, "Failed to fetch user information")
