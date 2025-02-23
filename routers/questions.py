# routers/questions.py
from fastapi import APIRouter, Depends, HTTPException
from typing import List, Optional
from pydantic import BaseModel, Field
from uuid import uuid4
from tools.database import get_db
from tools.token_generator import get_current_user

router = APIRouter()

class ChoiceModel(BaseModel):
    choice_text: str
    is_correct: Optional[bool] = False
    correct_position: Optional[int] = None

class AddQuestionRequest(BaseModel):
    question_text: str
    q_type: str
    points: int
    section: int
    choices: List[ChoiceModel] = []

class AddQuestionResponse(BaseModel):
    message: str
    external_id: str

class QuestionChoiceResponse(BaseModel):
    choice_text: str
    is_correct: bool
    correct_position: Optional[int]

class QuestionResponse(BaseModel):
    id: str
    external_id: str
    section: int
    question: str
    points: int
    q_type: str
    choices: List[QuestionChoiceResponse]

@router.post("/", response_model=AddQuestionResponse, summary="Add a new question (advanced DB schema)")
def add_question(body: AddQuestionRequest, session = Depends(get_db), current_user = Depends(get_current_user)):
    if current_user["role"] != "teacher":
        raise HTTPException(status_code=403, detail="Only teachers can add questions.")
    external_id = str(uuid4())
    question_id = str(uuid4())
    session.run("""
    CREATE (q:Question {
        id: $id,
        external_id: $external_id,
        section: $section,
        question: $question,
        points: $points,
        type: $q_type
    })
    """, {
        "id": question_id,
        "external_id": external_id,
        "section": body.section,
        "question": body.question_text,
        "points": body.points,
        "q_type": body.q_type
    })
    for ch in body.choices:
        choice_id = str(uuid4())
        session.run("""
        MATCH (q:Question {id: $question_id})
        CREATE (c:Choice {
            id: $choice_id,
            choice_text: $choice_text,
            is_correct: $is_correct,
            correct_position: $correct_position
        })
        CREATE (q)-[:HAS_CHOICE]->(c)
        """, {
            "question_id": question_id,
            "choice_id": choice_id,
            "choice_text": ch.choice_text.strip(),
            "is_correct": ch.is_correct or False,
            "correct_position": ch.correct_position
        })
    return {"message": "Question added successfully with new DB schema", "external_id": external_id}

@router.get("/", response_model=List[QuestionResponse], summary="List all questions (advanced DB schema)")
def list_all_questions(session = Depends(get_db), current_user = Depends(get_current_user)):
    if current_user["role"] not in ["teacher", "admin"]:
        raise HTTPException(status_code=403, detail="Only teachers or admins can list questions.")
    result = session.run("""
    MATCH (q:Question)
    OPTIONAL MATCH (q)-[:HAS_CHOICE]->(c:Choice)
    RETURN q, collect(c) as choices
    """)
    results = []
    for record in result:
        q = record["q"]
        choices = record["choices"]
        choice_list = []
        for c in choices:
            if c:
                choice_list.append({
                    "choice_text": c["choice_text"],
                    "is_correct": c["is_correct"],
                    "correct_position": c["correct_position"]
                })
        results.append({
            "id": q["id"],
            "external_id": q["external_id"],
            "section": q["section"],
            "question": q["question"],
            "points": q["points"],
            "q_type": q["type"],
            "choices": choice_list
        })
    return results
