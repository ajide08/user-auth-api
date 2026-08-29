from pydantic import BaseModel, EmailStr

class UserInCreate(BaseModel):
    name: str
    email: EmailStr
    password: str

class UserOutput(BaseModel):
    id: int
    name: str
    email: EmailStr

class UserInUpdate(BaseModel):
    id: int
    name: str | None = None
    email: EmailStr | None = None
    password: str | None = None

class UserInLogin(BaseModel):
    email: EmailStr
    password: str

class TokenResponse(BaseModel):
    token_type: str
    access_token: str
    refresh_token: str
    user: UserOutput | None = None

class RefreshTokenRequest(BaseModel):
    refresh_token: str
    