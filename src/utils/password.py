import os
from passlib.context import CryptContext

SECRET_KEY = os.getenv("SECRET")
ALGORITHM = os.getenv("ALGORITHM")
ACCESS_TOKEN_EXPIRE_MINUTES = 30

pwd_context = CryptContext(schemes=["bcrypt"], deprecated="auto")

def verify_password(plain_password, hashed_password) -> str:
  return pwd_context.verify(plain_password, hashed_password)

def get_password_hash(password) -> str:
  return pwd_context.hash(password)

def validate_password(password: str) -> bool:
  return (
    len(password) >= 8 and
    any(ch.islower() for ch in password) and
    any(ch.isupper() for ch in password) and
    any(ch.isdigit() for ch in password) and
    any(ch in "!\"#$%&'()*+,-./:;<=>?@[\]^_`{|}~" for ch in password)
  )

