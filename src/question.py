# src/question.py

import os
from utils import read_json, write_json, get_next_question_id

QUESTIONS_FOLDER = 'data/questions/'
ANSWERS_FILE = 'data/answers/answers.json'

class QuestionManager:
    def __init__(self):
        self.question_types = {
            'true_false': 'true_false_questions.json',
            'single_choice': 'single_choice_questions.json',
            'multiple_choice': 'multiple_choice_questions.json'
        }

    def add_question(self):
        """Yeni bir soru ekler."""
        print("\n=== Yeni Soru Ekle ===")
        question_type = input("Soru tipi (true_false, single_choice, multiple_choice): ").strip().lower()
        if question_type not in self.question_types:
            print("Geçersiz soru tipi.")
            return

        section_input = input("Bölüm numarası (1-4): ").strip()
        try:
            section = int(section_input)
            if section < 1 or section > 4:
                raise ValueError
        except ValueError:
            print("Geçersiz bölüm numarası. Lütfen 1 ile 4 arasında bir sayı giriniz.")
            return

        question_text = input("Soru metni: ").strip()
        points_input = input("Soru puanı: ").strip()
        try:
            points = float(points_input)
            if points <= 0:
                raise ValueError
        except ValueError:
            print("Geçersiz puan. Lütfen pozitif bir sayı giriniz.")
            return

        if question_type == 'true_false':
            options = ["Doğru", "Yanlış"]
        else:
            options_input = input("Seçenekleri virgülle ayırarak girin: ").strip()
            options = [opt.strip() for opt in options_input.split(',')]
            if len(options) < 2:
                print("En az iki seçenek girmeniz gerekmektedir.")
                return

        correct_answer_input = input("Doğru cevap(lar) (birden fazla ise virgülle ayırın): ").strip()
        if question_type == 'multiple_choice':
            correct_answer = [ans.strip() for ans in correct_answer_input.split(',')]
            if not correct_answer:
                print("En az bir doğru cevap girmeniz gerekmektedir.")
                return
        else:
            correct_answer = correct_answer_input.strip()
            if not correct_answer:
                print("Doğru cevap girmeniz gerekmektedir.")
                return

        # Otomatik ID ataması
        question_id = get_next_question_id(question_type)

        question = {
            'id': question_id,
            'section': section,
            'question': question_text,
            'points': points
        }
        if question_type != 'true_false':
            question['options'] = options

        # Soruyu dosyaya ekle
        file_path = os.path.join(QUESTIONS_FOLDER, self.question_types[question_type])
        questions = []
        if os.path.exists(file_path):
            questions = read_json(file_path)
        questions.append(question)
        write_json(questions, file_path)

        # Doğru cevabı answers.json dosyasına ekle
        answers = {}
        if os.path.exists(ANSWERS_FILE):
            answers = read_json(ANSWERS_FILE)
        answers[str(question_id)] = correct_answer
        write_json(answers, ANSWERS_FILE)

        print(f"Soru eklendi. Soru ID: {question_id}")

    def list_questions(self, question_type):
        """Belirtilen tipteki veya tüm soruları listeler."""
        question_type = question_type.lower()
        if question_type != 'all' and question_type not in self.question_types:
            print("Geçersiz soru tipi.")
            return

        if question_type == 'all':
            print("\n=== Tüm Sorular ===")
            for qtype, filename in self.question_types.items():
                file_path = os.path.join(QUESTIONS_FOLDER, filename)
                if not os.path.exists(file_path):
                    print(f"\n=== {qtype.capitalize()} Soruları ===")
                    print("Soru dosyası bulunamadı.")
                    continue

                questions = read_json(file_path)
                print(f"\n=== {qtype.capitalize()} Soruları ===")
                if not questions:
                    print("Hiç soru bulunmamaktadır.")
                    continue

                for q in questions:
                    print(f"ID: {q['id']}, Bölüm: {q['section']}, Soru: {q['question']}, Puan: {q['points']}")
                    if 'options' in q:
                        for idx, option in enumerate(q['options'], 1):
                            print(f"   {idx}. {option}")
        else:
            file_path = os.path.join(QUESTIONS_FOLDER, self.question_types[question_type])
            if not os.path.exists(file_path):
                print("Soru dosyası bulunamadı.")
                return

            questions = read_json(file_path)
            print(f"\n=== {question_type.capitalize()} Soruları ===")
            if not questions:
                print("Hiç soru bulunmamaktadır.")
                return

            for q in questions:
                print(f"ID: {q['id']}, Bölüm: {q['section']}, Soru: {q['question']}, Puan: {q['points']}")
                if 'options' in q:
                    for idx, option in enumerate(q['options'], 1):
                        print(f"   {idx}. {option}")

    def delete_question(self, question_id):
        """Belirtilen ID'ye sahip soruyu siler."""
        found = False
        for qtype, filename in self.question_types.items():
            file_path = os.path.join(QUESTIONS_FOLDER, filename)
            if os.path.exists(file_path):
                questions = read_json(file_path)
                new_questions = [q for q in questions if q['id'] != question_id]
                if len(questions) != len(new_questions):
                    write_json(new_questions, file_path)
                    found = True
                    print(f"Soru ID {question_id} silindi.")
                    break
        if not found:
            print(f"Soru ID {question_id} bulunamadı.")

        # Cevaplardan da sil
        if os.path.exists(ANSWERS_FILE):
            answers = read_json(ANSWERS_FILE)
            if str(question_id) in answers:
                del answers[str(question_id)]
                write_json(answers, ANSWERS_FILE)

    def update_question(self, question_id):
        """Belirtilen ID'ye sahip soruyu günceller."""
        found = False
        for qtype, filename in self.question_types.items():
            file_path = os.path.join(QUESTIONS_FOLDER, filename)
            if os.path.exists(file_path):
                questions = read_json(file_path)
                for q in questions:
                    if q['id'] == question_id:
                        print(f"\n=== Soru ID {question_id} Güncelleme ===")
                        print(f"Mevcut Soru Metni: {q['question']}")
                        new_question_text = input("Yeni soru metni (boş bırakılırsa aynı kalır): ").strip()
                        if new_question_text:
                            q['question'] = new_question_text

                        print(f"Mevcut Puan: {q['points']}")
                        new_points_input = input("Yeni puan (boş bırakılırsa aynı kalır): ").strip()
                        if new_points_input:
                            try:
                                new_points = float(new_points_input)
                                if new_points <= 0:
                                    raise ValueError
                                q['points'] = new_points
                            except ValueError:
                                print("Geçersiz puan. Puan güncellenmedi.")

                        if qtype != 'true_false':
                            print(f"Mevcut Seçenekler: {', '.join(q['options'])}")
                            options_input = input("Yeni seçenekler (virgülle ayırarak girin, boş bırakılırsa aynı kalır): ").strip()
                            if options_input:
                                new_options = [opt.strip() for opt in options_input.split(',')]
                                if len(new_options) < 2:
                                    print("En az iki seçenek girmeniz gerekmektedir. Seçenekler güncellenmedi.")
                                else:
                                    q['options'] = new_options
                                    # Doğru cevabı da güncellemek gerekebilir
                                    correct_answer_input = input("Yeni doğru cevap(lar) (birden fazla ise virgülle ayırın, boş bırakılırsa aynı kalır): ").strip()
                                    if correct_answer_input:
                                        if qtype == 'multiple_choice':
                                            new_correct_answer = [ans.strip() for ans in correct_answer_input.split(',')]
                                        else:
                                            new_correct_answer = correct_answer_input.strip()
                                        # Doğru cevabı answers.json dosyasından güncelle
                                        answers = {}
                                        if os.path.exists(ANSWERS_FILE):
                                            answers = read_json(ANSWERS_FILE)
                                        answers[str(question_id)] = new_correct_answer
                                        write_json(answers, ANSWERS_FILE)
                        write_json(questions, file_path)
                        print(f"Soru ID {question_id} güncellendi.")
                        found = True
                        break
                if found:
                    break
        if not found:
            print(f"Soru ID {question_id} bulunamadı.")
