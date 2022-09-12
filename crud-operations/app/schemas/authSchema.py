from pydantic import BaseModel


class AuthDetails(BaseModel):
    username: str
    password: str


class Token(BaseModel):
    token: str


class ActivationBody(BaseModel):
    activation_code: str
    password: str
