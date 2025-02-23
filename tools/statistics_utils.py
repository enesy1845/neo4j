# tools/statistics_utils.py
def update_statistics(session, school_id, class_name, section_scores: dict, section_correct_wrong: dict):
    """
    section_scores: { section_number: [sum_earned, sum_possible], ... }
    section_correct_wrong: { section_number: [correct_count, wrong_count], ... }
    Her bölüm için istatistik düğümü oluşturulur veya güncellenir.
    """
    subject_mapping = {1: "Math", 2: "English", 3: "Science", 4: "History"}
    for sec in range(1, 5):
        sum_earned, sum_possible = section_scores.get(sec, [0, 0])
        section_percentage = round((sum_earned / sum_possible) * 100, 2) if sum_possible > 0 else 0
        session.run("""
        MERGE (st:Statistics {school_id: $school_id, class_name: $class_name, section_number: $section_number})
        SET st.correct_questions = coalesce(st.correct_questions, 0) + $correct,
            st.wrong_questions = coalesce(st.wrong_questions, 0) + $wrong,
            st.section_percentage = $section_percentage,
            st.exam_takers = coalesce(st.exam_takers, 0) + 1,
            st.section_name = $section_name
        """, {
            "school_id": school_id,
            "class_name": class_name,
            "section_number": sec,
            "correct": section_correct_wrong.get(sec, [0, 0])[0],
            "wrong": section_correct_wrong.get(sec, [0, 0])[1],
            "section_percentage": section_percentage,
            "section_name": subject_mapping.get(sec, f"Section {sec}")
        })
