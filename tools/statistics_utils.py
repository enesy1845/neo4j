# tools/statistics_utils.py

from sqlalchemy.orm import Session
from tools.models import Statistics

def update_statistics(db: Session, school_id, class_name, section_scores):
    """
    section_scores => { 1: [earned, possible], 2: [earned, possible], ... }
    We update the 'Statistics' table. For each section => correct_questions, wrong_questions
    but we also do average_score => (old + new)/2 mantığı,
    eğer old =0 => 50 ile başla

    'Statistics' tablosunda:
      - correct_questions
      - wrong_questions
      - average_score (daha önce 0 default)
      - section_percentage (daha önce 0 default)
    """
    for sec, arr in section_scores.items():
        earned, possible = arr
        ds = int(earned)  # 'doğru sayısı' demek değil ama basit mantık
        # istersen "ds" => round(earned) de diyebilirsin
        # wrong => possible-earned
        # ama question bazında 1 question = 1 dogru + x yanlis diyeceksin. 
        # Yine de, basit kalması için ds=earned, ys=possible-earned
        ys = int(possible - earned)
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

        # update ds, ys
        stat.correct_questions += ds
        stat.wrong_questions += ys

        # section_score = (earned/possible)*100
        if possible > 0:
            new_score = (earned / possible)*100
        else:
            new_score = 0.0

        # average_score => eğer old=0 => 50'den başla
        old_avg = stat.average_score
        if old_avg == 0.0:
            old_avg = 50.0  # senin istediğin "başlangıç 50%" kuralı

        stat.average_score = (old_avg + new_score) / 2

        # section_percentage => correct_questions / (correct+wrong) *100
        c = stat.correct_questions
        w = stat.wrong_questions
        if (c + w) > 0:
            stat.section_percentage = (c / (c + w)) * 100
        else:
            stat.section_percentage = 0.0

        db.commit()
