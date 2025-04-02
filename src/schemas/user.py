from pydantic import BaseModel, EmailStr, Field

class UserBase(BaseModel):
    "Base user model with email validation"
    email: EmailStr

class UserCreate(UserBase):
    "Create user model with password len validation"
    password: str = Field(..., min_length=8)

class UserRead(UserBase):
    "Read user model for response"
    id: int

    class Config:
        from_attributes = True