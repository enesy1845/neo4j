# routers/results.py

from fastapi import APIRouter, Depends, HTTPException
from typing import List, Dict
from pydantic import BaseModel
from tools.database import get_db
from tools.token_generator import get_current_user
import math
from datetime import datetime

router = APIRouter()

class QuestionDetailModel(BaseModel):
    question_text: str
    student_answers: List[str]
    correct_answers: List[str]
    status: str  # "Correct", "Wrong", "Partially Correct"
    points_earned: int
    points_possible: int

class SectionResult(BaseModel):
    section_number: int
    correct_answers: int
    wrong_answers: int
    so: float  # class average
    oo: float  # school average
    notu: float
    ort: float

class ExamDetailV2(BaseModel):
    start_time: str
    end_time: str | None
    pass_fail: str
    sections_details: List[SectionResult]
    questions_details: List[QuestionDetailModel]
    exam_percentage: float  # overall exam percentage

class ExamResultV2Response(BaseModel):
    student_number: int | None
    class_name: str
    attempts: int
    exams: List[ExamDetailV2]
    overall_percentage: float

def format_datetime(dt):
    if isinstance(dt, str):
        try:
            dt_obj = datetime.fromisoformat(dt)
        except Exception:
            return dt
        return dt_obj.strftime("%b %d, %Y %H:%M:%S")
    elif hasattr(dt, "strftime"):
        return dt.strftime("%b %d, %Y %H:%M:%S")
    else:
        return dt

