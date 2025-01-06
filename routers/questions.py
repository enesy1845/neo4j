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

# class AddQuestionResponse(BaseModel):
#     external_id: uuid4

    
#AddQuestionResponse
#QuestionResponse


# ========== Endpoints ==========

# @router.post("/", response_model=AddQuestionResponse, summary="Add a new question")
# def add_question(
#     body: AddQuestionRequest,
#     db: Session = Depends(get_db),
#     current_user: User = Depends(get_current_user)
# ):
#     if current_user.role != "teacher":
#         raise HTTPException(status_code=403, detail="Only teachers can add questions.")
#     if not current_user.registered_section:
#         raise HTTPException(status_code=400, detail="Teacher has no registered section.")
#     if body.q_type not in ['single_choice', 'multiple_choice', 'true_false', 'ordering']:
#         raise HTTPException(status_code=400, detail="Invalid question type.")

#     external_id = str(uuid4())
#     section = int(current_user.registered_section)

#     new_q = Question(
#         external_id=external_id,
#         section=section,
#         question=body.question_text,
#         points=body.points,
#         type=body.q_type
#     )
#     db.add(new_q)
#     db.commit()
#     db.refresh(new_q)

#     ans = Answer(
#         question_id=new_q.id,
#         correct_answer=body.correct_answer.strip()
#     )
#     db.add(ans)
#     db.commit()

#     return {"message": "Question added successfully", "external_id": external_id}

# #list_all_questions - get
