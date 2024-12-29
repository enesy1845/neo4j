# tools/exam.py

import random
from datetime import datetime
from sqlalchemy.orm import Session
from tools.models import Question, Answer, Exam, ExamAnswer, User
from tools.statistics_utils import update_statistics

def load_questions(db: Session):
    return db.query(Question).all()

def select_questions(db: Session, user: User):
    if user.attempts >= 2:
        return None
    questions = load_questions(db)
    sections = {1: [], 2: [], 3: [], 4: []}
    for sec in range(1, 5):
        sec_qs = [q for q in questions if q.section == sec]
        selected = sec_qs if len(sec_qs) < 5 else random.sample(sec_qs, 5)
        sections[sec] = selected
    return sections

def process_results(db: Session, user: User, selected_questions, user_answers: dict, end_time: datetime):
    section_correct = {1: 0, 2: 0, 3: 0, 4: 0}
    section_wrong = {1: 0, 2: 0, 3: 0, 4: 0}
    section_scores = {1: 0, 2: 0, 3: 0, 4: 0}

    # 1) Doğru-yanlış ve skorları hesapla
    for section, qs in selected_questions.items():
        for q in qs:
            ans = db.query(Answer).filter(Answer.question_id == q.id).first()
            if not ans:
                section_wrong[section] += 1
                continue
            correct_answer = ans.correct_answer.strip().lower()
            user_answer = user_answers.get(str(q.id), "").strip().lower()

            correct = False
            if q.type in ['true_false', 'single_choice']:
                if user_answer == correct_answer:
                    correct = True
            elif q.type in ['multiple_choice', 'ordering']:
                correct_ans_set = set(a.strip() for a in correct_answer.split(','))
                user_ans_set = set(a.strip() for a in user_answer.split(','))
                if correct_ans_set == user_ans_set:
                    correct = True

            if correct:
                section_correct[section] += 1
                section_scores[section] += q.points
            else:
                section_wrong[section] += 1

    # 2) Kullanıcının attempts güncellemesi
    user.attempts += 1
    user.last_attempt_date = datetime.now()

    # Basit bir hesap: total max puan 20 diyelim, (score/20)*100 => general_percentage
    total_score = sum(section_scores.values())
    general_percentage = (total_score / 20) * 100 if total_score > 0 else 0

    if user.attempts == 1:
        user.score1 = general_percentage
    elif user.attempts == 2:
        user.score2 = general_percentage
        user.score_avg = (user.score1 + user.score2) / 2

    db.commit()

    # 3) Exam kaydı
    exam = Exam(
        user_id=user.user_id,
        class_name=user.class_name,
        school_id=user.school_id,
        start_time=datetime.now(),
        end_time=end_time
    )
    db.add(exam)
    db.commit()
    db.refresh(exam)

    # 4) ExamAnswer
    for section, qs in selected_questions.items():
        for q in qs:
            ans = db.query(Answer).filter(Answer.question_id == q.id).first()
            if not ans:
                continue
            correct_answer = ans.correct_answer.strip().lower()
            user_answer = user_answers.get(str(q.id), "").strip().lower()

            is_correct = False
            if q.type in ['true_false', 'single_choice']:
                if user_answer == correct_answer:
                    is_correct = True
            elif q.type in ['multiple_choice', 'ordering']:
                correct_ans_set = set(a.strip() for a in correct_answer.split(','))
                user_ans_set = set(a.strip() for a in user_answer.split(','))
                if correct_ans_set == user_ans_set:
                    is_correct = True

            points_earned = q.points if is_correct else 0
            exam_ans = ExamAnswer(
                exam_id=exam.exam_id,
                question_id=q.id,
                user_answer=user_answers.get(str(q.id), ""),
                is_correct=is_correct,
                points_earned=points_earned
            )
            db.add(exam_ans)
    db.commit()

    # 5) İstatistik güncelle
    update_statistics(db, user.school_id, user.class_name, section_correct, section_wrong, section_scores)
