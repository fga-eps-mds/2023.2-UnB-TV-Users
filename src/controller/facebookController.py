from dotenv import load_dotenv
import os
from fastapi import FastAPI, APIRouter, HTTPException
from typing import Any, Dict, Optional
from src.utils.base import DiscoveryDocument, OpenID
from src.utils.facebook import create_provider
from starlette.requests import Request

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
    client_id="1372492926710085",  # Replace with your App ID
    client_secret="7ce978fbf2ab6977ad94124564fa2bc7",  # Replace with your App Secret
    redirect_uri="http://localhost:5000/callback",
    allow_insecure_http=True
)

@facebook.get("/facebook")
async def sso_login():
    """Generate login url and redirect."""
    with sso:
        return await sso.get_login_redirect()

@facebook.get("/callback")
async def sso_callback(request: Request):
    """Process login response from Facebook and return user info."""
    with sso:
        user = await sso.verify_and_process(request)
    if user is None:
        raise HTTPException(401, "Failed to fetch user information")
    return {
        "id": user.id,
        "picture": user.picture,
        "display_name": user.display_name,
        "email": user.email,
        "provider": user.provider,
    }