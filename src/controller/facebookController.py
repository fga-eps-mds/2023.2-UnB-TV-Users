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
from fastapi.responses import RedirectResponse
from model.userModel import SSOUser
from sqlalchemy.exc import IntegrityError

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
    redirect_uri="http://localhost:8000/callback",
    allow_insecure_http=True
)

@facebook.get("/facebook")
async def sso_login():
    """Generate login url and redirect."""
    with sso:
        return await sso.get_login_redirect()
    
@facebook.get("/callback")
async def sso_callback(request: Request, db: Session = Depends(get_db)):
    try:
        user_data = None
        with sso:
            user_data = await sso.verify_and_process(request)
        
        if user_data:
            user_email = user_data.email
            user_name = user_data.display_name
            
            try:
                user = await get_or_create_user(user_email, user_name, db)
                # Confirme a transação se tudo ocorreu bem
                db.commit()
                return RedirectResponse(url=f"http://localhost:4200/videos")
            except IntegrityError:
                # Reverta a transação em caso de erro de integridade
                db.rollback()
                # Depois de reverter, tente buscar o usuário novamente ou lidar com o erro
                user = db.query(SSOUser).filter(SSOUser.email == user_email).first()
                if user:
                    # Se encontrou o usuário, redirecione
                    return RedirectResponse(url=f"http://localhost:4200/videos")
                else:
                    # Se ainda não encontrou, lance um erro HTTP
                    raise HTTPException(status_code=500, detail="User not found after integrity error.")
        else:
            raise HTTPException(status_code=401, detail="Failed to fetch user information")

    except HTTPException as http_exc:
        # Se outra exceção HTTP foi lançada, apenas retransmita
        raise http_exc
    except Exception as exc:
        # Para outras exceções, reverta a transação e lance uma exceção HTTP genérica
        db.rollback()
        raise HTTPException(status_code=500, detail="An unexpected error occurred.")