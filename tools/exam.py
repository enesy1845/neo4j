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
    # Calculate scores per section.
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
        if points_earned < q.get("points", 1):
            session.run("""
MATCH (q:Question {id: $qid})
SET q.wrong_count = coalesce(q.wrong_count, 0) + 1
""", {"qid": qid})
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
                session.run("""
MATCH (ea:ExamAnswer {id: $exam_answer_id})
MATCH (q:Question {id: $qid})-[:HAS_CHOICE]->(c:Choice)
WHERE toLower(c.choice_text) = toLower($answer_text)
CREATE (ea)-[:CHOSE]->(c)
""", {"exam_answer_id": exam_answer_id, "qid": qid, "answer_text": answer_text.strip()})
    total_earned = sum(section_scores[s][0] for s in section_scores)
    total_possible = sum(section_scores[s][1] for s in section_scores)
    final_score = round((total_earned / total_possible) * 100, 2) if total_possible > 0 else 0.0
    attempt_number = user.get("attempts", 0) + 1
    exam_result_id = str(uuid4())
    session.run("""
CREATE (er:ExamResult {
    id: $exam_result_id,
    exam_id: $exam_id,
    student_id: $user_id,
    attempt_number: $attempt_number,
    exam_percentage: $final_score,
    timestamp: datetime($end_time)
})
""", {
        "exam_result_id": exam_result_id,
        "exam_id": exam_node["exam_id"],
        "user_id": user["user_id"],
        "attempt_number": attempt_number,
        "final_score": final_score,
        "end_time": end_time
    })
    session.run("""
MATCH (u:User {user_id: $user_id}), (er:ExamResult {id: $exam_result_id})
CREATE (u)-[:HAS_RESULT]->(er)
""", {"user_id": user["user_id"], "exam_result_id": exam_result_id})
    for sec in range(1, 5):
        session.run("""
MATCH (er:ExamResult {id: $exam_result_id}),
(st:Statistics {school_id: $school_id, class_name: $class_name, section_number: $sec})
MERGE (er)-[:RESULT_FOR {section: $sec}]->(st)
""", {
            "exam_result_id": exam_result_id,
            "school_id": user.get("school_id"),
            "class_name": user.get("class_name"),
            "sec": sec
        })
    # Update user's exam attempt count and score average in one query.
    session.run("""
    MATCH (u:User {user_id: $user_id})
    WITH u, coalesce(u.attempts, 0) as old_attempts, coalesce(u.score_avg, 0) as old_avg
    SET u.score_avg = CASE 
        WHEN old_attempts = 0 THEN $final_score 
        ELSE round(((old_avg * old_attempts) + $final_score) / (old_attempts + 1), 2)
    END,
    u.attempts = old_attempts + 1
    """, {"user_id": user["user_id"], "final_score": final_score})
    update_statistics(session, user.get("school_id"), user.get("class_name"), section_scores, section_correct_wrong, attempt_number=attempt_number)
