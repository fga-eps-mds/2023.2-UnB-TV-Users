from pydantic import BaseModel, ConfigDict
from typing import Union

class UserUpdate(BaseModel):
  display_name: Union[str, None] = None
  email: Union[str, None] = None

class User(BaseModel):
  model_config = ConfigDict(from_attributes = True)
  display_name: str
  email: str