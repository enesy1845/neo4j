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

def process_results(db: Session, user: User, exam: Exam, selected_questions: List[Question], answers_dict, end_time):
    # "answers_dict" => { question_id: { "selected_texts": [..] } }

    section_correct = {1: 0, 2: 0, 3: 0, 4: 0}
    section_wrong = {1: 0, 2: 0, 3: 0, 4: 0}
    section_scores = {1: 0, 2: 0, 3: 0, 4: 0}

    for q in selected_questions:
        ans_data = answers_dict.get(str(q.id))
        if not ans_data:
            # User hiç cevap vermemiş
            create_exam_answer(db, exam, q, 0, [])  # 0 puan
            section_wrong[q.section] += 1
            continue

        selected_texts = ans_data.selected_texts or []
        # "selected_texts" -> list[str], ordering / multiple / single / tf

        # 1) ExamAnswer kaydı
        exam_ans = create_exam_answer(db, exam, q, 0, selected_texts)

        # 2) Doğruluk kontrolü
        points_earned, is_correct = evaluate_question(db, q, selected_texts)
        exam_ans.points_earned = points_earned
        db.commit()

        if is_correct:
            section_correct[q.section] += 1
            section_scores[q.section] += points_earned
        else:
            section_wrong[q.section] += 1

    # Kullanıcının attempt/panel vs.
    user.attempts += 1
    user.last_attempt_date = datetime.now()
    total_score = sum(section_scores.values())
    general_percentage = (total_score / 20) * 100 if total_score > 0 else 0  # 20 puan = rastgele max?

    if user.attempts == 1:
        user.score1 = general_percentage
        user.score_avg = general_percentage
    elif user.attempts == 2:
        user.score2 = general_percentage
        user.score_avg = (user.score1 + user.score2) / 2

    exam.end_time = end_time
    db.commit()

    # İstatistik
    update_statistics(db, user.school_id, user.class_name, section_correct, section_wrong, section_scores)


def create_exam_answer(db: Session, exam: Exam, question: Question, points_earned: int, selected_texts: List[str]):
    exam_ans = ExamAnswer(
        exam_id=exam.exam_id,
        question_id=question.id,
        points_earned=points_earned
    )
    db.add(exam_ans)
    db.commit()
    db.refresh(exam_ans)

    # user_choices ekle
    # question.type'e göre ek mantık
    if question.type in ["single_choice", "multiple_choice", "true_false"]:
        # her selected_text'e göre question_choice bul
        for txt in selected_texts:
            choice_row = db.query(QuestionChoice).filter(
                QuestionChoice.question_id == question.id,
                QuestionChoice.choice_text == txt
            ).first()
            if choice_row:
                uc = UserChoice(
                    exam_answer_id=exam_ans.id,
                    question_choice_id=choice_row.id
                )
                db.add(uc)
        db.commit()

    elif question.type == "ordering":
        # ordering => user sıralamayı selected_texts bekliyoruz (örn: ["1","2","3","4"]).
        # Her elemanı satır satır kaydedelim:
        for idx, val in enumerate(selected_texts):
            # val => "1", "2", ...
            # question_choice bul
            choice_row = db.query(QuestionChoice).filter(
                QuestionChoice.question_id == question.id,
                QuestionChoice.choice_text == val
            ).first()
            if choice_row:
                uc = UserChoice(
                    exam_answer_id=exam_ans.id,
                    question_choice_id=choice_row.id,
                    user_position=idx  # kullanıcı sırasını da sakla
                )
                db.add(uc)
        db.commit()

    return exam_ans


def evaluate_question(db: Session, question: Question, selected_texts: List[str]):
    """
    Sorunun tipine göre user'ın seçimini doğru/yanlış değerlendirip puan döndürüyoruz.
    """
    # max alabileceği puan = question.points
    # Bu basit örnekte, "tam doğruysa full puan, aksi 0" diyelim.

    if question.type == "true_false":
        # Tek bir choice doğru, user da tek bir choice seçmişse -> check
        correct_choice = db.query(QuestionChoice).filter_by(question_id=question.id, is_correct=True).first()
        if not correct_choice:
            return (0, False)
        if len(selected_texts) == 1 and selected_texts[0] == correct_choice.choice_text:
            return (question.points, True)
        return (0, False)

    elif question.type == "single_choice":
        # Tek bir choice doğru
        correct_choice = db.query(QuestionChoice).filter_by(question_id=question.id, is_correct=True).first()
        if not correct_choice:
            return (0, False)
        if len(selected_texts) == 1 and selected_texts[0] == correct_choice.choice_text:
            return (question.points, True)
        return (0, False)

    elif question.type == "multiple_choice":
        # Birden fazla choice doğru
        correct_choices = db.query(QuestionChoice).filter_by(question_id=question.id, is_correct=True).all()
        correct_texts = set([c.choice_text for c in correct_choices])

        user_set = set(selected_texts)
        if user_set == correct_texts:
            return (question.points, True)
        return (0, False)

    elif question.type == "ordering":
        # Tüm choice’ları correct_position sırasıyla user_position eşleşiyor mu?
        all_choices = db.query(QuestionChoice).filter_by(question_id=question.id).all()
        # Mesela [ ("3",pos=2), ("1",pos=0), ... ] vs.
        mismatch = False
        for c in all_choices:
            if c.correct_position is not None:
                # Kullanıcı bu choice’ı hangi indexte seçti?
                # user_texts => "val" sıralaması
                # basit approach: user_texts[x] == c.choice_text
                # eğer x == c.correct_position => mismatch yok
                pass

        # Daha basit: "selected_texts" = ["1","2","3","4"]
        # DB’de correct_position=0 => "1", correct_position=1 => "2", ...
        # Eşleşirse tam puan
        for c in all_choices:
            if c.correct_position is None:
                continue
            # c.choice_text ne, user list’te index var mı
            # user_index = selected_texts.index(c.choice_text)
            # if user_index != c.correct_position => mismatch = True
            try:
                user_index = selected_texts.index(c.choice_text)
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
