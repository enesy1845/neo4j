# routers/stats.py
from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session
from typing import Dict, List
from tools.database import get_db
from tools.models import User, Statistics
from tools.token_generator import get_current_user

router = APIRouter()

@router.get("/", summary="View advanced statistics")
def view_statistics(db: Session = Depends(get_db), current_user: User = Depends(get_current_user)):

    # Sadece "teacher" veya "admin" görebilsin
    if current_user.role not in ["teacher", "admin"]:
        raise HTTPException(status_code=403, detail="Only teachers or admins can view statistics.")

    school_id = current_user.school_id
    query = db.query(Statistics).filter(Statistics.school_id == school_id)

    # Eğer teacher ise, sadece registered_section (CSV) içindeki section_number'ları ve
    # class_name (CSV) içindeki sınıfları filtreleyelim
    if current_user.role == "teacher":
        if current_user.registered_section:
            teacher_sections = [int(x.strip()) for x in current_user.registered_section.split(",") if x.strip()]
            query = query.filter(Statistics.section_number.in_(teacher_sections))
        teacher_class_list = [c.strip() for c in current_user.class_name.split(",")]
        query = query.filter(Statistics.class_name.in_(teacher_class_list))

    all_stats = query.all()
    if not all_stats:
        return {
            "per_class": {},
            "school_summary": []
        }

    # 1) per_class
    per_class = {}

    # set() toplamak için
    class_names = set()
    section_numbers = set()
    for st in all_stats:
        class_names.add(st.class_name)
        section_numbers.add(st.section_number)

    tmp_per_class = {}
    for cls in class_names:
        tmp_per_class[cls] = {}

    for st in all_stats:
        c = st.class_name
        sec = st.section_number
        tmp_per_class[c][sec] = (st.correct_questions, st.wrong_questions)

    # dict'ten list'e dönüştür
    for cls in tmp_per_class:
        items_list = []
        for sec in sorted(tmp_per_class[cls].keys()):
            ds, ys = tmp_per_class[cls][sec]
            items_list.append({
                "section_number": sec,
                "correct_answers": ds,
                "wrong_answers": ys
            })
        per_class[cls] = items_list

    # 2) school_summary
    # Tekrar section bazında toplayacağız
    # section_map = { sec: { ds_total, ys_total, classes: {} } }
    section_map = {}
    for sec in section_numbers:
        section_map[sec] = {
            "correct_answers_total": 0,
            "wrong_answers_total": 0,
            "classes": {}
        }

    for st in all_stats:
        sec = st.section_number
        ds = st.correct_questions
        ys = st.wrong_questions
        cls = st.class_name

        section_map[sec]["correct_answers_total"] += ds
        section_map[sec]["wrong_answers_total"] += ys

        total_q = ds + ys
        percent = 0.0
        if total_q != 0:
            percent = round((ds / total_q) * 100, 2)
        section_map[sec]["classes"][cls] = percent

    school_summary = []
    for sec in sorted(section_map.keys()):
        ds_total = section_map[sec]["correct_answers_total"]
        ys_total = section_map[sec]["wrong_answers_total"]
        total_q = ds_total + ys_total
        sn_basarisi = 0.0
        if total_q > 0:
            sn_basarisi = round((ds_total / total_q) * 100, 2)

        school_summary.append({
            "section_number": sec,
            "correct_answers_total": ds_total,
            "wrong_answers_total": ys_total,
            "sn_basarisi": sn_basarisi,
            "classes": section_map[sec]["classes"]
        })

    return {
        "per_class": per_class,
        "school_summary": school_summary
}
