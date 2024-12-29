# routers/exams.py

from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session
from datetime import datetime
from typing import Dict
from pydantic import BaseModel

from tools.database import get_db
from tools.models import User
from tools.exam import select_questions, process_results
from tools.token_generator import get_current_user

router = APIRouter()

# ========== Pydantic Models ==========

class QuestionItem(BaseModel):
    question_id: str
    external_id: str
    question: str
    type: str
    points: int

class SectionQuestions(BaseModel):
    section: int
    questions: list[QuestionItem]

class StartExamResponse(BaseModel):
    message: str
    questions: list[SectionQuestions]

#SubmitExamRequest,SubmitExamResponse

# ========== Endpoints ==========

@router.post("/start", response_model=StartExamResponse, summary="Start an exam")
def start_exam_endpoint(db: Session = Depends(get_db), current_user: User = Depends(get_current_user)):
    if current_user.role != "student":
        raise HTTPException(status_code=403, detail="Only students can start an exam.")
    if current_user.attempts >= 2:
        raise HTTPException(status_code=400, detail="You have no remaining exam attempts.")

    selected_questions = select_questions(db, current_user)
    if not selected_questions:
        raise HTTPException(status_code=400, detail="No questions available.")

    response_data = []
    for section, qs in selected_questions.items():
        question_list = []
        for q in qs:
            question_list.append(QuestionItem(
                question_id=str(q.id),
                external_id=q.external_id,
                question=q.question,
                type=q.type,
                points=q.points,
            ))
        response_data.append(SectionQuestions(
            section=section,
            questions=question_list
        ))
    return {"message": "Exam started", "questions": response_data}

#submit_exam_endpoint - post
