# tools/exam.py
import random
from datetime import datetime
from sqlalchemy.orm import Session
from typing import Dict, List,Any
from tools.models import Question, QuestionChoice, Exam, ExamAnswer, UserChoice, User
from tools.statistics_utils import update_statistics

def load_questions(db: Session):
    """
    Veritabanından tüm soruları yükler.
    """
    return db.query(Question).all()

def select_questions(db: Session, user: User) -> Dict[int, List[Question]]:
    """
    Sınav için soruları seçer.
    - Her soru tipinden en az bir tane seçilir.
    - Her section'dan belirli sayıda soru seçilir.
    - Toplamda istenen sayıda soru olacak şekilde düzenlenir.
    """
    if user.attempts >= 2:
        return {}

    # Tüm soruları al
    questions = db.query(Question).all()

    # 1) Her question.type için en az 1 tane (mümkünse) seç
    question_types = ["true_false", "single_choice", "multiple_choice", "ordering"]
    must_have = []
    for qt in question_types:
        q_of_type = [q for q in questions if q.type == qt]
        if q_of_type:
            must_have.append(random.choice(q_of_type))
        else:
            # O tipte soru yoksa, bu kuralı enforce edemezsiniz.
            pass

    # 2) Her section'dan 5 tane seçme
    sections = {1: [], 2: [], 3: [], 4: []}
    for sec in range(1, 5):
        sec_qs = [q for q in questions if q.section == sec]
        if len(sec_qs) <= 5:
            sections[sec] = sec_qs
        else:
            sections[sec] = random.sample(sec_qs, 5)

    # 3) Tüm bu seçilenleri set olarak toplayalım
    selected_final = set()
    for sec in sections:
        selected_final.update(sections[sec])
    for mh in must_have:
        selected_final.add(mh)

    # 4) Geri dönerken yine section bazlı dict yapımız olsun:
    final_dict = {1: [], 2: [], 3: [], 4: []}
    for q in selected_final:
        final_dict[q.section].append(q)

    return final_dict

def process_results(db: Session, user: User, exam: Exam,
                   selected_questions: List[Question],
                   answers_dict: Dict[str, Any], end_time: datetime):
    """
    Sınav sonuçlarını işleyerek kullanıcı puanlarını ve istatistikleri günceller.
    - Her section için toplam puan ve olası puan hesaplanır.
    - Her section için doğru ve yanlış soru sayısı hesaplanır.
    - Geçme kriterleri uygulanır.
    - Kullanıcı puanları güncellenir.
    - İstatistikler güncellenir.
    """
    # "answers_dict" => { question_id: { "selected_texts": [..] } }
    
    # section_scores => { section_number: [sum_earned, sum_possible] }
    section_scores = {sec: [0, 0] for sec in range(1, 5)}   # [sum_earned, sum_possible]
    # section_correct_wrong => { section_number: [correct_count, wrong_count] }
    section_correct_wrong = {sec: [0, 0] for sec in range(1, 5)}  # [correct_count, wrong_count]

    for q in selected_questions:
        ans_data = answers_dict.get(str(q.id))
        if not ans_data:
            # Kullanıcı hiç cevap vermemiş -> 0 puan
            exam_ans = create_exam_answer(db, exam, q, 0, [])
            section_scores[q.section][1] += q.points
            section_correct_wrong[q.section][1] += 1  # Yanlış sayılır
            continue
        else:
            selected_texts = ans_data.selected_texts or []
        exam_ans = create_exam_answer(db, exam, q, 0, selected_texts)
        points_earned, is_full_correct = evaluate_question(db, q, selected_texts)
        exam_ans.points_earned = points_earned
        db.commit()

        # Section puanlarına ekle
        section_scores[q.section][0] += points_earned
        section_scores[q.section][1] += q.points

        # Tam doğru mu kontrolü
        if is_full_correct:
            section_correct_wrong[q.section][0] += 1  # Doğru sayısı
        else:
            section_correct_wrong[q.section][1] += 1  # Yanlış sayısı

    # Geçme kriterlerini kontrol et
    all_section_pass = True
    for sec in section_scores:
        earned, possible = section_scores[sec]
        if possible > 0:
            section_score = (earned / possible) * 100
        else:
            section_score = 0.0
        if section_score < 75.0:
            all_section_pass = False

    # Final score hesapla
    total_earned = sum([section_scores[s][0] for s in section_scores])
    total_possible = sum([section_scores[s][1] for s in section_scores])
    if total_possible > 0:
        final_score = (total_earned / total_possible) * 100
    else:
        final_score = 0.0

    # Geçme durumu
    pass_exam = (all_section_pass and (final_score >= 75.0))
    exam.passed = pass_exam  # Eklenen alan: passed
    db.commit()

    # Kullanıcı puanlarını güncelle
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
        # 2'den fazla attempt yoksa, bu else'e girmez
        user.score_avg = (user.score_avg + general_percentage) / 2

    exam.end_time = end_time
    db.commit()

    # İstatistikleri güncelle
    update_statistics(db, user.school_id, user.class_name,
                      section_scores,
                      section_correct_wrong)

def create_exam_answer(db: Session, exam: Exam, question: Question,
                      points_earned: int, selected_texts: List[str]):
    """
    ExamAnswer ve UserChoice kayıtlarını oluşturur.
    """
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

def evaluate_question(db: Session, question: Question, selected_texts: List[str]) -> (int, bool):
    """
    Sorunun doğru cevabı kontrol edilir ve puan hesaplanır.
    Returns:
        points_earned (int): Alınan puan
        is_full_correct (bool): Tam doğru mu?
    """
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
            # Yanlış şık da seçmiş -> 0 puan, yanlış
            return (0, False)
        # Kısmi puan: (seçilen doğru sayısı) / (toplam doğru sayısı)
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

    # Default case: yanlış
    return (0, False)
