# tools/statistics_utils.py
from sqlalchemy.orm import Session
from tools.models import Statistics, Question

def update_statistics(db: Session, school_id, class_name, section_correct, section_wrong, section_scores):
    """
    Her section için correct_questions ve wrong_questions birikimli arttırılır.
    Ardından section_percentage, (correct_questions / toplam soru sayısı) * 100 şeklinde hesaplanır.
    average_score = section_percentage ile aynı tutulur (isteğe göre farklı hesaplanabilir).
    """

    for sec in range(1, 5):
        stat = db.query(Statistics).filter(
            Statistics.school_id == school_id,
            Statistics.class_name == class_name,
            Statistics.section_number == sec
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

        # Güncelle
        stat.correct_questions += section_correct[sec]
        stat.wrong_questions += section_wrong[sec]

        total_ans_for_section = stat.correct_questions + stat.wrong_questions
        if total_ans_for_section > 0:
            section_percentage = (stat.correct_questions / total_ans_for_section) * 100
        else:
            section_percentage = 0.0

        # average_score'ı da bu şekilde güncelleyebiliriz
        stat.section_percentage = section_percentage
        stat.average_score = section_percentage

        db.commit()
