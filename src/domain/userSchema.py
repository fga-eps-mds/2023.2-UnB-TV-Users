from pydantic import BaseModel

class UserLogin(BaseModel):
  email: str
  password: str

class UserCreate(BaseModel):
  email: str
  password: str

class UserUpdate(BaseModel):
  email: str

class User(BaseModel):
  id: int
  email: str
  is_active: bool

  class Config:
    from_attributes = True
