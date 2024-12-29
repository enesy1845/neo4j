# routers/auth.py

from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session
from pydantic import BaseModel, Field
from tools.database import get_db
from tools.user import register_user, login_user
from tools.token_generator import create_access_token

router = APIRouter()

# ========== Pydantic Models ==========

class RegisterRequest(BaseModel):
    username: str = Field(..., min_length=3, max_length=50)
    password: str = Field(..., min_length=3)
    name: str
    surname: str
    class_name: str
    role: str
    registered_section: str | None = None

class RegisterResponse(BaseModel):
    message: str

class LoginRequest(BaseModel):
    username: str
    password: str

class LoginResponse(BaseModel):
    access_token: str
    token_type: str = "bearer"

# ========== Endpoints ==========

@router.post("/register", response_model=RegisterResponse)
def register_endpoint(request: RegisterRequest, db: Session = Depends(get_db)):
    success = register_user(
        db=db,
        username=request.username,
        password=request.password,
        name=request.name,
        surname=request.surname,
        class_name=request.class_name,
        role=request.role,
        registered_section=request.registered_section,
    )
    if not success:
        raise HTTPException(
            status_code=400, 
            detail="Username already exists or default school not found."
        )
    return {"message": "Registration successful."}

@router.post("/login", response_model=LoginResponse)
def login_endpoint(request: LoginRequest, db: Session = Depends(get_db)):
    user = login_user(db, request.username, request.password)
    if not user:
        raise HTTPException(status_code=400, detail="Invalid credentials.")
    token = create_access_token(str(user.user_id))
    return {"access_token": token, "token_type": "bearer"}
