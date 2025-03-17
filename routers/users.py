# routers/users.py
from fastapi import APIRouter, Depends, HTTPException, Path, Body
from typing import List, Optional
from pydantic import BaseModel, Field
from tools.database import get_db
from tools.token_generator import get_current_user
from tools.user import delete_user, update_user
from tools.utils import hash_password

router = APIRouter()

class UserResponse(BaseModel):
    user_id: str
    username: str
    role: str
    class_name: Optional[str] = Field(None, description="Required for students and teachers")  # ✅ class_name artık zorunlu değil
    school_id: str
    name: str
    surname: str
    registered_section: Optional[str] = None
    attempts: int
    score_avg: float
    okul_no: Optional[int]

class UpdateUserRequest(BaseModel):
    name: Optional[str] = None
    surname: Optional[str] = None
    class_name: Optional[str] = None
    role: Optional[str] = None
    registered_section: Optional[str] = None
    new_password: Optional[str] = None

class SelfUpdateRequest(BaseModel):
    name: Optional[str] = None
    surname: Optional[str] = None
    class_name: Optional[str] = None
    new_password: Optional[str] = None

def validate_password_strength(password: str) -> bool:
    if len(password) < 8:
        return False
    if not any(c.isupper() for c in password):
        return False
    if not any(c.islower() for c in password):
        return False
    if not any(c.isdigit() for c in password):
        return False
    return True

@router.get("/me", response_model=UserResponse, summary="Get current user details")
def read_current_user(current_user = Depends(get_current_user)):
    # Eğer current_user, ilişkisel bilgileri içermiyorsa; isteniyorsa get_current_user fonksiyonunda da
    # ilişkilerden class_name ve school_id eklenebilir.
    return current_user

@router.put("/me", summary="Update current user's profile")
def update_current_user(request: SelfUpdateRequest, session = Depends(get_db), current_user = Depends(get_current_user)):
    update_fields = {}
    if request.name is not None:
        update_fields["name"] = request.name
    if request.surname is not None:
        update_fields["surname"] = request.surname
    if request.class_name is not None:
        update_fields["class_name"] = request.class_name
    if request.new_password is not None and request.new_password.strip() != "":
        if not validate_password_strength(request.new_password.strip()):
            raise HTTPException(status_code=400, detail="Password does not meet complexity rules.")
        update_fields["password"] = hash_password(request.new_password.strip())
    if not update_fields:
        return {"message": "No changes provided."}
    success = update_user(session, current_user, current_user["user_id"], **update_fields)
    if not success:
        raise HTTPException(status_code=404, detail="User not updated.")
    current_user_dict = dict(current_user)
    current_user_dict.update(update_fields)
    return {"message": "Profile updated successfully.", "user": current_user_dict}

@router.get("/", response_model=List[UserResponse], summary="List all users")
def list_all_users(session = Depends(get_db), current_user = Depends(get_current_user)):
    if current_user["role"] != "admin":
        raise HTTPException(status_code=403, detail="Only admins can list users.")
    # Grafik modeline göre kullanıcı bilgilerini ilişkilerden almak için sorgu:
    query = """
    MATCH (u:User)
    OPTIONAL MATCH (u)-[:BELONGS_TO|TEACHES]->(c:Class) 
    OPTIONAL MATCH (c)<-[:HAS_CLASS]-(s:School)
    RETURN u, c.name as class_name, s.school_id as school_id
    """
    result = session.run(query)
    users = []
    for record in result:
        # Node objesini dict'e çeviriyoruz
        user = dict(record["u"])
        user["class_name"] = record.get("class_name") or ""
        user["school_id"] = record.get("school_id") or ""
        users.append(user)
    return users

@router.put("/{user_id}", summary="Update a user (Admin)")
def update_user_endpoint(user_id: str, request: UpdateUserRequest, session = Depends(get_db), current_user = Depends(get_current_user)):
    if current_user["role"] != "admin":
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
    if request.new_password is not None and request.new_password.strip() != "":
        if not validate_password_strength(request.new_password.strip()):
            raise HTTPException(status_code=400, detail="Password does not meet complexity rules.")
        update_fields["password"] = hash_password(request.new_password.strip())
    success = update_user(session, current_user, user_id, **update_fields)
    if not success:
        raise HTTPException(status_code=404, detail="User not found or not updated.")
    return {"message": "User updated successfully."}

@router.delete("/{username}", summary="Delete a user")
def delete_user_endpoint(username: str, session = Depends(get_db), current_user = Depends(get_current_user)):
    if current_user["role"] != "admin":
        raise HTTPException(status_code=403, detail="Only admins can delete users.")
    success = delete_user(session, current_user, username)
    if not success:
        raise HTTPException(status_code=404, detail="User not found or not deleted.")
    return {"message": f"User {username} deleted successfully."}
