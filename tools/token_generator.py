# tools/token_generator.py
import jwt
import datetime
import os
from fastapi import Depends, HTTPException
from fastapi.security import HTTPBearer, HTTPAuthorizationCredentials
from tools.database import get_db
from tools.security import verify_access_token

bearer_scheme = HTTPBearer()
SECRET_KEY = os.getenv("SECRET_KEY", "TEST_SECRET_KEY")
ALGORITHM = "HS256"
ACCESS_TOKEN_EXPIRE_MINUTES = 60

def create_access_token(user_id: str):
    expire = datetime.datetime.utcnow() + datetime.timedelta(minutes=ACCESS_TOKEN_EXPIRE_MINUTES)
    payload = {"user_id": user_id, "exp": expire}
    token = jwt.encode(payload, SECRET_KEY, algorithm=ALGORITHM)
    return token

def get_current_user(credentials: HTTPAuthorizationCredentials = Depends(bearer_scheme), session = Depends(get_db)):
    token = credentials.credentials
    payload = verify_access_token(token)
    if not payload:
        raise HTTPException(status_code=401, detail="Invalid token.")
    user_id = payload.get("user_id")
    if not user_id:
        raise HTTPException(status_code=401, detail="Invalid token payload.")
    result = session.run("""
MATCH (u:User {user_id: $user_id})
OPTIONAL MATCH (u)-[:BELONGS_TO|TEACHES]->(c:Class)
OPTIONAL MATCH (c)<-[:HAS_CLASS]-(s:School)
RETURN u, c.name as class_name, s.school_id as school_id, u.registered_section as registered_section
""", {"user_id": user_id})
    record = result.single()
    if not record:
        raise HTTPException(status_code=401, detail="User not found.")
    user = dict(record["u"])
    user["class_name"] = record.get("class_name") or ""
    user["school_id"] = record.get("school_id") or ""
    user["registered_section"] = record.get("registered_section") or ""
    return user
