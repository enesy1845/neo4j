# routers/stats.py
from fastapi import APIRouter, Depends, HTTPException
from tools.database import get_db
from tools.token_generator import get_current_user

router = APIRouter()

@router.get("/", summary="View advanced statistics")
def view_statistics(session = Depends(get_db), current_user = Depends(get_current_user)):
    subject_mapping = {1: "Math", 2: "English", 3: "Science", 4: "History"}
    if current_user["role"] == "teacher" and current_user.get("registered_section"):
        try:
            teacher_sections = [int(x.strip()) for x in current_user["registered_section"].split(",") if x.strip().isdigit()]
        except:
            teacher_sections = []
        teacher_class = current_user["class_name"]
        # Teacher's own class statistics
        class_stats_result = session.run("""
            MATCH (st:Statistics {class_name: $class_name})
            WHERE st.section_number IN $sections
            RETURN st
        """, {"class_name": teacher_class, "sections": teacher_sections})
        teacher_class_stats = []
        for record in class_stats_result:
            st = record["st"]
            teacher_class_stats.append({
                "section_number": st["section_number"],
                "section_name": subject_mapping.get(st["section_number"], f"Section {st['section_number']}"),
                "correct_answers": st["correct_questions"],
                "wrong_answers": st["wrong_questions"],
                "exam_takers": st["exam_takers"]
            })
        # School-wide summary statistics (aggregated from all classes)
        school_stats_result = session.run("""
            MATCH (st:Statistics {school_id: $school_id})
            WHERE st.section_number IN $sections
            RETURN st
        """, {"school_id": current_user.get("school_id"), "sections": teacher_sections})
        school_summary_dict = {}
        for record in school_stats_result:
            st = record["st"]
            sec = st["section_number"]
            if sec not in school_summary_dict:
                school_summary_dict[sec] = {
                    "section_number": sec,
                    "section_name": subject_mapping.get(sec, f"Section {sec}"),
                    "correct_answers_total": 0,
                    "wrong_answers_total": 0,
                    "exam_takers": 0
                }
            school_summary_dict[sec]["correct_answers_total"] += st["correct_questions"]
            school_summary_dict[sec]["wrong_answers_total"] += st["wrong_questions"]
            school_summary_dict[sec]["exam_takers"] += st["exam_takers"]
        school_summary = list(school_summary_dict.values())
        # Per-question statistics for each section:
        question_stats = {}
        for sec in teacher_sections:
            qs_result = session.run("""
                MATCH (q:Question {section: $section})
                OPTIONAL MATCH (q)<-[r:FOR_QUESTION]-(ea:ExamAnswer)
                RETURN q.question AS question_text, 
                       count(CASE WHEN ea.points_earned = q.points THEN 1 ELSE null END) AS correct_count,
                       count(CASE WHEN ea.points_earned = 0 THEN 1 ELSE null END) AS wrong_count
            """, {"section": sec})
            question_stats[sec] = [record for record in qs_result]
        return {
            "teacher_class_stats": teacher_class_stats,
            "school_summary": school_summary,
            "question_stats": question_stats
        }
    else:
        result = session.run("""
            MATCH (st:Statistics)
            RETURN st
        """)
        per_class = {}
        subject_mapping = {1: "Math", 2: "English", 3: "Science", 4: "History"}
        for record in result:
            st = record["st"]
            cls = st["class_name"]
            if cls not in per_class:
                per_class[cls] = []
            per_class[cls].append({
                "section_number": st["section_number"],
                "section_name": subject_mapping.get(st["section_number"], f"Section {st['section_number']}"),
                "correct_answers": st["correct_questions"],
                "wrong_answers": st["wrong_questions"],
                "exam_takers": st["exam_takers"]
            })
        return {
            "per_class": per_class,
            "school_summary": [],
            "question_stats": {}
        }
