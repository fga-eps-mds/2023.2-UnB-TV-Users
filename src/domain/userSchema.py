from pydantic import BaseModel, ConfigDict
from typing import Union

class UserUpdate(BaseModel):
  name: str | None = None
  email: str | None = None
  connection: str | None = None

'''
class UserUpdate(BaseModel):
  display_name: Union[str, None] = None
  email: Union[str, None] = None
'''

class User(BaseModel):
  model_config = ConfigDict(from_attributes = True)
  id: int
  name: str
  connection: str
  email: str
  role: str
  is_active: bool
