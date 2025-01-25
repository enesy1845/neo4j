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
    """
    Genişletilmiş: Her sınıf ve section için DS/YS,
    ayrıca okul özeti tablosu da döner.

    Dönüş formatı:
    {
      "per_class": {
        "7-a": [
          { "section_number": 1, "ds": X, "ys": Y },
          { "section_number": 2, "ds": X, "ys": Y }
        ],
        "7-b": [...],
      },
      "school_summary": [
        {
          "section_number": 1,
          "ds_total": 35,
          "ys_total": 18,
          "sn_basarisi": 50,
          "classes": {
            "7-a": 65,
            "7-b": 45,
            ...
          }
        },
        ...
      ]
    }
    """
    # Sadece "teacher" veya "admin" görebilsin (eski hal)
    if current_user.role not in ["teacher", "admin"]:
        raise HTTPException(status_code=403, detail="Only teachers or admins can view statistics.")

    # Teacher => kendi school_id'sini al, oradaki tüm class'ların stats'ini görebilir
    school_id = current_user.school_id

    # Tüm stats'ları çek
    all_stats = db.query(Statistics).filter(Statistics.school_id == school_id).all()
    if not all_stats:
        return {
            "per_class": {},
            "school_summary": []
        }

    # 1) per_class = { class_name: [ { section_number, ds, ys }, ... ] }
    #    ds, ys => correct_questions, wrong_questions
    # 2) school_summary => [ { section_number, ds_total, ys_total, sn_basarisi, classes: { "7-a": 65, "7-b": ...} } ]

    # (A) per_class
    per_class = {}
    # { "7-a": {1: {"ds":..., "ys":...}, 2:... }, "7-b": {...} }

    # (B) overall: her section için TUM class'ların ds/ys toplanacak
    # Ayrıca her class'ın section yüzdesi (ds/(ds+ys))*100
    # Bunu "classes" dict'ine koyacağız.

    # 1) Tüm class_name'leri toplayacağız
    # 2) Tüm section_number'ları da
    # 3) Per section => ds_total, ys_total
    # 4) Per section + per class => ds, ys -> orandan "??"

    class_names = set()
    section_numbers = set()

    for st in all_stats:
        class_names.add(st.class_name)
        section_numbers.add(st.section_number)

    # A) per_class doldur
    # Basitçe, st.correct_questions => ds, st.wrong_questions => ys
    # Bir teacher, "registered_section" vs. => ama senin istediğin tablo "birden çok sınıf" diyorsan
    # admin benzeri bir bakış oluyor. Biz gene de hepsini alalım.

    # per_class -> { "7-a": { 1: (ds,ys), 2: (ds,ys) }, "7-b": {...} }
    tmp_per_class = {}
    for cls in class_names:
        tmp_per_class[cls] = {}

    for st in all_stats:
        c = st.class_name
        sec = st.section_number
        ds = st.correct_questions
        ys = st.wrong_questions
        tmp_per_class[c][sec] = (ds, ys)

    # Artık dict'ten list'e dönüştürelim
    # "7-a": [ {section_number=1, ds=..., ys=...}, {section_number=2, ...} ]
    for cls in tmp_per_class:
        items_list = []
        for sec in sorted(tmp_per_class[cls].keys()):
            ds, ys = tmp_per_class[cls][sec]
            items_list.append({
                "section_number": sec,
                "ds": ds,
                "ys": ys
            })
        per_class[cls] = items_list

    # B) school_summary
    # section -> { ds_total, ys_total, classes: { "7-a": <some %>, "7-b":... } }
    # or "7-a" = st.correct_questions / (st.correct + st.wrong)*100 ?

    # 1) "ds_total" => sum of ds across all classes
    #    "ys_total" => sum of ys across all classes
    #    "sn_basarisi" => or (ds_total / (ds_total+ys_total))*100 ?

    # "classes" => { "7-a": <some %> } => st.correct/(st.correct+st.wrong)*100
    # Tüm stats'ı section bazında grupluyoruz.
    section_map = {}
    # section_map[sec]["ds_total"] = ...
    # section_map[sec]["ys_total"] = ...
    # section_map[sec]["classes"] = { "7-a": X, "7-b": Y, ... }

    for sec in section_numbers:
        section_map[sec] = {
            "ds_total": 0,
            "ys_total": 0,
            "classes": {}
        }

    # Tekrar all_stats üzerinden -> her row: ds, ys -> classes
    for st in all_stats:
        sec = st.section_number
        ds = st.correct_questions
        ys = st.wrong_questions
        cls = st.class_name

        # ekle totals
        section_map[sec]["ds_total"] += ds
        section_map[sec]["ys_total"] += ys

        # ekle classes oransal
        total_q = ds + ys
        if total_q == 0:
            percent = 0.0
        else:
            percent = round((ds / total_q) * 100, 2)
        section_map[sec]["classes"][cls] = percent

    # simdi "sn_basarisi" => ds_total/(ds_total+ys_total)*100
    # son final list: [ {section_number, ds_total, ys_total, sn_basarisi, classes:{ "7-a":..., "7-b":... } } ]
    school_summary = []
    for sec in sorted(section_map.keys()):
        ds_total = section_map[sec]["ds_total"]
        ys_total = section_map[sec]["ys_total"]
        total_q = ds_total + ys_total
        if total_q == 0:
            sn_basarisi = 0.0
        else:
            sn_basarisi = round((ds_total / total_q) * 100, 2)

        school_summary.append({
            "section_number": sec,
            "ds_total": ds_total,
            "ys_total": ys_total,
            "sn_basarisi": sn_basarisi,
            "classes": section_map[sec]["classes"]  # dict of {class_name: percent}
        })

    return {
        "per_class": per_class,
        "school_summary": school_summary
    }
