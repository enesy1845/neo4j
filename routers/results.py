# routers/results.py
from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session
from typing import List, Dict
from pydantic import BaseModel
from tools.database import get_db
from tools.models import User, Exam, ExamAnswer, Question, QuestionChoice, Statistics
from tools.token_generator import get_current_user

router = APIRouter()

class SectionResult(BaseModel):
    section_number: int
    ds: int  # dogru sayisi
    ys: int  # yanlis sayisi
    so: float  # sinif ortalamasi (section_percentage veya average_score'dan)
    oo: float  # okul ortalamasi (simdilik ayni, ornegin)
    notu: float  # bu section'da ogrencinin puani (0..100)
    ort: float   # ogrencinin genel ortalamasi (score_avg)

class ExamDetailV2(BaseModel):
    exam_id: str
    start_time: str
    end_time: str | None
    pass_fail: str
    sections_details: List[SectionResult]

class ExamResultV2Response(BaseModel):
    # ID, sinifi, vs. tablo basligi icin
    student_id: str
    class_name: str
    attempts: int
    exams: List[ExamDetailV2]

@router.get("/results_v2", response_model=ExamResultV2Response, summary="View your exam results (table style)")
def view_exam_results_v2(
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    """
    Yeni versiyon: her exam için section bazında DS, YS, SO, OO, Notu, Ort...
    pass_fail'e göre 'geçti' veya 'gecemedi'.
    """

    if current_user.role != "student":
        raise HTTPException(status_code=403, detail="Only students can view their exam results.")

    exams = db.query(Exam).filter(Exam.user_id == current_user.user_id).order_by(Exam.start_time.asc()).all()
    if not exams:
        # Hic exam yoksa bos donebiliriz
        return {
            "student_id": str(current_user.user_id),
            "class_name": current_user.class_name,
            "attempts": current_user.attempts,
            "exams": []
        }

    # Okul+class icin statistic tablo verilerine ulasalim (so, oo)
    # Tek tek cekecegiz: school_id + class_name + section
    stats_map: Dict[int, Statistics] = {}
    # ornegin key=section_number -> stat obj
    all_stats = db.query(Statistics).filter(
        Statistics.school_id == current_user.school_id,
        Statistics.class_name == current_user.class_name
    ).all()
    for st in all_stats:
        stats_map[st.section_number] = st

    pass_mark = 75.0  # her bolumden en az 60 puan

    exam_details_list = []

    for exam in exams:
        # Bu exam icin "section -> (correct_count, wrong_count, sum_points_earned, sum_points_possible)"
        section_dict = {}

        # Tüm examAnswer'ları cekip question.section bazında grupluyoruz
        exam_answers = db.query(ExamAnswer).filter(ExamAnswer.exam_id == exam.exam_id).all()
        for ans in exam_answers:
            question_obj = db.query(Question).filter(Question.id == ans.question_id).first()
            if not question_obj:
                continue
            sec = question_obj.section
            if sec not in section_dict:
                section_dict[sec] = {
                    "correct_count": 0,
                    "wrong_count": 0,
                    "sum_earned": 0,
                    "sum_possible": 0
                }

            # dogru mu yanlis mi? Basit logic: if ans.points_earned == question_obj.points => dogru
            # cünkü tam puan aldiysa dogru
            if ans.points_earned == question_obj.points:
                section_dict[sec]["correct_count"] += 1
            else:
                section_dict[sec]["wrong_count"] += 1

            section_dict[sec]["sum_earned"] += ans.points_earned
            section_dict[sec]["sum_possible"] += question_obj.points

        # Her section icin DS, YS, so, oo, notu, ort
        sections_details = []
        # 1..4 olabilir. Hangilerini cozmus?
        # Veya dynamic: section_dict.keys()
        # Fakat 1..4 sabit seklinde istersen...
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
                # so'yu stats_row.section_percentage
                so_value = round(stats_row.section_percentage, 2)
                # oo'yu da ayni sekilde (eger ayri okulla calisacaksak, ek bir logic lazim)
                # ornek: average_score filan
                oo_value = round(stats_row.section_percentage, 2)
            else:
                so_value = 0.0
                oo_value = 0.0

            # ort => ogrencinin "score_avg" (tum sinavlar ortalamasi)
            # istersen bu exam'e ozel ortalama da yapabilirsin. Simdilik user.score_avg
            ort_value = round(current_user.score_avg, 2)

            sec_result = SectionResult(
                section_number=section_num,
                ds=ds,
                ys=ys,
                so=so_value,
                oo=oo_value,
                notu=notu_value,
                ort=ort_value
            )
            sections_details.append(sec_result)

        # pass/fail: eger tum section'larin "notu_value" >= pass_mark ise "geçti" else "gecemedi"
        pass_fail = "geçti"
        for s in sections_details:
            if s.notu < pass_mark:
                pass_fail = "geçemedi"
                break

        exam_detail = ExamDetailV2(
            exam_id=str(exam.exam_id),
            start_time=exam.start_time.isoformat(),
            end_time=exam.end_time.isoformat() if exam.end_time else None,
            pass_fail=pass_fail,
            sections_details=sections_details
        )
        exam_details_list.append(exam_detail)

    return {
        "student_id": str(current_user.user_id),
        "class_name": current_user.class_name,
        "attempts": current_user.attempts,
        "exams": exam_details_list
    }
