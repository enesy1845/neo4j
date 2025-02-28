def update_statistics(session, school_id, class_name, section_scores: dict, section_correct_wrong: dict, attempt_number):
    """
    Her bölüm için istatistik düğümü oluşturulur veya güncellenir.
    Ek olarak, attempt_number bilgisine göre ilk ve ikinci sınav yüzdeleri ayrı tutulur.
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
            st.section_name = $section_name,
            st.success_rate = CASE WHEN ($correct + $wrong) > 0 THEN round(($correct * 1.0 / ($correct + $wrong)) * 100, 2) ELSE 0 END
        """, {
            "school_id": school_id,
            "class_name": class_name,
            "section_number": sec,
            "correct": section_correct_wrong.get(sec, [0, 0])[0],
            "wrong": section_correct_wrong.get(sec, [0, 0])[1],
            "section_percentage": section_percentage,
            "section_name": subject_mapping.get(sec, f"Section {sec}")
        })
        if attempt_number == 1:
            session.run("""
            MATCH (st:Statistics {school_id: $school_id, class_name: $class_name, section_number: $section_number})
            SET st.first_exam_percentage = coalesce(st.first_exam_percentage, 0) + $section_percentage,
                st.first_exam_count = coalesce(st.first_exam_count, 0) + 1
            """, {"school_id": school_id, "class_name": class_name, "section_number": sec, "section_percentage": section_percentage})
        elif attempt_number == 2:
            session.run("""
            MATCH (st:Statistics {school_id: $school_id, class_name: $class_name, section_number: $section_number})
            SET st.second_exam_percentage = coalesce(st.second_exam_percentage, 0) + $section_percentage,
                st.second_exam_count = coalesce(st.second_exam_count, 0) + 1
            """, {"school_id": school_id, "class_name": class_name, "section_number": sec, "section_percentage": section_percentage})
