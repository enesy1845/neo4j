# routers/results.py
from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session
from typing import List,Optional
from pydantic import BaseModel
from tools.database import get_db
from tools.models import User, Exam, ExamAnswer, Question
from tools.token_generator import get_current_user

router = APIRouter()

# ========== Pydantic Models ==========
class AnswerDetail(BaseModel):
    question_id: str
    external_id: str
    question: str
    user_answer: str
    is_correct: bool
    points_earned: int

class ExamDetail(BaseModel):
    exam_id: str
    start_time: str
    end_time: Optional[str] = None  # <-- Artık None kabul edilir.
    score_avg: float
    answers: List[AnswerDetail]

class ExamResultResponse(BaseModel):
    exams: List[ExamDetail]

# ========== Endpoints ==========
@router.get("/results", response_model=ExamResultResponse, summary="View your exam results")
def view_exam_results(db: Session = Depends(get_db), current_user: User = Depends(get_current_user)):
    if current_user.role != "student":
        raise HTTPException(status_code=403, detail="Only students can view their exam results.")
    
    exams = db.query(Exam).filter(Exam.user_id == current_user.user_id).all()
    if not exams:
        return {"exams": []}
    
    exam_details = []
    for exam in exams:
        exam_answers = db.query(ExamAnswer).filter(ExamAnswer.exam_id == exam.exam_id).all()
        answers = []
        for ans in exam_answers:
            question = db.query(Question).filter(Question.id == ans.question_id).first()
            if not question:
                continue
            answers.append(AnswerDetail(
                question_id=str(question.id),
                external_id=question.external_id,
                question=question.question,
                user_answer=ans.user_answer,
                is_correct=ans.is_correct,
                points_earned=ans.points_earned
            ))
        exam_detail = ExamDetail(
            exam_id=str(exam.exam_id),
            start_time=exam.start_time.isoformat(),
            end_time=exam.end_time.isoformat() if exam.end_time else None,
            score_avg=current_user.score_avg,
            answers=answers
        )
        exam_details.append(exam_detail)
    
    return {"exams": exam_details}