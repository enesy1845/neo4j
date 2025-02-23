# migrate_questions.py
import json
from pathlib import Path
from uuid import uuid4
from tools.database import get_db, init_db

# Kaynak dosya yolları
QUESTIONS_DIR = Path("questions")            # Örn: "questions_section1.json" ...
ANSWERS_FILE = Path("answers/answers.json")    # Örn: "answers.json"

def load_json(filepath: Path):
    with open(filepath, 'r', encoding='utf-8') as f:
        return json.load(f)

def questions_already_migrated(session) -> bool:
    result = session.run("MATCH (q:Question) RETURN q LIMIT 1")
    return result.single() is not None

def main():
    session = get_db()
    try:
        init_db()  # Constraint ve index'leri oluşturuyoruz

        if questions_already_migrated(session):
            print("Questions already migrated. Skipping.")
            return

        # 1) Cevapları yükle
        if not ANSWERS_FILE.exists():
            print(f"Answers file '{ANSWERS_FILE}' not found. Can't set correct answers.")
            answers_data = {}
        else:
            answers_data = load_json(ANSWERS_FILE)  # { "q_ext_id": cevap }
            
        # 2) Her bölüm için soru dosyalarını işle
        for section in range(1, 5):
            q_file = QUESTIONS_DIR / f"questions_section{section}.json"
            if not q_file.exists():
                print(f"{q_file} not found, skipping.")
                continue
            q_data = load_json(q_file)
            questions_list = q_data.get("questions", [])
            if not questions_list:
                print(f"No questions found in {q_file}, skipping.")
                continue

            for q_item in questions_list:
                ext_id = q_item["id"]
                # Benzersiz soru düğümü oluştur
                question_id = str(uuid4())
                cypher_create_question = """
                CREATE (q:Question {
                    id: $id,
                    external_id: $external_id,
                    section: $section,
                    question: $question,
                    points: $points,
                    type: $qtype
                })
                """
                params = {
                    "id": question_id,
                    "external_id": ext_id,
                    "section": q_item["section"],
                    "question": q_item["question"],
                    "points": q_item["points"],
                    "qtype": q_item["type"]
                }
                session.run(cypher_create_question, params)
                # Cevabı belirle
                raw_answer = answers_data.get(ext_id, None)
                options_list = q_item.get("options") or q_item.get("choices") or []
                if q_item["type"] == "true_false" and not options_list:
                    options_list = ["True", "False"]

                for opt in options_list:
                    is_corr = False
                    if raw_answer:
                        if isinstance(raw_answer, str) and opt.strip().lower() == raw_answer.strip().lower():
                            is_corr = True
                        elif isinstance(raw_answer, list) and opt.strip().lower() in [a.strip().lower() for a in raw_answer]:
                            is_corr = True
                    choice_id = str(uuid4())
                    cypher_create_choice = """
                    MATCH (q:Question {id: $question_id})
                    CREATE (c:Choice {
                        id: $choice_id,
                        choice_text: $choice_text,
                        is_correct: $is_correct,
                        correct_position: $correct_position
                    })
                    CREATE (q)-[:HAS_CHOICE]->(c)
                    """
                    params_choice = {
                        "question_id": question_id,
                        "choice_id": choice_id,
                        "choice_text": opt,
                        "is_correct": is_corr,
                        "correct_position": None
                    }
                    session.run(cypher_create_choice, params_choice)
                print(f"Migrated Q: {ext_id} ({q_item['question'][:30]}...)")
        print("Migration completed successfully.")
    finally:
        session.close()

if __name__ == "__main__":
    main()
