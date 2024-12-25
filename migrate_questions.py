# migrate_questions.py

import json
from pathlib import Path
from tools.database import get_db
from tools.models import Question, Answer
from sqlalchemy.orm import Session

QUESTIONS_DIR = Path("questions")
ANSWERS_FILE = Path("answers/answers.json")

def load_json(filepath):
    with open(filepath, 'r', encoding='utf-8') as f:
        return json.load(f)

def questions_already_migrated(db: Session):
    # Eğer veritabanında en az bir soru varsa, migrate işlemini tekrar yapma
    existing = db.query(Question).first()
    return existing is not None

def main():
    with next(get_db()) as db:
        if questions_already_migrated(db):
            print("Questions already migrated. Skipping.")
            return

        for section in range(1,5):
            q_file = QUESTIONS_DIR / f"questions_section{section}.json"
            if not q_file.exists():
                print(f"{q_file} not found, skipping.")
                continue
            q_data = load_json(q_file)
            questions_list = q_data.get("questions", [])

            # Her soruyu Question tablosuna kaydet
            for q in questions_list:
                # Artık q["id"] kullanmıyoruz. Veritabanı veya Python otomatik UUID atar.
                new_q = Question(
                    section=q["section"],
                    question=q["question"],
                    points=q["points"],
                    type=q["type"]
                )
                db.add(new_q)
            db.commit()

        # Answers ekle
        a_data = load_json(ANSWERS_FILE)
        # a_data: { question_id: cevap } 
        # Buradaki question_id json'da var. Biz soruları eklerken id set etmedik.
        # Bu nedenle question_id eşleşmesi yerine question metnine göre eşleşme yapabiliriz.
        # Ancak bu, veri yapısında zorluk çıkarır. Varsayım: JSON'daki question_id ler aslında 
        # orijinal soruların unique id'siydi. Bu durumda ya question metnine göre eşleşme yapmalı
        # ya da answers.json içeriğini orijinal question metinleriyle map etmeliyiz.
        # Kolaylık için a_data içindeki key'leri question metni ile eşleşecek hale getirelim.
        # Ancak elinizde question_id yoksa bu kısım zorlaşır.
        # Burada basitçe soruları question metnine göre eşleyeceğiz:
        # a_data: { "Soru metni": "cevap" }

        # answers.json'daki anahtar question_id yerine question text olsun.
        # Answers formatınızı buna göre güncelleyin. Örnek: { "Soru metni": "cevap" }

        # Eğer answers dosyası question_id bazlı ise, ya bu logic'i değiştirin
        # ya da migration'dan önce question id'leri sabit tutun.
        # Aşağıdaki kod question text'e göre eşleşecektir.

        # Cevap json'u örneğin:
        # {
        #   "Soru metni A": "a",
        #   "Soru metni B": "true"
        # }

        # Dolayısıyla question metnini baz alarak cevabı ekleyeceğiz.
        questions = db.query(Question).all()
        for q in questions:
            if q.question in a_data:
                ans_value = a_data[q.question]
                if isinstance(ans_value, list):
                    correct_answer = ",".join(ans.strip() for ans in ans_value)
                else:
                    correct_answer = ans_value.strip()
                new_a = Answer(
                    question_id=q.id,
                    correct_answer=correct_answer
                )
                db.add(new_a)
        db.commit()
        print("Migration completed successfully.")

if __name__ == "__main__":
    main()
