# routers/results.py
from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session
from typing import List, Dict
from pydantic import BaseModel
from tools.database import get_db
from tools.models import User, Exam, ExamAnswer, Question, QuestionChoice, Statistics
from tools.token_generator import get_current_user

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

class ExamResultV2Response(BaseModel):
    student_number: int | None
    class_name: str
    attempts: int
    exams: List[ExamDetailV2]

@router.get("/results_v2", response_model=ExamResultV2Response, summary="View your exam results (table style)")
def view_exam_results_v2(db: Session = Depends(get_db), current_user: User = Depends(get_current_user)):
    if current_user.role != "student":
        raise HTTPException(status_code=403, detail="Only students can view their exam results.")
    # Only include exams that have been submitted (i.e. end_time is not None)
    exams = db.query(Exam).filter(Exam.user_id == current_user.user_id, Exam.end_time.isnot(None)).order_by(Exam.start_time.asc()).all()
    if not exams:
        return {
            "student_number": current_user.okul_no,
            "class_name": current_user.class_name,
            "attempts": current_user.attempts,
            "exams": []
        }
    pass_mark = 75.0
    exam_details_list = []

    # Okul + Class için Statistic tablo
    stats_map = {}
    all_stats = db.query(Statistics).filter(
        Statistics.school_id == current_user.school_id,
        Statistics.class_name == current_user.class_name
    ).all()
    for st in all_stats:
        stats_map[st.section_number] = st

    for exam in exams:
        # SECTION DETAILS
        section_dict = {}
        exam_answers = db.query(ExamAnswer).filter(ExamAnswer.exam_id == exam.exam_id).all()
        for ans in exam_answers:
            q_obj = db.query(Question).filter(Question.id == ans.question_id).first()
            if not q_obj:
                continue
            sec = q_obj.section
            if sec not in section_dict:
                section_dict[sec] = {
                    "correct_count": 0,
                    "wrong_count": 0,
                    "sum_earned": 0,
                    "sum_possible": 0
                }
            if ans.points_earned == q_obj.points:
                section_dict[sec]["correct_count"] += 1
            else:
                section_dict[sec]["wrong_count"] += 1
            section_dict[sec]["sum_earned"] += ans.points_earned
            section_dict[sec]["sum_possible"] += q_obj.points

        sections_details = []
        for section_num in sorted(section_dict.keys()):
            stats_row = stats_map.get(section_num, None)
            ds = section_dict[section_num]["correct_count"]
            ys = section_dict[section_num]["wrong_count"]
            sum_earned = section_dict[section_num]["sum_earned"]
            sum_possible = section_dict[section_num]["sum_possible"]
            if sum_possible > 0:
                notu_value = round((sum_earned / sum_possible) * 100, 2)
            else:
                notu_value = 0.0

            if stats_row:
                so_value = round(stats_row.section_percentage, 2)
                oo_value = round(stats_row.section_percentage, 2)
            else:
                so_value = 0.0
                oo_value = 0.0
            ort_value = round(current_user.score_avg, 2)

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

        # PASS/FAIL
        pass_fail = "geçti"
        for s in sections_details:
            if s.notu < pass_mark:
                pass_fail = "geçemedi"
                break

        # QUESTION DETAILS
        questions_details = []
        # Tüm examAnswer -> question -> user choices -> check correct
        for ans in exam_answers:
            q_obj = db.query(Question).filter(Question.id == ans.question_id).first()
            if not q_obj:
                continue
            # Puan
            points_earned = ans.points_earned
            points_possible = q_obj.points

            # Doğru Cevap(lar)
            all_choices = db.query(QuestionChoice).filter(QuestionChoice.question_id == q_obj.id).all()
            correct_texts = []
            if q_obj.type == "ordering":
                # ordering -> correct_position sırasına göre
                sorted_choices = sorted(all_choices, key=lambda c: c.correct_position if c.correct_position is not None else 9999)
                correct_texts = [c.choice_text for c in sorted_choices if c.correct_position is not None]
            elif q_obj.type in ["multiple_choice", "single_choice", "true_false"]:
                correct_texts = [c.choice_text for c in all_choices if c.is_correct]

            # Student Cevap(lar)
            student_selected = [uc.question_choice_id for uc in ans.user_choices]
            # O id'lerden choice_text bulalım
            student_answers_list = []
            for cid in student_selected:
                cc = next((x for x in all_choices if x.id == cid), None)
                if cc:
                    student_answers_list.append(cc.choice_text)

            # partial / correct / wrong
            if points_earned == points_possible:
                status = "Correct"
            elif points_earned > 0:
                status = "Partially Correct"
            else:
                status = "Wrong"

            question_details = QuestionDetailModel(
                question_text=q_obj.question,
                student_answers=student_answers_list,
                correct_answers=correct_texts,
                status=status,
                points_earned=points_earned,
                points_possible=points_possible
            )
            questions_details.append(question_details)

        exam_detail = ExamDetailV2(
            start_time=exam.start_time.isoformat(),
            end_time=exam.end_time.isoformat() if exam.end_time else None,
            pass_fail=pass_fail,
            sections_details=sections_details,
            questions_details=questions_details
        )
        exam_details_list.append(exam_detail)

    return {
        "student_number": current_user.okul_no,
        "class_name": current_user.class_name,
        "attempts": current_user.attempts,
        "exams": exam_details_list
    }
