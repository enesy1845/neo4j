# tools/exam.py

import uuid
import random
from datetime import datetime
from sqlalchemy.orm import Session
from tools.models import Question, Answer, Exam, ExamAnswer, User, Statistics

def load_questions(db: Session):
    return db.query(Question).all()

def select_questions(db: Session, user):
    if user.attempts >= 2:
        print("You have no remaining exam attempts.")
        return None
    questions = load_questions(db)
    sections = {1: [], 2: [], 3: [], 4: []}
    for sec in range(1,5):
        sec_qs = [q for q in questions if q.section == sec]
        selected = sec_qs if len(sec_qs) < 5 else random.sample(sec_qs, 5)
        sections[sec] = selected
    return sections

def start_exam(db: Session, user):
    selected_questions = select_questions(db, user)
    if not selected_questions:
        return
    print("Exam started. You have 30 minutes. (Simulated)")
    user_answers = {}
    for section, qs in selected_questions.items():
        print(f"\n--- Section {section} ---")
        for q in qs:
            print(f"Q: {q.question} ({q.type})")
            user_response = input("Your answer: ")
            user_answers[q.id] = user_response
    end_time = datetime.now()
    process_results(db, user, selected_questions, user_answers, end_time)

def process_results(db: Session, user, selected_questions, user_answers, end_time):
    total_score = 0
    section_scores = {1:0, 2:0, 3:0, 4:0}
    section_correct = {1:0, 2:0, 3:0, 4:0}
    section_wrong = {1:0, 2:0, 3:0, 4:0}

    for section, qs in selected_questions.items():
        for q in qs:
            ans = db.query(Answer).filter(Answer.question_id == q.id).first()
            correct_answer = ans.correct_answer.strip().lower()
            user_answer = user_answers.get(q.id, "").strip().lower()
            correct = False
            if q.type in ['true_false', 'single_choice']:
                if user_answer == correct_answer:
                    correct = True
            elif q.type in ['multiple_choice', 'ordering']:
                correct_ans_set = set([a.strip().lower() for a in correct_answer.split(',')])
                user_ans_set = set([a.strip().lower() for a in user_answer.split(',')])
                if user_ans_set == correct_ans_set:
                    correct = True

            if correct:
                section_scores[section] += q.points
                section_correct[section] += 1
            else:
                section_wrong[section] += 1

    total_score = sum(section_scores.values())
    score_avg = (total_score / 20) * 100 if total_score > 0 else 0

    passed = True
    for sec in range(1,5):
        section_percentage = (section_scores[sec]/5)*100 if section_scores[sec] > 0 else 0
        if section_percentage < 75:
            passed = False
    if score_avg < 75:
        passed = False
    result = "Passed" if passed else "Failed"

    user.attempts += 1
    user.last_attempt_date = datetime.now()
    if user.attempts == 1:
        user.score1 = total_score
    elif user.attempts == 2:
        user.score2 = total_score
        user.score_avg = (user.score1 + user.score2) / 2
    db.commit()

    exam = Exam(
        user_id=user.user_id,
        class_name=user.class_name,
        school_name=user.school_name,
        start_time=datetime.now(),
        end_time=end_time
    )
    db.add(exam)
    db.commit()
    db.refresh(exam)

    for section, qs in selected_questions.items():
        for q in qs:
            ans = db.query(Answer).filter(Answer.question_id == q.id).first()
            correct_answer = ans.correct_answer.strip().lower()
            user_answer = user_answers.get(q.id, "").strip().lower()

            is_correct = False
            if q.type in ['true_false', 'single_choice']:
                if user_answer == correct_answer:
                    is_correct = True
            elif q.type in ['multiple_choice', 'ordering']:
                correct_ans_set = set([a.strip().lower() for a in correct_answer.split(',')])
                user_ans_set = set([a.strip().lower() for a in user_answer.split(',')])
                if user_ans_set == correct_ans_set:
                    is_correct = True
            points_earned = q.points if is_correct else 0

            exam_ans = ExamAnswer(
                exam_id=exam.exam_id,
                question_id=q.id,
                user_answer=user_answers.get(q.id, ""),
                is_correct=is_correct,
                points_earned=points_earned
            )
            db.add(exam_ans)
    db.commit()

    update_statistics(db, user.school_name, user.class_name, section_correct, section_wrong, section_scores)
    print(f"Exam Finished. Your Score: {total_score}/20. Result: {result}\n")

def update_statistics(db: Session, school_name, class_name, section_correct, section_wrong, section_scores):
    for sec in range(1,5):
        stat = db.query(Statistics).filter(
            Statistics.school_name == school_name,
            Statistics.class_name == class_name,
            Statistics.section_number == sec
        ).first()
        if not stat:
            stat = Statistics(
                school_name=school_name,
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

        stat.correct_questions += section_correct[sec]
        stat.wrong_questions += section_wrong[sec]
        # exam.py içindeki update_statistics fonksiyonunda

        # Önce bölümün maksimum puanını hesaplayın:
        max_section_points = sum(q.points for q in db.query(Question).filter(Question.section == sec).all())

        # Ardından new_percentage hesaplamasını güncelleyin:
        new_percentage = (section_scores[sec] / max_section_points) * 100 if max_section_points > 0 else 0

        
        stat.average_score = (stat.average_score + new_percentage) / 2
        stat.section_percentage = new_percentage
        db.commit()
