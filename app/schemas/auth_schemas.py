from pydantic import BaseModel, Field

class UserRegister(BaseModel):
    username: str = Field(..., json_schema_extra="myuser")
    password: str = Field(..., json_schema_extra="mypassword")
    role: str = Field("user", json_schema_extra="read_only")

class UserLogin(BaseModel):
    username: str
    password: str

class UserOut(BaseModel):
    id: int
    username: str
    role: str

    class ConfigDict:
        from_attributes = True

class TokenOut(BaseModel):
    access_token: str
    token_type: str = "bearer"
