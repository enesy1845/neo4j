# migrate_questions.py
import json
from pathlib import Path
from tools.database import get_db
from tools.models import Question, Answer
from sqlalchemy.orm import Session

QUESTIONS_DIR = Path("questions")           # "questions_section1.json" vb. buradaysa
ANSWERS_FILE = Path("answers/answers.json") # "answers.json" buradaysa

def load_json(filepath):
    with open(filepath, 'r', encoding='utf-8') as f:
        return json.load(f)

def questions_already_migrated(db: Session) -> bool:
    """ Eğer veritabanında en az 1 soru varsa, tekrar migrate etmeyelim. """
    existing = db.query(Question).first()
    return existing is not None

def main():
    with next(get_db()) as db:
        if questions_already_migrated(db):
            print("Questions already migrated. Skipping.")
            return

        # 1) Soru ekleme
        for section in range(1, 5):
            q_file = QUESTIONS_DIR / f"questions_section{section}.json"
            if not q_file.exists():
                print(f"{q_file} not found, skipping.")
                continue

            q_data = load_json(q_file)
            questions_list = q_data.get("questions", [])

            for q_item in questions_list:
                ext_id = q_item["id"]  # JSON’daki "id", bizde external_id olacak

                # Aynı external_id ile soru var mı kontrol
                existing_q = db.query(Question).filter(Question.external_id == ext_id).first()
                if existing_q:
                    # Dilerseniz update mantığı veya sadece skip
                    print(f"Question with external_id={ext_id} already exists. Skipping.")
                    continue
                
                new_q = Question(
                    external_id=ext_id,
                    section=q_item["section"],
                    question=q_item["question"],
                    points=q_item["points"],
                    type=q_item["type"]
                )
                db.add(new_q)
                db.commit()
                db.refresh(new_q)

        # 2) Cevap ekleme
        a_data = load_json(ANSWERS_FILE)  # answers.json -> { "Q1": "a", "Q2": "true" }
        # Tüm soruları çek
        questions_in_db = db.query(Question).all()

        for q in questions_in_db:
            ext_id = q.external_id
            if ext_id in a_data:
                ans_value = a_data[ext_id]
                # Eğer birden fazla cevapsa list -> string yapabilirsiniz
                if isinstance(ans_value, list):
                    correct_answer = ",".join(str(a).strip() for a in ans_value)
                else:
                    correct_answer = str(ans_value).strip()
                
                # Cevap kaydı -> question_id = q.id (UUID)
                new_a = Answer(
                    question_id=q.id,
                    correct_answer=correct_answer
                )
                db.add(new_a)
                db.commit()
            else:
                print(f"No answer found for question external_id={ext_id}")

        print("Migration completed successfully.")

if __name__ == "__main__":
    main()
