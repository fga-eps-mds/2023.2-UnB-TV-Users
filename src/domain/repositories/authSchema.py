from pydantic import BaseModel, EmailStr

class UserCreate(BaseModel):
  display_name: str
  email: str