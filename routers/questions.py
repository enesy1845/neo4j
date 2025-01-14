# routers/questions.py

from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session
from typing import List, Optional
from pydantic import BaseModel, Field
from uuid import uuid4

from tools.database import get_db
from tools.models import User, Question, Answer
from tools.token_generator import get_current_user

router = APIRouter()

# ========== Pydantic Models ==========

class AddQuestionRequest(BaseModel):
    question_text: str
    q_type: str
    points: int
    correct_answer: str

# (Yeni) AddQuestionResponse modeli
class AddQuestionResponse(BaseModel):
    message: str
    external_id: str

# (Yeni) QuestionResponse modeli
class QuestionResponse(BaseModel):
    id: str
    external_id: str
    section: int
    question: str
    points: int
    q_type: str
    correct_answer: str

    class Config:
        orm_mode = True
# (Yeni) AddQuestionResponse modeli
class AddQuestionResponse(BaseModel):
    message: str
    external_id: str

# (Yeni) QuestionResponse modeli
class QuestionResponse(BaseModel):
    id: str
    external_id: str
    section: int
    question: str
    points: int
    q_type: str
    correct_answer: str

    class Config:
        orm_mode = True

# ========== Endpoints ==========

@router.post("/", response_model=AddQuestionResponse, summary="Add a new question")
def add_question(
    body: AddQuestionRequest,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    if current_user.role != "teacher":
        raise HTTPException(status_code=403, detail="Only teachers can add questions.")
    if not current_user.registered_section:
        raise HTTPException(status_code=400, detail="Teacher has no registered section.")
    if body.q_type not in ['single_choice', 'multiple_choice', 'true_false', 'ordering']:
        raise HTTPException(status_code=400, detail="Invalid question type.")

    external_id = str(uuid4())
    section = int(current_user.registered_section)

    new_q = Question(
        external_id=external_id,
        section=section,
        question=body.question_text,
        points=body.points,
        type=body.q_type
    )
    db.add(new_q)
    db.commit()
    db.refresh(new_q)

    ans = Answer(
        question_id=new_q.id,
        correct_answer=body.correct_answer.strip()
    )
    db.add(ans)
    db.commit()

    return {
        "message": "Question added successfully",
        "external_id": external_id
    }
    return {
        "message": "Question added successfully",
        "external_id": external_id
    }

# (Yeni) List all questions - GET
@router.get("/", response_model=List[QuestionResponse], summary="List all questions")
def list_all_questions(
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    """
    Tüm soruları listeleme endpoint'i:
    Sadece teacher veya admin rolü görebilsin, isterseniz 'student' da görebilir.
    """
    if current_user.role not in ["teacher", "admin"]:
        raise HTTPException(status_code=403, detail="Only teachers or admins can list questions.")

    # DB'deki tüm soruları çekiyoruz
    questions = db.query(Question).all()

    # Pydantic'e uygun JSON dönmesi için verileri map'liyoruz
    results = []
    for q in questions:
        correct_ans = q.answer.correct_answer if q.answer else ""
        results.append(QuestionResponse(
            id=str(q.id),
            external_id=q.external_id,
            section=q.section,
            question=q.question,
            points=q.points,
            q_type=q.type,
            correct_answer=correct_ans
        ))
    return results
