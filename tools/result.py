# routers/results.py
from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session
from typing import List
from pydantic import BaseModel
from tools.database import get_db
from tools.models import User, Exam, ExamAnswer, QuestionChoice
from tools.token_generator import get_current_user

router = APIRouter()

class ChoiceDetail(BaseModel):
    choice_text: str
    user_position: int | None = None

class AnswerDetail(BaseModel):
    question_id: str
    question_text: str
    points_earned: int
    choices_selected: List[ChoiceDetail]
    # is_correct -> points_earned>0 gibi basit check ile anlayabiliriz.
    # ya da devaml ettirebilirsiniz.

class ExamDetail(BaseModel):
    exam_id: str
    start_time: str
    end_time: str | None
    score_avg: float
    answers: List[AnswerDetail]

class ExamResultResponse(BaseModel):
    exams: List[ExamDetail]

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
        answers_out = []
        for ans in exam_answers:
            q = db.query(QuestionChoice).filter(QuestionChoice.id == ans.question_id).first()  # <-- Bu satır HATALI
            # Yukarı satırda "ans.question_id" 'Question' a refer ediyor, 'QuestionChoice' değil.
            # Doğrusu 'Question' tablosunu almalı:
            question_obj = db.query(...).filter(...).first()
            # Örnek:
            question_obj = ans.exam.exam_answers[0] # yanlıs
            # Düzeltelim:
            from tools.models import Question
            question_obj = db.query(Question).filter(Question.id == ans.question_id).first()

            # user choices
            user_choices = ans.user_choices
            csel = []
            for uc in user_choices:
                # question_choice'ı al
                # question_choice_id = uc.question_choice_id
                qc = db.query(QuestionChoice).filter(QuestionChoice.id == uc.question_choice_id).first()
                if qc:
                    csel.append(ChoiceDetail(
                        choice_text=qc.choice_text,
                        user_position=uc.user_position
                    ))

            answers_out.append(AnswerDetail(
                question_id=str(ans.question_id),
                question_text=question_obj.question if question_obj else "",
                points_earned=ans.points_earned,
                choices_selected=csel
            ))

        exam_details.append(ExamDetail(
            exam_id=str(exam.exam_id),
            start_time=exam.start_time.isoformat(),
            end_time=exam.end_time.isoformat() if exam.end_time else None,
            score_avg=current_user.score_avg,
            answers=answers_out
        ))

    return {"exams": exam_details}
