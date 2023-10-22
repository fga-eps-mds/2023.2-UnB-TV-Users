import os
from fastapi import FastAPI, Request, HTTPException, Depends
from src.domain.models.google import GoogleSSO
from dotenv import load_dotenv
from src.domain.models.base import DiscoveryDocument, OpenID
from src.domain.models.facebook import create_provider
from typing import Any, Dict
from sqlalchemy.sql import insert
from src.infrastructure.repositories.userRepository import create_user_from_model
from src.database import get_db
from src.application.userSchema import User
from sqlalchemy.orm import Session

load_dotenv()

os.environ["OAUTHLIB_INSECURE_TRANSPORT"] = "1"
CLIENT_ID = os.getenv("CLIENT_ID")
CLIENT_SECRET = os.getenv("CLIENT_SECRET")
FACEBOOK_CLIENT_ID = os.getenv("FACEBOOK_CLIENT_ID")
FACEBOOK_CLIENT_SECRET = os.getenv("FACEBOOK_CLIENT_SECRET")

app = FastAPI()

sso = GoogleSSO(
    client_id=CLIENT_ID,
    client_secret=CLIENT_SECRET,
    redirect_uri="http://localhost:5000/auth/callback",
    allow_insecure_http=True,
)

@app.get("/auth/login")
async def auth_init():
    """Initialize auth and redirect"""
    with sso:
        return await sso.get_login_redirect(params={"prompt": "consent", "access_type": "offline"})


@app.get("/auth/callback")
async def auth_callback(request: Request):
    """Verify login"""
    with sso:
        user = await sso.verify_and_process(request)
        db: Session = Depends(get_db)

        ew_user = create_user_from_model(db, display_name=user.display_name, email=user.email)
    return user

def convert_facebook(response: Dict[str, Any]) -> OpenID:
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

facebook_sso = GenericSSO(
    client_id=FACEBOOK_CLIENT_ID,
    client_secret=FACEBOOK_CLIENT_SECRET,
    redirect_uri="http://localhost:8080/auth/callback/facebook",
    allow_insecure_http=True
)

@app.get("/login/facebook")
async def sso_login():
    """Generate login url and redirect."""
    with sso:
        return await sso.get_login_redirect()

@app.get("/auth/callback/facebook")
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


@app.get("/")
def read_root():
    return {"message": "UnB-TV!"}
