# routers/auth.py

from fastapi import APIRouter, Depends, HTTPException
from pydantic import BaseModel, Field, root_validator, validator
from tools.database import get_db
from tools.user import register_user, login_user
from tools.token_generator import create_access_token

router = APIRouter()

class RegisterRequest(BaseModel):
    username: str = Field(..., min_length=3, max_length=50)
    password: str
    name: str
    surname: str
    class_name: str
    role: str
    registered_section: str | None = None

    @validator("name")
    def validate_name(cls, value):
        if len(value) < 2:
            raise ValueError("Name must be at least 2 characters long!")
        return value

    @validator("surname")
    def validate_surname(cls, value):
        if len(value) < 2:
            raise ValueError("Surname must be at least 2 characters long!")
        return value

    @root_validator
    def validate_password_complexity(cls, values):
        pwd = values.get("password")
        if not pwd:
            raise ValueError("Password is required.")
        if len(pwd) < 8:
            raise ValueError("Password must be at least 8 characters long.")
        if not any(c.isupper() for c in pwd):
            raise ValueError("Password must include at least one uppercase letter.")
        if not any(c.islower() for c in pwd):
            raise ValueError("Password must include at least one lowercase letter.")
        if not any(c.isdigit() for c in pwd):
            raise ValueError("Password must include at least one digit.")
        return values

class RegisterResponse(BaseModel):
    message: str

class LoginRequest(BaseModel):
    username: str
    password: str

class LoginResponse(BaseModel):
    access_token: str
    token_type: str = "bearer"
    role: str

@router.post("/register", response_model=RegisterResponse)
def register_endpoint(request: RegisterRequest, session = Depends(get_db)):
    success = register_user(
        session=session,
        username=request.username,
        password=request.password,
        name=request.name,
        surname=request.surname,
        class_name=request.class_name,
        role=request.role,
        registered_section=request.registered_section,
    )
    if not success:
        raise HTTPException(status_code=400, detail="Username already exists or default school not found.")
    return {"message": "Registration successful."}

@router.post("/login", response_model=LoginResponse)
def login_endpoint(body: LoginRequest, session = Depends(get_db)):
    user = login_user(session, body.username, body.password)
    if not user:
        raise HTTPException(status_code=401, detail="Invalid username or password.")
    token = create_access_token(user["user_id"])
    return {
        "access_token": token,
        "token_type": "bearer",
        "role": user["role"]
    }
