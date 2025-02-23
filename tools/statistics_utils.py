# tools/statistics_utils.py
def update_statistics(session, school_id, class_name, section_scores: dict, section_correct_wrong: dict):
    """
    section_scores: { section_number: [sum_earned, sum_possible], ... }
    section_correct_wrong: { section_number: [correct_count, wrong_count], ... }
    Her bölüm için istatistik düğümü oluşturulur veya güncellenir.
    """
    for sec in range(1, 5):
        session.run("""
        MERGE (st:Statistics {school_id: $school_id, class_name: $class_name, section_number: $section_number})
        SET st.correct_questions = coalesce(st.correct_questions, 0) + $correct,
            st.wrong_questions = coalesce(st.wrong_questions, 0) + $wrong,
            st.average_score = coalesce(st.average_score, 0), 
            st.section_percentage = coalesce(st.section_percentage, 0),
            st.exam_takers = coalesce(st.exam_takers, 0) + 1
        """, {
            "school_id": school_id,
            "class_name": class_name,
            "section_number": sec,
            "correct": section_correct_wrong.get(sec, [0, 0])[0],
            "wrong": section_correct_wrong.get(sec, [0, 0])[1]
        })
