# tools/statistics_utils.py

from sqlalchemy.orm import Session
from tools.models import Statistics

def update_statistics(db: Session, school_id, class_name,
                      section_scores: dict,
                      section_correct_wrong: dict):
    """
    section_scores => { 1: [sum_earned, sum_possible], ... }  # puan hesapları
    section_correct_wrong => { 1: [correct_count, wrong_count], ... }
    """
    for sec, arr in section_scores.items():
        earned, possible = arr
        # puan bazlı average_score vs. hesaplamaya devam edebilirsiniz (isterseniz).
        # ama "doğru" ve "yanlış" sayısı section_correct_wrong'tan gelecek.
        
        correct_count = section_correct_wrong[sec][0]
        wrong_count = section_correct_wrong[sec][1]

        stat = db.query(Statistics).filter_by(
            school_id=school_id,
            class_name=class_name,
            section_number=sec
        ).first()

        if not stat:
            stat = Statistics(
                school_id=school_id,
                class_name=class_name,
                section_number=sec,
                correct_questions=0,
                wrong_questions=0,
                average_score=0.0,
                section_percentage=0.0
            )
            db.add(stat)
            db.commit()
            db.refresh(stat)

        # Artık tam doğru ise correct_questions += correct_count
        stat.correct_questions += correct_count
        stat.wrong_questions += wrong_count

        # İsterseniz average_score güncellemesine devam:
        new_score = 0.0
        if possible > 0:
            new_score = (earned / possible)*100
        
        old_avg = stat.average_score
        if old_avg == 0.0:
            old_avg = 50.0
        
        stat.average_score = (old_avg + new_score) / 2

        c = stat.correct_questions
        w = stat.wrong_questions
        total_q = c + w
        if total_q > 0:
            stat.section_percentage = (c / total_q)*100
        else:
            stat.section_percentage = 0.0

        db.commit()