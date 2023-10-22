from pydantic import BaseModel

class UserUpdate(BaseModel):
    display_name: str 
    email: str 

class User(BaseModel):
    display_name: str
    email: str

class Config:
    from_atribute = True