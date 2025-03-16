# routers/stats.py
from fastapi import APIRouter, Depends, HTTPException
from tools.database import get_db
from tools.token_generator import get_current_user
router = APIRouter()
subject_mapping = {1: "Math", 2: "English", 3: "Science", 4: "History"}
@router.get("/", summary="View advanced statistics")
def view_statistics(session = Depends(get_db), current_user = Depends(get_current_user)):
    if current_user["role"] == "teacher":
        teacher_class = current_user["class_name"]
        teacher_sections = []
        if current_user.get("registered_section"):
            try:
                teacher_sections = [int(x.strip()) for x in current_user["registered_section"].split(",") if x.strip().isdigit()]
            except:
                teacher_sections = []
        if not teacher_sections:
            teacher_sections = [1, 2, 3, 4]
        # Teacher's own class statistics
        class_stats_result = session.run("""
        MATCH (st:Statistics {class_name: $class_name})
        WHERE st.section_number IN $sections
        RETURN st
        """, {"class_name": teacher_class, "sections": teacher_sections})
        teacher_class_stats = []
        for record in class_stats_result:
            st = record["st"]
            total = st["correct_questions"] + st["wrong_questions"]
            teacher_class_stats.append({
                "section_number": st["section_number"],
                "section_name": subject_mapping.get(st["section_number"], f"Section {st['section_number']}"),
                "correct_answers": st["correct_questions"],
                "wrong_answers": st["wrong_questions"],
                "exam_takers": st["exam_takers"],
                "success_rate": round((st["correct_questions"]/total)*100, 2) if total > 0 else 0
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
        school_summary = []
        for sec, data in school_summary_dict.items():
            total = data["correct_answers_total"] + data["wrong_answers_total"]
            data["success_rate"] = round((data["correct_answers_total"]/total)*100, 2) if total > 0 else 0
            school_summary.append(data)
        # Per-question statistics for each section:
        question_stats = {}
        for sec in teacher_sections:
            qs_result = session.run("""
            MATCH (q:Question {section: $section})
            OPTIONAL MATCH (q)<-[r:FOR_QUESTION]-(ea:ExamAnswer)
            RETURN q.question AS question_text,
            coalesce(count(CASE WHEN ea.points_earned = q.points THEN 1 ELSE null END), 0) AS correct_count,
            coalesce(count(CASE WHEN ea.points_earned = 0 THEN 1 ELSE null END), 0) AS wrong_count
            """, {"section": sec})
            qs = [record for record in qs_result]
            # Fallback: if no questions are returned, still return empty rows for each question
            if not qs:
                qs_result = session.run("""
                MATCH (q:Question {section: $section})
                RETURN q.question AS question_text, 0 AS correct_count, 0 AS wrong_count
                """, {"section": sec})
                qs = [record for record in qs_result]
            question_stats[sec] = qs
        return {
            "teacher_class_stats": teacher_class_stats,
            "school_summary": school_summary,
            "question_stats": question_stats
        }
    elif current_user["role"] == "admin":
        result = session.run("""
        MATCH (st:Statistics)
        RETURN st
        """)
        per_class = {}
        overall_summary_dict = {}
        for record in result:
            st = record["st"]
            cls = st["class_name"]
            if cls not in per_class:
                per_class[cls] = []
            total = st["correct_questions"] + st["wrong_questions"]
            stat_entry = {
                "section_number": st["section_number"],
                "section_name": subject_mapping.get(st["section_number"], f"Section {st['section_number']}"),
                "correct_answers": st["correct_questions"],
                "wrong_answers": st["wrong_questions"],
                "exam_takers": st["exam_takers"],
                "success_rate": round((st["correct_questions"]/total)*100, 2) if total > 0 else 0
            }
            per_class[cls].append(stat_entry)
            # Aggregate overall summary by section
            sec = st["section_number"]
            if sec not in overall_summary_dict:
                overall_summary_dict[sec] = {
                    "section_number": sec,
                    "section_name": subject_mapping.get(sec, f"Section {sec}"),
                    "correct_answers_total": 0,
                    "wrong_answers_total": 0,
                    "exam_takers": 0
                }
            overall_summary_dict[sec]["correct_answers_total"] += st["correct_questions"]
            overall_summary_dict[sec]["wrong_answers_total"] += st["wrong_questions"]
            overall_summary_dict[sec]["exam_takers"] += st["exam_takers"]
        overall_summary = []
        for sec, data in overall_summary_dict.items():
            total = data["correct_answers_total"] + data["wrong_answers_total"]
            data["success_rate"] = round((data["correct_answers_total"]/total)*100, 2) if total > 0 else 0
            overall_summary.append(data)
        return {
            "per_class": per_class,
            "overall_summary": overall_summary,
            "question_stats": {}  # Admin view does not include per-question stats
        }
    else:
        return {
            "per_class": {},
            "overall_summary": [],
            "question_stats": {}
        }
