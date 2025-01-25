# routers/users.py
from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session
from typing import List, Optional
from pydantic import BaseModel
from uuid import UUID
from tools.database import get_db
from tools.models import User
from tools.user import delete_user, update_user
from tools.token_generator import get_current_user
from tools.utils import hash_password

router = APIRouter()

# ========== Pydantic Models ==========
class UserResponse(BaseModel):
    user_id: UUID
    username: str
    role: str
    class_name: str
    school_id: UUID
    name: str
    surname: str
    registered_section: Optional[str] = None
    attempts: int
    score_avg: float

    class Config:
        orm_mode = True

class UpdateUserRequest(BaseModel):
    name: Optional[str]
    surname: Optional[str]
    class_name: Optional[str]
    role: Optional[str]
    registered_section: Optional[str]
    new_password: Optional[str] = None

class SelfUpdateRequest(BaseModel):
    """
    Kendi profilini (student/teacher) güncelleme talebi
    """
    name: Optional[str]
    surname: Optional[str]
    class_name: Optional[str]
    new_password: Optional[str] = None


# ========== Yardımcı Fonksiyon ==========
def validate_password_strength(password: str) -> bool:
    """8 karakter, en az 1 büyük/küçük/rakam"""
    if len(password) < 8:
        return False
    if not any(c.isupper() for c in password):
        return False
    if not any(c.islower() for c in password):
        return False
    if not any(c.isdigit() for c in password):
        return False
    return True


# ========== Endpoints ==========

# 1. Önce /me endpoint'ini tanımla
@router.get("/me", response_model=UserResponse, summary="Get current user info")
def get_current_user_info(db: Session = Depends(get_db), current_user: User = Depends(get_current_user)):
    """
    Student, teacher veya admin farketmez, kendi bilgilerini döndür.
    """
    return current_user

@router.put("/me", summary="Update your own profile")
def update_own_profile(request: SelfUpdateRequest,
                       db: Session = Depends(get_db),
                       current_user: User = Depends(get_current_user)):
    """
    Student/Teacher kendi profilini güncelleyebilir (Ad, Soyad, Sınıf, Parolayı)
    Admin de isterse bu endpoint'i kendi kendine çağırabilir.
    """
    # Parola güncelleme
    if request.new_password and request.new_password.strip():
        if not validate_password_strength(request.new_password.strip()):
            raise HTTPException(status_code=400, detail="New password does not meet complexity rules.")
        current_user.password = hash_password(request.new_password.strip())

    if request.name is not None:
        current_user.name = request.name
    if request.surname is not None:
        current_user.surname = request.surname
    if request.class_name is not None:
        current_user.class_name = request.class_name

    db.commit()
    db.refresh(current_user)
    return {"message": "Profile updated successfully."}

# 2. Daha sonra /{username} endpoint'ini tanımla
@router.put("/{username}", summary="Update a user (Admin)")
def update_user_endpoint(username: str,
                         request: UpdateUserRequest,
                         db: Session = Depends(get_db),
                         current_user: User = Depends(get_current_user)):
    """
    Admin'in başkalarını güncelleyebildiği endpoint
    """
    if current_user.role != "admin":
        raise HTTPException(status_code=403, detail="Only admins can update users.")

    update_fields = {}
    if request.name is not None:
        update_fields["name"] = request.name
    if request.surname is not None:
        update_fields["surname"] = request.surname
    if request.class_name is not None:
        update_fields["class_name"] = request.class_name
    if request.role is not None:
        update_fields["role"] = request.role
    if request.registered_section is not None:
        update_fields["registered_section"] = request.registered_section

    # Parola kontrolü
    if request.new_password is not None and request.new_password.strip() != "":
        if not validate_password_strength(request.new_password.strip()):
            raise HTTPException(status_code=400, detail="Password does not meet complexity rules.")
        hashed = hash_password(request.new_password.strip())
        update_fields["password"] = hashed

    success = update_user(db, current_user, username, **update_fields)
    if not success:
        raise HTTPException(status_code=404, detail="User not found or not updated.")
    return {"message": f"User {username} updated successfully."}

@router.get("/", response_model=List[UserResponse], summary="List all users")
def list_all_users(db: Session = Depends(get_db), current_user: User = Depends(get_current_user)):
    if current_user.role != "admin":
        raise HTTPException(status_code=403, detail="Only admins can list users.")
    users = db.query(User).all()
    return users

@router.delete("/{username}", summary="Delete a user")
def delete_user_endpoint(username: str,
                         db: Session = Depends(get_db),
                         current_user: User = Depends(get_current_user)):
    if current_user.role != "admin":
        raise HTTPException(status_code=403, detail="Only admins can delete users.")
    success = delete_user(db, current_user, username)
    if not success:
        raise HTTPException(status_code=404, detail="User not found or not deleted.")
    return {"message": f"User {username} deleted successfully."}
