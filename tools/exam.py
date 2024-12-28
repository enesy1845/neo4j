# tools/exam.py
import uuid
import random
from datetime import datetime
from sqlalchemy.orm import Session
from tools.models import Question, Answer, Exam, ExamAnswer, User, Statistics
from tools.statistics_utils import update_statistics

def load_questions(db: Session):
    return db.query(Question).all()

def select_questions(db: Session, user):
    if user.attempts >= 2:
        print("You have no remaining exam attempts.")
        return None
    questions = load_questions(db)
    sections = {1: [], 2: [], 3: [], 4: []}
    for sec in range(1, 5):
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

# tools/exam.py

def process_results(db, user, selected_questions, user_answers, end_time):
    from tools.models import Exam, ExamAnswer, Answer
    from datetime import datetime
    from tools.statistics_utils import update_statistics

    # Bölümler için doğru, yanlış ve puan bilgilerini saklamak için sözlükler
    section_correct = {}
    section_wrong = {}
    section_scores = {}
    section_max_scores = {}

    # Her bölüm için gerekli başlatmalar (1'den 4'e kadar örnek, sizde farklı ise güncelleyin)
    for section in range(1, 5):
        section_correct[section] = 0
        section_wrong[section] = 0
        section_scores[section] = 0
        section_max_scores[section] = 0  # Her bölümün maksimum puanı (sorulardaki "points" toplamı)

    # 1) Skor ve doğru/yanlış sayıları hesaplama
    for section, qs in selected_questions.items():
        for q in qs:
            ans = db.query(Answer).filter(Answer.question_id == q.id).first()
            if not ans:
                print(f"[WARNING] No answer found for question: {q.question}. Marking as incorrect.")
                section_wrong[section] += 1
                continue

            correct_answer = ans.correct_answer.strip().lower()
            user_answer = user_answers.get(q.id, "").strip().lower()

            correct = False
            if q.type in ['true_false', 'single_choice']:
                if user_answer == correct_answer:
                    correct = True
            elif q.type in ['multiple_choice', 'ordering']:
                correct_ans_set = set(a.strip().lower() for a in correct_answer.split(','))
                user_ans_set = set(a.strip().lower() for a in user_answer.split(','))
                if user_ans_set == correct_ans_set:
                    correct = True

            if correct:
                section_scores[section] += q.points
                section_correct[section] += 1
            else:
                section_wrong[section] += 1

            # Her bölümün maksimum puanını toplama
            section_max_scores[section] += q.points

    # 2) Her bölümün yüzdelik başarısını hesaplama
    section_percentages = {}
    for section in section_correct.keys():
        total_questions = section_correct[section] + section_wrong[section]
        if total_questions > 0:
            section_percentage = (section_correct[section] / total_questions) * 100
        else:
            section_percentage = 0.0
        section_percentages[section] = section_percentage

    # 3) Genel yüzdeyi hesaplama (ortalama)
    general_percentage = sum(section_percentages.values()) / len(section_percentages) if len(section_percentages) > 0 else 0.0

    # 4) Geçme kriterini belirleme
    # Her bölümde en az %75 doğruluk ve genel yüzde en az %75 ise geçilmiş sayılacak
    passed = True
    for section, percentage in section_percentages.items():
        if percentage < 75:
            passed = False
            break  # Bir bölümde kriter sağlanmazsa genel olarak başarısız

    if general_percentage < 75:
        passed = False

    result = "Passed" if passed else "Failed"

    # 5) Öğrenciye her bölümün yüzdesini ve genel puanı göstermek
    print("\n=== Bölüm Bazlı Sonuçlar ===")
    for section in sorted(section_percentages.keys()):
        print(f"Section {section}: % {section_percentages[section]:.2f}")
    print(f"Genel Puan: % {general_percentage:.2f} - Sonuç: {result}\n")

    # 6) Kullanıcının attempts bilgisini güncelleme
    user.attempts += 1
    user.last_attempt_date = datetime.now()
    if user.attempts == 1:
        user.score1 = general_percentage
    elif user.attempts == 2:
        user.score2 = general_percentage
        user.score_avg = (user.score1 + user.score2) / 2

    db.commit()

    # 7) Exam kaydı oluşturma
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

    # 8) ExamAnswer kayıtlarını oluşturma
    for section, qs in selected_questions.items():
        for q in qs:
            ans = db.query(Answer).filter(Answer.question_id == q.id).first()
            if not ans:
                continue  # Cevap yoksa atla
            correct_answer = ans.correct_answer.strip().lower()
            user_answer = user_answers.get(q.id, "").strip().lower()
            is_correct = False

            if q.type in ['true_false', 'single_choice']:
                if user_answer == correct_answer:
                    is_correct = True
            elif q.type in ['multiple_choice', 'ordering']:
                correct_ans_set = set(a.strip().lower() for a in correct_answer.split(','))
                user_ans_set = set(a.strip().lower() for a in user_answer.split(','))
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

    # 9) İstatistikleri güncelleme
    update_statistics(db, user.school_id, user.class_name, section_correct, section_wrong, section_scores)

    print("Exam Finished.\n")


