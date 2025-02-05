# tools/exam.py
import random
from datetime import datetime
from sqlalchemy.orm import Session
from typing import Dict, List, Any
from tools.models import Question, QuestionChoice, Exam, ExamAnswer, UserChoice, User
from tools.statistics_utils import update_statistics

def load_questions(db: Session):
    """
    Loads all questions from the database.
    """
    return db.query(Question).all()

def select_questions(db: Session, user: User) -> Dict[int, List[Question]]:
    """
    Select exactly 5 questions from each section (total 20 questions) and ensure that
    at least one question from each type ('true_false', 'single_choice', 'multiple_choice', 'ordering')
    is present.
    """
    if user.attempts >= 2:
        return {}
    questions = db.query(Question).all()
    # For each section, select exactly 5 questions (assuming enough questions exist)
    selected = {}
    for sec in range(1, 5):
        sec_questions = [q for q in questions if q.section == sec]
        if len(sec_questions) < 5:
            selected[sec] = sec_questions.copy()
        else:
            selected[sec] = random.sample(sec_questions, 5)
    # Flatten the selection into a single list
    total_selected = [q for sec in selected for q in selected[sec]]
    # Ensure at least one question of each type is present
    required_types = {"true_false", "single_choice", "multiple_choice", "ordering"}
    types_present = set(q.type for q in total_selected)
    missing_types = required_types - types_present
    for m_type in missing_types:
        # Find a candidate question of the missing type
        candidates = [q for q in questions if q.type == m_type]
        if candidates:
            candidate = random.choice(candidates)
            sec = candidate.section
            # Replace a question in the candidate's section that is overrepresented
            replaced = False
            for i, q in enumerate(selected[sec]):
                type_count = sum(1 for x in total_selected if x.type == q.type)
                if type_count > 1:
                    selected[sec][i] = candidate
                    replaced = True
                    break
            if not replaced:
                # Force replacement if needed
                selected[sec][0] = candidate
            # Update the flattened list after replacement
            total_selected = [q for s in selected for q in selected[s]]
    # Return the questions grouped by section (each section exactly 5 questions)
    final_dict = {sec: selected.get(sec, []) for sec in range(1, 5)}
    return final_dict

def process_results(db: Session, user: User, exam: Exam,
                    selected_questions: List[Question],
                    answers_dict: Dict[str, Any], end_time: datetime):
    """
    Process the exam results, update scores and statistics.
    """
    # section_scores: { section_number: [sum_earned, sum_possible] }
    section_scores = {sec: [0, 0] for sec in range(1, 5)}
    # section_correct_wrong: { section_number: [correct_count, wrong_count] }
    section_correct_wrong = {sec: [0, 0] for sec in range(1, 5)}
    for q in selected_questions:
        ans_data = answers_dict.get(str(q.id))
        if not ans_data:
            exam_ans = create_exam_answer(db, exam, q, 0, [])
            section_scores[q.section][1] += q.points
            section_correct_wrong[q.section][1] += 1  # Count as wrong
            continue
        else:
            selected_texts = ans_data.selected_texts or []
            exam_ans = create_exam_answer(db, exam, q, 0, selected_texts)
            points_earned, is_full_correct = evaluate_question(db, q, selected_texts)
            exam_ans.points_earned = points_earned
            db.commit()
            section_scores[q.section][0] += points_earned
            section_scores[q.section][1] += q.points
            if is_full_correct:
                section_correct_wrong[q.section][0] += 1
            else:
                section_correct_wrong[q.section][1] += 1
    all_section_pass = True
    for sec in section_scores:
        earned, possible = section_scores[sec]
        section_score = (earned / possible) * 100 if possible > 0 else 0.0
        if section_score < 75.0:
            all_section_pass = False
    total_earned = sum(section_scores[s][0] for s in section_scores)
    total_possible = sum(section_scores[s][1] for s in section_scores)
    final_score = (total_earned / total_possible) * 100 if total_possible > 0 else 0.0
    pass_exam = (all_section_pass and (final_score >= 75.0))
    exam.passed = pass_exam
    db.commit()
    user.attempts += 1
    user.last_attempt_date = datetime.now()
    general_percentage = final_score
    if user.attempts == 1:
        user.score1 = general_percentage
        user.score_avg = general_percentage
    elif user.attempts == 2:
        user.score2 = general_percentage
        user.score_avg = (user.score1 + user.score2) / 2
    else:
        user.score_avg = (user.score_avg + general_percentage) / 2
    exam.end_time = end_time
    db.commit()
    update_statistics(db, user.school_id, user.class_name,
                      section_scores, section_correct_wrong)