@router.get("/results_v2", response_model=ExamResultV2Response, summary="View your exam results (table style)")
def view_exam_results_v2(session = Depends(get_db), current_user = Depends(get_current_user)):
    if current_user["role"] != "student":
        raise HTTPException(status_code=403, detail="Only students can view their exam results.")
    exam_result = session.run(
        """
        MATCH (e:Exam)
        WHERE e.user_id = $user_id AND e.end_time IS NOT NULL
        RETURN e ORDER BY e.start_time ASC
        """, {"user_id": current_user["user_id"]}
    )
    exams = [record["e"] for record in exam_result]
    if not exams:
        return {
            "student_number": current_user.get("okul_no"),
            "class_name": current_user["class_name"],
            "attempts": current_user.get("attempts", 0),
            "exams": [],
            "overall_percentage": 0.0
        }
    pass_mark = 75.0
    exam_details_list = []
    stats_map = {}
    stats_result = session.run(
        """
        MATCH (st:Statistics)
        WHERE st.school_id = $school_id AND st.class_name = $class_name
        RETURN st
        """, {"school_id": current_user.get("school_id"), "class_name": current_user["class_name"]}
    )
    for record in stats_result:
        st = record["st"]
        stats_map[st["section_number"]] = st
    total_exam_percentage = 0.0
    for exam in exams:
        exam_id = exam["exam_id"]
        ea_result = session.run(
            """
            MATCH (e:Exam {exam_id: $exam_id})-[:HAS_ANSWER]->(ea:ExamAnswer)
            RETURN ea
            """, {"exam_id": exam_id}
        )
        exam_answers = [rec["ea"] for rec in ea_result]
        section_dict = {}
        for ea in exam_answers:
            q_result = session.run(
                """
                MATCH (q:Question {id: $qid})
                RETURN q LIMIT 1
                """, {"qid": ea["question_id"]}
            )
            q_record = q_result.single()
            if not q_record:
                continue
            q_obj = q_record["q"]
            sec = q_obj["section"]
            if sec not in section_dict:
                section_dict[sec] = {
                    "correct_count": 0,
                    "wrong_count": 0,
                    "sum_earned": 0,
                    "sum_possible": 0
                }
            if ea["points_earned"] == q_obj["points"]:
                section_dict[sec]["correct_count"] += 1
            else:
                section_dict[sec]["wrong_count"] += 1
            section_dict[sec]["sum_earned"] += ea["points_earned"]
            section_dict[sec]["sum_possible"] += q_obj["points"]
        sections_details = []
        for section_num in sorted(section_dict.keys()):
            data = section_dict[section_num]
            ds = data["correct_count"]
            ys = data["wrong_count"]
            sum_earned = data["sum_earned"]
            sum_possible = data["sum_possible"]
            if sum_possible > 0:
                notu_value = round((sum_earned / sum_possible) * 100, 2)
            else:
                notu_value = 0.0
            if section_num in stats_map:
                so_value = round(stats_map[section_num].get("section_percentage", 0), 2)
                oo_value = round(stats_map[section_num].get("section_percentage", 0), 2)
            else:
                so_value = 0.0
                oo_value = 0.0
            ort_value = round(current_user.get("score_avg", 0), 2)
            sec_result = SectionResult(
                section_number=section_num,
                correct_answers=ds,
                wrong_answers=ys,
                so=so_value,
                oo=oo_value,
                notu=notu_value,
                ort=ort_value
            )
            sections_details.append(sec_result)
        all_section_pass = True
        for sec in section_dict:
            earned = section_dict[sec]["sum_earned"]
            possible = section_dict[sec]["sum_possible"]
            section_score = (earned / possible) * 100 if possible > 0 else 0.0
            if section_score < pass_mark:
                all_section_pass = False
        total_earned = sum(section_dict[s]["sum_earned"] for s in section_dict)
        total_possible = sum(section_dict[s]["sum_possible"] for s in section_dict)
        final_score = round((total_earned / total_possible) * 100, 2) if total_possible > 0 else 0.0
        pass_fail = "passed" if (all_section_pass and (final_score >= pass_mark)) else "failed"
        questions_details = []
        for ea in exam_answers:
            q_result = session.run(
                """
                MATCH (q:Question {id: $qid})
                RETURN q LIMIT 1
                """, {"qid": ea["question_id"]}
            )
            q_record = q_result.single()
            if not q_record:
                continue
            q_obj = q_record["q"]
            choices_result = session.run(
                """
                MATCH (q:Question {id: $qid})-[:HAS_CHOICE]->(c:Choice)
                RETURN c
                """, {"qid": q_obj["id"]}
            )
            all_choices = [rec["c"] for rec in choices_result]
            correct_texts = []
            if q_obj["type"] == "ordering":
                sorted_choices = sorted(all_choices, key=lambda c: c.get("correct_position") if c.get("correct_position") is not None else 9999)
                correct_texts = [c["choice_text"] for c in sorted_choices if c.get("correct_position") is not None]
            elif q_obj["type"] in ["multiple_choice", "single_choice", "true_false"]:
                correct_texts = [c["choice_text"] for c in all_choices if c.get("is_correct")]
            ua_result = session.run(
                """
                MATCH (ea:ExamAnswer {id: $ea_id})-[r:CHOSE]->(c:Choice)
                RETURN collect(c.id) as selected
                """, {"ea_id": ea["id"]}
            )
            ua_record = ua_result.single()
            student_selected = ua_record["selected"] if ua_record and ua_record["selected"] else []
            student_answers_list = []
            for cid in student_selected:
                for c in all_choices:
                    if c["id"] == cid:
                        student_answers_list.append(c["choice_text"])
                        break
            if ea["points_earned"] == q_obj["points"]:
                status = "Correct"
            elif ea["points_earned"] > 0:
                status = "Partially Correct"
            else:
                status = "Wrong"
            question_detail = QuestionDetailModel(
                question_text=q_obj["question"],
                student_answers=student_answers_list,
                correct_answers=correct_texts,
                status=status,
                points_earned=ea["points_earned"],
                points_possible=q_obj["points"]
            )
            questions_details.append(question_detail)
        exam_detail = ExamDetailV2(
            start_time=format_datetime(exam["start_time"]),
            end_time=format_datetime(exam.get("end_time")) if exam.get("end_time") else None,
            pass_fail=pass_fail,
            sections_details=sections_details,
            questions_details=questions_details,
            exam_percentage=final_score
        )
        exam_details_list.append(exam_detail)
        total_exam_percentage += final_score
    overall_percentage = round(total_exam_percentage / len(exam_details_list), 2)
    return {
        "student_number": current_user.get("okul_no"),
        "class_name": current_user["class_name"],
        "attempts": current_user.get("attempts", 0),
        "exams": exam_details_list,
        "overall_percentage": overall_percentage
    }
