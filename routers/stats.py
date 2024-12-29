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

#view_statistics-get
