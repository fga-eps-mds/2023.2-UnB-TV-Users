from pydantic import BaseModel

class UserLogin(BaseModel):
  email: str
  password: str

class UserCreate(BaseModel):
  name: str
  connection: str
  email: str
  password: str

class UserUpdate(BaseModel):
  name: str | None = None
  email: str | None = None
  connection: str | None = None

class User(BaseModel):
  id: int
  name: str
  connection: str
  email: str

  class Config:
    from_attributes = True
