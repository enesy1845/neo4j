# tools/exam.py
import random
from datetime import datetime
from uuid import uuid4
from tools.statistics_utils import update_statistics

def load_questions(session):
    result = session.run("MATCH (q:Question) RETURN q")
    return [record["q"] for record in result]

def select_questions(session, user):
    if user.get("attempts", 0) >= 2:
        return {}
    questions = load_questions(session)
    selected = {}
    for sec in range(1, 5):
        sec_questions = [q for q in questions if q.get("section") == sec]
        if len(sec_questions) < 5:
            selected[sec] = sec_questions.copy()
        else:
            selected[sec] = random.sample(sec_questions, 5)
    total_selected = [q for sec in selected for q in selected[sec]]
    required_types = {"true_false", "single_choice", "multiple_choice", "ordering"}
    types_present = set(q.get("type") for q in total_selected)
    missing_types = required_types - types_present
    for m_type in missing_types:
        candidates = [q for q in questions if q.get("type") == m_type]
        if candidates:
            candidate = random.choice(candidates)
            sec = candidate.get("section")
            replaced = False
            for i, q in enumerate(selected.get(sec, [])):
                type_count = sum(1 for x in total_selected if x.get("type") == q.get("type"))
                if type_count > 1:
                    selected[sec][i] = candidate
                    replaced = True
                    break
            if not replaced and sec in selected:
                selected[sec][0] = candidate
    final_dict = {sec: selected.get(sec, []) for sec in range(1, 5)}
    return final_dict

def process_results(session, user, exam_node, selected_questions, answers_dict, end_time):
    section_scores = {sec: [0, 0] for sec in range(1, 5)}
    section_correct_wrong = {sec: [0, 0] for sec in range(1, 5)}
    for q in selected_questions:
        qid = q["id"]
        ans_data = answers_dict.get(str(qid))
        if not ans_data:
            points_earned = 0
        else:
            if isinstance(ans_data, dict):
                selected = ans_data.get("selected_texts", [])
            else:
                selected = ans_data.selected_texts or []
            result = session.run("""
            MATCH (q:Question {id: $qid})-[:HAS_CHOICE]->(c:Choice)
            WHERE c.is_correct = true
            RETURN collect(c.choice_text) as correct
            """, {"qid": qid})
            correct_choices = result.single()["correct"]
            if set(selected) == set(correct_choices):
                points_earned = q.get("points", 1)
            elif set(selected) & set(correct_choices):
                points_earned = q.get("points", 1) / 2
            else:
                points_earned = 0

        section_scores[q["section"]][0] += points_earned
        section_scores[q["section"]][1] += q.get("points", 1)
        if points_earned == q.get("points", 1):
            section_correct_wrong[q["section"]][0] += 1
        else:
            section_correct_wrong[q["section"]][1] += 1

        exam_answer_id = str(uuid4())
        session.run("""
        MATCH (e:Exam {exam_id: $exam_id}), (q:Question {id: $qid})
        CREATE (ea:ExamAnswer {
            id: $exam_answer_id,
            points_earned: $points_earned,
            question_id: $qid
        })
        CREATE (e)-[:HAS_ANSWER]->(ea)
        CREATE (ea)-[:FOR_QUESTION]->(q)
        CREATE (ea)-[:ANSWER_FOR]->(q)
        """, {"exam_id": exam_node["exam_id"], "qid": qid, "exam_answer_id": exam_answer_id, "points_earned": points_earned})

        # Eğer tam puan alamadıysa ilgili soru düğümünde wrong_count artırılıyor
        if points_earned < q.get("points", 1):
            session.run("""
            MATCH (q:Question {id: $qid})
            SET q.wrong_count = coalesce(q.wrong_count, 0) + 1
            """, {"qid": qid})

        # Seçilen şıklar için sayacın güncellenmesi
        if ans_data:
            if isinstance(ans_data, dict):
                selected = ans_data.get("selected_texts", [])
            else:
                selected = ans_data.selected_texts or []
            for answer_text in selected:
                session.run("""
                MATCH (q:Question {id: $qid})-[:HAS_CHOICE]->(c:Choice)
                WHERE toLower(c.choice_text) = toLower($answer_text)
                SET c.selected_count = coalesce(c.selected_count, 0) + 1
                """, {"qid": qid, "answer_text": answer_text.strip()})
                session.run("""
                MATCH (q:Question {id: $qid})-[:HAS_CHOICE]->(c:Choice)
                WHERE toLower(c.choice_text) = toLower($answer_text) AND c.is_correct = true
                SET c.selected_correct_count = coalesce(c.selected_correct_count, 0) + 1
                """, {"qid": qid, "answer_text": answer_text.strip()})

    # Sınavın bitiş zamanı ve durumunun güncellenmesi
    session.run("""
    MATCH (e:Exam {exam_id: $exam_id})
    SET e.end_time = datetime($end_time), e.status = 'submitted'
    """, {"exam_id": exam_node["exam_id"], "end_time": end_time})

    total_earned = sum(section_scores[s][0] for s in section_scores)
    total_possible = sum(section_scores[s][1] for s in section_scores)
    final_score = round((total_earned / total_possible) * 100, 2) if total_possible > 0 else 0.0

    # Kullanıcının sınav denemelerini güncelleme: 
    # İlk deneme ise first_exam_score, ikinci deneme ise second_exam_score, ve genel ortalama score_avg hesaplanıyor.
    session.run("""
    MATCH (u:User {user_id: $user_id})
    WITH u, coalesce(u.attempts, 0) as currentAttempts
    SET u.attempts = currentAttempts + 1
    WITH u, currentAttempts + 1 as newAttempts
    SET u.first_exam_score = CASE WHEN newAttempts = 1 THEN $final_score ELSE u.first_exam_score END,
        u.second_exam_score = CASE WHEN newAttempts = 2 THEN $final_score ELSE u.second_exam_score END,
        u.score_avg = CASE WHEN newAttempts = 1 THEN $final_score
                           WHEN newAttempts = 2 THEN (u.first_exam_score + $final_score)/2
                           ELSE u.score_avg END
    """, {"user_id": user["user_id"], "final_score": final_score})

    # Deneme numarasını (1 veya 2) update_statistics fonksiyonuna geçiriyoruz
    # (Not: user nesnesi eski olabileceğinden, deneme sayısını dışarıdan takip etmek gerekebilir;
    # burada basitçe mevcut deneme sayısının bir fazlasını kullanıyoruz.)
    attempt_number = user.get("attempts", 0) + 1
    update_statistics(session, user.get("school_id"), user["class_name"], section_scores, section_correct_wrong, attempt_number=attempt_number)