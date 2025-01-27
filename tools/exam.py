# tools/exam.py

import random
from datetime import datetime
from sqlalchemy.orm import Session
from typing import Dict, List
from tools.models import Question, QuestionChoice, Exam, ExamAnswer, UserChoice, User
from tools.statistics_utils import update_statistics

def load_questions(db: Session):
    return db.query(Question).all()

def select_questions(db: Session, user: User):
    if user.attempts >= 2:
        return None
    questions = load_questions(db)
    # basit random logic -> her section'dan 5 tane
    sections = {1: [], 2: [], 3: [], 4: []}
    for sec in range(1, 5):
        sec_qs = [q for q in questions if q.section == sec]
        selected = sec_qs if len(sec_qs) < 5 else random.sample(sec_qs, 5)
        sections[sec] = selected
    return sections

def process_results(db: Session, user: User, exam: Exam,
                    selected_questions: List[Question],
                    answers_dict, end_time):
    """
    Her section için:
      - sum_points_earned, sum_points_possible
      - section_score = round( (earned / possible)*100, 2 )

    Sonra final_score = round( (total_earned / total_possible)*100, 2 )

    Geçme Kriteri:
    - Tüm section_score >= 75
    - final_score >= 75
    Aksi halde fail
    """
    # "answers_dict" => { question_id: { "selected_texts": [..] } }
    # Aşağısı eskiden de vardı:
    #   evaluate_question => ans.points_earned
    from math import isclose

    section_scores = {}  # key=section_number -> (sum_earned, sum_possible)
    for sec in range(1, 5):
        section_scores[sec] = [0, 0]  # [sum_earned, sum_possible]

    for q in selected_questions:
        ans_data = answers_dict.get(str(q.id))
        if not ans_data:
            # User hiç cevap vermemiş -> 0 puan
            exam_ans = create_exam_answer(db, exam, q, 0, [])
            section_scores[q.section][1] += q.points
            continue

        selected_texts = ans_data.selected_texts or []
        exam_ans = create_exam_answer(db, exam, q, 0, selected_texts)
        points_earned, _is_correct = evaluate_question(db, q, selected_texts)
        exam_ans.points_earned = points_earned
        db.commit()

        # section skoruna ekle
        section_scores[q.section][0] += points_earned
        section_scores[q.section][1] += q.points

    # Artık section bazında (earned / possible)*100
    # pass/fail'e bakmak için en az 75
    all_section_pass = True
    for sec in section_scores:
        earned, possible = section_scores[sec]
        if possible > 0:
            section_score = (earned / possible) * 100
        else:
            section_score = 0.0
        if section_score < 75.0:
            all_section_pass = False

    # Final Score
    total_earned = sum([section_scores[s][0] for s in section_scores])
    total_possible = sum([section_scores[s][1] for s in section_scores])
    if total_possible > 0:
        final_score = (total_earned / total_possible) * 100
    else:
        final_score = 0.0

    # pass => all_section_pass & final_score>=75
    pass_exam = (all_section_pass and (final_score >= 75.0))
    exam.passed = pass_exam  # <-- ekle

    # Yukarıdaki pass/fail "ExamAnswer" tablosuna kaydedilmiyor. Ama
    # istersen Exam tablosuna da "passed" bool alanı ekleyebilirsin.
    # Şimdilik eklemedim.

    # Kullanıcının attempts, score hesaplama (score1, score2, score_avg) eskisi gibi
    user.attempts += 1
    user.last_attempt_date = datetime.now()

    # final_score => user'ın bu exam'deki performansı
    # general_percentage => final_score
    general_percentage = final_score

    if user.attempts == 1:
        user.score1 = general_percentage
        user.score_avg = general_percentage
    elif user.attempts == 2:
        user.score2 = general_percentage
        user.score_avg = (user.score1 + user.score2) / 2
    else:
        # eğer 2'den fazla attempt yoksa, bu else'e girmez ama
        # sistemde "2 den fazla attempt" kapalı, yinede koruyalım
        user.score_avg = (user.score_avg + general_percentage) / 2

    exam.end_time = end_time
    db.commit()

    # Statistics
    # section_scores + user => update_statistics
    # oradaki average_score -> (old + section_score)/2 vs.
    # bu logic orada
    update_statistics(db, user.school_id, user.class_name, section_scores)

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

def evaluate_question(db: Session, question: Question, selected_texts: List[str]):
    # Aşağısı eskisi gibi, ama en sonunda "points" max question.points => %100
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
            # Yanlış şık da seçmiş -> 0
            return (0, False)

        # kısmi puan: (seçtiğin doğru sayısı) / (toplam doğru sayısı)
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

    # default
    return (0, False)