def create_exam_answer(db: Session, exam: Exam, question: Question,
                       points_earned: int, selected_texts: List[str]):
    exam_ans = ExamAnswer(
        exam_id=exam.exam_id,
        question_id=question.id,
        points_earned=points_earned
    )
    db.add(exam_ans)
    db.commit()
    db.refresh(exam_ans)
    all_choices = db.query(QuestionChoice).filter(QuestionChoice.question_id == question.id).all()
    if question.type == "ordering":
        if len(selected_texts) == 1 and "," in selected_texts[0]:
            splitted = [x.strip() for x in selected_texts[0].split(",")]
        else:
            splitted = selected_texts
        for idx, val in enumerate(splitted):
            normalized_val = val.strip().lower()
            for choice in all_choices:
                if choice.choice_text.strip().lower() == normalized_val:
                    uc = UserChoice(
                        exam_answer_id=exam_ans.id,
                        question_choice_id=choice.id,
                        user_position=idx
                    )
                    db.add(uc)
                    db.commit()
                    break
    elif question.type in ["single_choice", "multiple_choice", "true_false"]:
        for txt in selected_texts:
            normalized_txt = txt.strip().lower()
            for choice in all_choices:
                if choice.choice_text.strip().lower() == normalized_txt:
                    uc = UserChoice(
                        exam_answer_id=exam_ans.id,
                        question_choice_id=choice.id
                    )
                    db.add(uc)
                    db.commit()
                    break
    return exam_ans

def evaluate_question(db: Session, question: Question, selected_texts: List[str]) -> tuple[int, bool]:
    if question.type == "true_false":
        correct_choice = db.query(QuestionChoice).filter_by(question_id=question.id, is_correct=True).first()
        if not correct_choice:
            return (0, False)
        if len(selected_texts) == 1 and selected_texts[0].strip().lower() == correct_choice.choice_text.strip().lower():
            return (question.points, True)
        return (0, False)
    elif question.type == "single_choice":
        correct_choice = db.query(QuestionChoice).filter_by(question_id=question.id, is_correct=True).first()
        if not correct_choice:
            return (0, False)
        if len(selected_texts) == 1 and selected_texts[0].strip().lower() == correct_choice.choice_text.strip().lower():
            return (question.points, True)
        return (0, False)
    elif question.type == "multiple_choice":
        correct_choices = db.query(QuestionChoice).filter_by(question_id=question.id, is_correct=True).all()
        correct_texts = set(c.choice_text.strip().lower() for c in correct_choices)
        user_set = set(txt.strip().lower() for txt in selected_texts)
        if not user_set.issubset(correct_texts):
            return (0, False)
        correct_selected = len(user_set & correct_texts)
        total_correct = len(correct_texts)
        if total_correct == 0:
            return (0, False)
        partial_score = int(question.points * (correct_selected / total_correct))
        is_full = (partial_score == question.points)
        return (partial_score, is_full)
    elif question.type == "ordering":
        if len(selected_texts) == 1 and "," in selected_texts[0]:
            splitted_texts = [x.strip().lower() for x in selected_texts[0].split(",")]
        else:
            splitted_texts = [x.strip().lower() for x in selected_texts]
        all_choices = db.query(QuestionChoice).filter_by(question_id=question.id).all()
        mismatch = False
        for c in all_choices:
            if c.correct_position is None:
                continue
            normalized_choice = c.choice_text.strip().lower()
            try:
                user_index = splitted_texts.index(normalized_choice)
                if user_index != c.correct_position:
                    mismatch = True
                    break
            except ValueError:
                mismatch = True
                break
        if mismatch:
            return (0, False)
        else:
            return (question.points, True)
    return (0, False)
