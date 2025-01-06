# routers/users.py

from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session
from typing import List
from pydantic import BaseModel
from uuid import UUID  # UUID türünü ekleyin
from typing import Optional, List
from tools.database import get_db
from tools.models import User
from tools.user import add_user, delete_user, update_user
from tools.token_generator import get_current_user
from tools.utils import check_password
from tools.security import create_access_token
from tools.dependencies import get_current_admin

router = APIRouter()

# ========== Pydantic Models ==========
class UserBase(BaseModel):
    username: str
    name: str
    surname: str
    phone_number: Optional[str]
    role: str
    class_name: str

class UserCreate(UserBase):
    password: str  # Şifre sadece oluşturma sırasında gerekli

class UserResponse(UserBase):
    user_id: UUID

    class Config:
        orm_mode = True


class UserLogin(BaseModel):
    username: str
    password: str
    
    
    
    
# class UserResponse(BaseModel):
#     user_id: UUID  # str yerine UUID kullanın
#     username: str
#     role: str
#     class_name: str
#     school_id: UUID  # str yerine UUID kullanın
#     name: str
#     surname: str

#     class Config:
#         orm_mode = True  # SQLAlchemy model -> Pydantic

class UpdateUserRequest(BaseModel):
    name: Optional[str]
    surname: Optional[str]
    class_name: Optional[str]
    role: Optional[str]
    registered_section: Optional[str]
# ========== Endpoints ==========

# @router.get("/", response_model=List[UserResponse], summary="List all users")
# def list_all_users(db: Session = Depends(get_db), current_user: User = Depends(get_current_user)):
#     if current_user.role != "admin":
#         raise HTTPException(status_code=403, detail="Only admins can list users.")
#     # Sorgu
#     users = db.query(User).all()
#     # FastAPI otomatik olarak her User nesnesini UserResponse’a dönüştürecek (orm_mode = True).
#     return users

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

@router.put("/{username}", summary="Update a user")
def update_user_endpoint(username: str,
    request: UpdateUserRequest,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)):
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
    success = update_user(db, current_user, username, **update_fields)
    if not success:
        raise HTTPException(status_code=404, detail="User not found or not updated.")
    return {"message": f"User {username} updated successfully."}


@router.post("/login")
def login(user: UserLogin, db: Session = Depends(get_db)):
    # Kullanıcıyı kontrol et
    db_user = db.query(User).filter(User.username == user.username).first()
    if not db_user or not check_password(user.password, db_user.password):
        
        raise HTTPException(status_code=401, detail=f"Invalid username or password 1{user.username}" )
    
    # Token oluştur
    access_token = create_access_token({"sub": db_user.username, "role": db_user.role})
    return {"access_token": access_token, "token_type": "bearer"}

#Tüm kullanıcıları listeleme
@router.get("/", response_model=list[UserResponse])
def list_users(db: Session = Depends(get_db)):
    return db.query(User).all()

@router.get("/admin", dependencies=[Depends(get_current_admin)])
def admin_only_route():
    return {"message": "Welcome, Admin!"}