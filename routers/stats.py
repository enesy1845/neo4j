# routers/stats.py
from fastapi import APIRouter, Depends, HTTPException
from tools.database import get_db
from tools.token_generator import get_current_user

router = APIRouter()

@router.get("/", summary="View advanced statistics")
def view_statistics(session = Depends(get_db), current_user = Depends(get_current_user)):
    if current_user["role"] == "teacher" and current_user.get("registered_section"):
        teacher_sections = [int(x.strip()) for x in current_user["registered_section"].split(",") if x.strip().isdigit()]
        teacher_class = current_user["class_name"]
        result = session.run("""
        MATCH (st:Statistics {class_name: $class_name})
        WHERE st.section_number IN $sections
        RETURN st
        """, {"class_name": teacher_class, "sections": teacher_sections})
        per_class = {}
        school_summary = []
        stats_list = [record["st"] for record in result]
        for st in stats_list:
            if teacher_class not in per_class:
                per_class[teacher_class] = []
            per_class[teacher_class].append({
                "section_number": st["section_number"],
                "section_name": st.get("section_name", f"Section {st['section_number']}"),
                "correct_answers": st["correct_questions"],
                "wrong_answers": st["wrong_questions"],
                "exam_takers": st["exam_takers"]
            })
            school_summary.append({
                "section_number": st["section_number"],
                "section_name": st.get("section_name", f"Section {st['section_number']}"),
                "correct_answers_total": st["correct_questions"],
                "wrong_answers_total": st["wrong_questions"],
                "exam_takers": st["exam_takers"],
                "sn_basarisi": round((st["correct_questions"]/(st["correct_questions"]+st["wrong_questions"]))*100,2) if (st["correct_questions"]+st["wrong_questions"])>0 else 0,
                "classes": {}
            })
        return {
            "per_class": per_class,
            "school_summary": school_summary,
            "question_stats": []
        }
    else:
        result = session.run("""
        MATCH (st:Statistics)
        RETURN st
        """)
        per_class = {}
        for record in result:
            st = record["st"]
            cls = st["class_name"]
            if cls not in per_class:
                per_class[cls] = []
            per_class[cls].append({
                "section_number": st["section_number"],
                "section_name": st.get("section_name", f"Section {st['section_number']}"),
                "correct_answers": st["correct_questions"],
                "wrong_answers": st["wrong_questions"],
                "exam_takers": st["exam_takers"]
            })
        return {
            "per_class": per_class,
            "school_summary": [],
            "question_stats": []
        }
