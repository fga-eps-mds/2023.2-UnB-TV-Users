import os
from fastapi import FastAPI, Request, HTTPException, Depends
from src.utils.google import GoogleSSO
from dotenv import load_dotenv
from src.utils.base import DiscoveryDocument, OpenID
from src.utils.facebook import create_provider
from typing import Any, Dict
from fastapi.middleware.cors import CORSMiddleware

from src.controller import userController, authController
from src.model import userModel
from src.database import engine

load_dotenv()

os.environ["OAUTHLIB_INSECURE_TRANSPORT"] = "1"
CLIENT_ID = os.getenv("CLIENT_ID")
CLIENT_SECRET = os.getenv("CLIENT_SECRET")
FACEBOOK_CLIENT_ID = os.getenv("FACEBOOK_CLIENT_ID")
FACEBOOK_CLIENT_SECRET = os.getenv("FACEBOOK_CLIENT_SECRET")

app = FastAPI()

userModel.Base.metadata.create_all(bind=engine)

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

@app.get("/")
def read_root():
    return {"message": "UnB-TV!"}
