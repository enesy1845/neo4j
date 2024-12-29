# routers/users.py

from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session
from typing import List, Optional
from pydantic import BaseModel, Field

from tools.database import get_db
from tools.models import User
from tools.user import add_user, delete_user, update_user
from tools.token_generator import get_current_user

router = APIRouter()

# ========== Pydantic Models ==========

class UserResponse(BaseModel):
    user_id: str
    username: str
    role: str
    class_name: str
    school_id: str
    name: str
    surname: str

    class Config:
        orm_mode = True  # SQLAlchemy model -> Pydantic

class UpdateUserRequest(BaseModel):
    name: Optional[str]
    surname: Optional[str]
    class_name: Optional[str]
    role: Optional[str]
    registered_section: Optional[str]

# ========== Endpoints ==========

@router.get("/", response_model=List[UserResponse], summary="List all users")
def list_all_users(db: Session = Depends(get_db), current_user: User = Depends(get_current_user)):
    if current_user.role != "admin":
        raise HTTPException(status_code=403, detail="Only admins can list users.")
    # Sorgu
    users = db.query(User).all()
    # FastAPI otomatik olarak her User nesnesini UserResponse’a dönüştürecek (orm_mode = True).
    return users

#delete_user_endpoint - delete

#update_user_endpoint - put