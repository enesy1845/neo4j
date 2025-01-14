# routers/exams.py
from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session
from datetime import datetime
from typing import Dict, List,Optional
from pydantic import BaseModel
from uuid import UUID

from tools.database import get_db
from tools.models import User, Exam, Question, Answer,exam_question_association
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
    # Yeni ekledik:
    choices: Optional[List[str]] = None

class SectionQuestions(BaseModel):
    section: int
    questions: List[QuestionItem]

class StartExamResponse(BaseModel):
    message: str
    exam_id: UUID
    questions: List[SectionQuestions]

class SubmitExamRequest(BaseModel):
    exam_id: UUID
    answers: Dict[str, str]  # { "question_id":"user_answer", ... }

class SubmitExamResponse(BaseModel):
    message: str

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
    
    # Create Exam record
    exam = Exam(
        user_id=current_user.user_id,
        class_name=current_user.class_name,
        school_id=current_user.school_id,
        start_time=datetime.utcnow()
    )
    db.add(exam)
    db.commit()
    db.refresh(exam)
    
    # Associate selected questions with the exam
    all_selected_questions = [q for qs in selected_questions.values() for q in qs]
    exam.selected_questions = all_selected_questions
    db.commit()
    
    # Prepare response data
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
                # DB’de JSON sakladık, UI'ya python list olarak göndermek için:
                choices=q.get_choices_list()  
            ))
        response_data.append(SectionQuestions(
            section=section,
            questions=question_list
        ))
    
    return {"message": "Exam started", "exam_id": exam.exam_id, "questions": response_data}

@router.post("/submit", response_model=SubmitExamResponse, summary="Submit exam answers")
def submit_exam_endpoint(
    body: SubmitExamRequest,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    if current_user.role != "student":
        raise HTTPException(status_code=403, detail="Only students can submit exam answers.")
    if current_user.attempts >= 2:
        raise HTTPException(status_code=400, detail="You have no remaining exam attempts.")
    
    # Retrieve the Exam record
    exam = db.query(Exam).filter(Exam.exam_id == body.exam_id, Exam.user_id == current_user.user_id).first()
    if not exam:
        raise HTTPException(status_code=404, detail="Exam not found.")
    if exam.end_time is not None:
        raise HTTPException(status_code=400, detail="Exam has already been submitted.")
    
    # Retrieve selected questions for this exam
    selected_questions = get_selected_questions_for_exam(db, exam)
    if not selected_questions:
        raise HTTPException(status_code=400, detail="No questions associated with this exam.")
    
    end_time = datetime.utcnow()
    process_results(db, current_user, selected_questions, body.answers, end_time, exam)
    return {"message": "Exam submitted successfully."}

# ========== Helper Functions ==========
def get_selected_questions_for_exam(db: Session, exam: Exam) -> Dict[int, List[Question]]:
    """
    Retrieves the selected questions associated with a specific exam.
    """
    selected_questions = db.query(Question).join(exam_question_association).filter(
        exam_question_association.c.exam_id == exam.exam_id
    ).all()
    sections = {1: [], 2: [], 3: [], 4: []}
    for q in selected_questions:
        sections[q.section].append(q)
    return sections