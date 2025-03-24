from pydantic import BaseModel


class UserUpdateInput(BaseModel):
    name: str
    email: str
    password: str
