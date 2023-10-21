from pydantic import BaseModel

class UserUpdate(BaseModel):
  name: str | None = None
  email: str | None = None
  connection: str | None = None

class User(BaseModel):
  id: int
  name: str
  connection: str
  email: str
  role: str
  is_active: bool

  class Config:
    from_attributes = True
