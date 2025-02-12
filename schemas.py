from pydantic import BaseModel, EmailStr, field_validator, Field, ValidationInfo


class IdentifyRequest(BaseModel):
    email: EmailStr = Field(default=None) # condition for the valid email
    number: str = Field(default=None, max_length=15, min_length = 10 ) # condition for the valid number
    
class SignUpRequest(BaseModel):
    name: str
    email: EmailStr
    password: str = Field(..., min_length=8) 
    confirm_password: str = Field(..., min_length=8) 
    
    @field_validator("confirm_password")
    @classmethod
    def passwords_match(cls, v: str, info: ValidationInfo):
        password = info.data.get("password")  # Correct way to access fields
        if password and v != password:
            raise ValueError("Passwords do not match")
        return v
    
class LoginRequest(BaseModel):
    email: EmailStr
    password: str = Field(..., min_length = 8)  