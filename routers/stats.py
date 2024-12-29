# routers/stats.py

from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session
from typing import List
from pydantic import BaseModel

from tools.database import get_db
from tools.models import User, Statistics
from tools.token_generator import get_current_user

router = APIRouter()

# ========== Pydantic Models ==========

class StatisticResponse(BaseModel):
    school_id: str
    class_name: str
    section_number: int
    correct_questions: int
    wrong_questions: int
    average_score: float
    section_percentage: float

# ========== Endpoints ==========

@router.get("/", response_model=List[StatisticResponse], summary="View statistics")
def view_statistics(db: Session = Depends(get_db), current_user: User = Depends(get_current_user)):
    if current_user.role not in ["teacher", "admin"]:
        raise HTTPException(status_code=403, detail="Only teachers or admins can view statistics.")

    stats = db.query(Statistics).all()
    if not stats:
        return []

    response_data = []
    for s in stats:
        response_data.append(StatisticResponse(
            school_id=str(s.school_id),
            class_name=s.class_name,
            section_number=s.section_number,
            correct_questions=s.correct_questions,
            wrong_questions=s.wrong_questions,
            average_score=s.average_score,
            section_percentage=s.section_percentage
        ))
    return response_data
