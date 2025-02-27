# routers/exams.py
from fastapi import APIRouter, Depends, HTTPException
from datetime import datetime
from typing import Dict, List, Optional
from pydantic import BaseModel
from uuid import uuid4
from tools.database import get_db
from tools.exam import select_questions, process_results
from tools.token_generator import get_current_user

router = APIRouter()

class ChoiceAnswer(BaseModel):
    selected_texts: Optional[List[str]] = None

class SubmitExamRequest(BaseModel):
    exam_id: str
    answers: Dict[str, ChoiceAnswer]

class SubmitExamResponse(BaseModel):
    message: str

@router.post("/start", summary="Start an exam")
def start_exam_endpoint(session = Depends(get_db), current_user = Depends(get_current_user)):
    if current_user["role"] != "student":
        raise HTTPException(status_code=403, detail="Only students can start an exam.")
    if current_user.get("attempts", 0) >= 2:
        raise HTTPException(status_code=400, detail="You have no remaining exam attempts.")

    # Ongoing exam sorgulaması
    query = """
    MATCH (e:Exam {user_id: $user_id, status: 'in_progress'})
    RETURN e LIMIT 1
    """
    result = session.run(query, {"user_id": current_user["user_id"]})
    record = result.single()
    if record:
        exam_node = record["e"]
        q_result = session.run("""
        MATCH (e:Exam {exam_id: $exam_id})-[:CONTAINS]->(q:Question)
        OPTIONAL MATCH (q)-[:HAS_CHOICE]->(c:Choice)
        RETURN q, collect(c) as choices
        """, {"exam_id": exam_node["exam_id"]})
        questions_data = {}
        for rec in q_result:
            q = rec["q"]
            sec = q["section"]
            if sec not in questions_data:
                questions_data[sec] = []
            choices = rec["choices"]
            questions_data[sec].append({
                "question_id": q["id"],
                "external_id": q["external_id"],
                "question": q["question"],
                "points": q["points"],
                "type": q["type"],
                "choices": [{"choice_id": c["id"], "choice_text": c["choice_text"]} for c in choices if c is not None]
            })
        return {
            "message": "You have an exam in progress. Please resume it.",
            "exam_id": exam_node["exam_id"],
            "questions": questions_data,
            "status": exam_node["status"]
        }

    # Yeni sınav oluşturma
    selected_questions = select_questions(session, current_user)
    if not selected_questions:
        raise HTTPException(status_code=400, detail="No questions available.")
    exam_id = str(uuid4())
    start_time = datetime.utcnow().isoformat()
    create_exam_query = """
    CREATE (e:Exam {
        exam_id: $exam_id,
        user_id: $user_id,
        class_name: $class_name,
        start_time: datetime($start_time),
        status: 'in_progress'
    })
    """
    session.run(create_exam_query, {
        "exam_id": exam_id,
        "user_id": current_user["user_id"],
        "class_name": current_user["class_name"],
        "start_time": start_time
    })


    # Ek olarak, kullanıcı ile sınav arasında açık ilişki kuruyoruz:
    session.run("""
    MATCH (u:User {user_id: $user_id}), (e:Exam {exam_id: $exam_id})
    MERGE (u)-[:TAKES_EXAM]->(e)
    """, {"user_id": current_user["user_id"], "exam_id": exam_id})

    for sec, qs in selected_questions.items():
        for q in qs:
            session.run("""
            MATCH (e:Exam {exam_id: $exam_id}), (q:Question {id: $question_id})
            CREATE (e)-[:CONTAINS]->(q)
            """, {"exam_id": exam_id, "question_id": q["id"]})
    q_result = session.run("""
    MATCH (e:Exam {exam_id: $exam_id})-[:CONTAINS]->(q:Question)
    OPTIONAL MATCH (q)-[:HAS_CHOICE]->(c:Choice)
    RETURN q, collect(c) as choices
    """, {"exam_id": exam_id})
    questions_data = {}
    for rec in q_result:
        q = rec["q"]
        sec = q["section"]
        if sec not in questions_data:
            questions_data[sec] = []
        choices = rec["choices"]
        questions_data[sec].append({
            "question_id": q["id"],
            "external_id": q["external_id"],
            "question": q["question"],
            "points": q["points"],
            "type": q["type"],
            "choices": [{"choice_id": c["id"], "choice_text": c["choice_text"]} for c in choices if c is not None]
        })
    return {
        "message": "Exam started",
        "exam_id": exam_id,
        "questions": questions_data,
        "status": "in_progress"
    }

@router.post("/submit", response_model=SubmitExamResponse, summary="Submit exam answers")
def submit_exam_endpoint(body: SubmitExamRequest, session = Depends(get_db), current_user = Depends(get_current_user)):
    if current_user["role"] != "student":
        raise HTTPException(status_code=403, detail="Only students can submit exam answers.")
    if current_user.get("attempts", 0) >= 2:
        raise HTTPException(status_code=400, detail="You have no remaining exam attempts.")
    result = session.run("""
    MATCH (e:Exam {exam_id: $exam_id, user_id: $user_id})
    RETURN e LIMIT 1
    """, {"exam_id": body.exam_id, "user_id": current_user["user_id"]})
    record = result.single()
    if not record:
        raise HTTPException(status_code=404, detail="Exam not found.")
    exam_node = record["e"]
    if exam_node.get("end_time") is not None:
        raise HTTPException(status_code=400, detail="Exam has already been submitted.")

    q_result = session.run("""
    MATCH (e:Exam {exam_id: $exam_id})-[:CONTAINS]->(q:Question)
    RETURN q
    """, {"exam_id": body.exam_id})
    selected_questions = [rec["q"] for rec in q_result]
    if not selected_questions:
        raise HTTPException(status_code=400, detail="No questions associated with this exam.")

    end_time = datetime.utcnow().isoformat()
    process_results(session, current_user, exam_node, selected_questions, body.answers, end_time)
    session.run("""
    MATCH (e:Exam {exam_id: $exam_id})
    SET e.end_time = datetime($end_time), e.status = 'submitted'
    """, {"exam_id": body.exam_id, "end_time": end_time})
    return {"message": "Exam submitted successfully."}
