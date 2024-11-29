# src/exam.py

import time
import os
import threading
import sys
import platform
from quiznexusai.question import QuestionManager
from quiznexusai.utils import (
    clear_screen,
    read_json,
    read_user_answers,
    write_user_answers,
    ANSWERS_FILE,
    CLASSES_FILE, 
    SCHOOLS_FILE
)
import random
import uuid
from datetime import datetime, timezone
from quiznexusai.result import Result

if platform.system() == 'Windows':
    import msvcrt
else:
    import select
    import tty
    import termios

class TimeUpException(Exception):
    pass

class Exam:
    def __init__(self, user):
        self.user = user
        self.duration = 180  # Sınav süresi (saniye cinsinden)
        self.start_time = None
        self.end_time = None
        self.sections = 4  # 4 bölüm
        self.question_manager = QuestionManager()
        self.answers = {}  # Kullanıcının cevapları
        self.used_question_ids = set()  # Kullanılan soru ID'lerini takip etmek için
        self.current_question_number = 1  # Soru sayacı
        self.time_up = False  # Zamanın dolup dolmadığını takip etmek için
        self.lock = threading.Lock()  # Thread güvenliği için kilit
        self.attempt_id = str(uuid.uuid4())  # Benzersiz deneme ID'si
        self.answers_record = []  # Her sorunun cevabını kaydetmek için
        self.correct_answers = read_json(ANSWERS_FILE, encrypted=True)  

    def start_exam(self):
        """Sınavı başlatır."""
        try:
            clear_screen()
            print("Sınav başlatılıyor...")
            self.user.increment_attempts()
            self.start_time = datetime.utcnow().isoformat()

            # Soruları yükle
            all_questions_by_section, all_questions_by_id = self.load_questions()
            
            # Sınav boyunca kullanılacak soru ID'lerini sıfırla
            self.used_question_ids = set()

            # Her bölüm için soruları sun
            for section_number in range(1, self.sections + 1):
                if self.time_up:
                    print("\nSınav süresi doldu.")
                    break

                # Bölüm başlığı
                print(f"\n=== Bölüm {section_number} ===")
                input(f"Bölüm {section_number} başlıyor. Devam etmek için Enter tuşuna basın...")
                
                # İlk bölüm başladığında zamanlayıcıyı başlat
                if section_number == 1:
                    self.end_time = time.time() + self.duration
                    timer_thread = threading.Thread(target=self.timer)
                    timer_thread.daemon = True
                    timer_thread.start()

                # Bölüm için soruları seç
                section_questions = self.select_questions_for_section(all_questions_by_section, section_number)

                # Soruları sun
                for question in section_questions:
                    if self.time_up:
                        print("\nSınav süresi doldu.")
                        raise TimeUpException("Sınav süresi doldu.")
                    self.present_question(question, section_number)  # Bölüm numarasını geç

                # Bölüm bitiş mesajı
                if section_number < self.sections:
                    print(f"\nBölüm {section_number} sona erdi.")
                    input(f"Bölüm {section_number + 1}'e geçmek için Enter tuşuna basın...")
                else:
                    print(f"\nBölüm {section_number} sona erdi. Sınav sona erdi.")

        except TimeUpException as tue:
            print("\nSınav süresi doldu!")
        except Exception as e:
            print(f"\nBeklenmeyen bir hata oluştu: {e}")
            input("Devam etmek için Enter tuşuna basın...")
        finally:
            # Sınavı bitir
            self.end_exam(all_questions_by_id)

    def timer(self):
        """Sınav süresini takip eder."""
        while True:
            with self.lock:
                remaining_time = self.end_time - time.time()
                if remaining_time <= 0:
                    self.time_up = True
                    break
            time.sleep(1)

    def is_time_up(self):
        """Sınav süresinin dolup dolmadığını kontrol eder."""
        with self.lock:
            return self.time_up or time.time() >= self.end_time

    def load_questions(self):
        """Tüm soruları yükler ve bölüm numarası ile soru ID'sine göre eşler."""
        all_questions_by_section = {}
        all_questions_by_id = {}
        qm = self.question_manager
        for section, filename in qm.section_files.items():
            file_path = os.path.join('data/questions/', filename)
            if os.path.exists(file_path):
                questions = read_json(file_path, encrypted=True)
                all_questions_by_section[section] = questions
                for q in questions:
                    all_questions_by_id[str(q['id'])] = q
        return all_questions_by_section, all_questions_by_id

    def select_questions_for_section(self, all_questions_by_section, section_number):
        """Her bölüm için soruları seçer."""
        section_questions = []
        questions_in_section = all_questions_by_section.get(section_number, [])

        if not questions_in_section:
            print(f"Uyarı: Bölüm {section_number} için soru bulunamadı.")
            return section_questions

        # Gerekli soru türleri
        required_types = ['true_false', 'single_choice', 'multiple_choice', 'ordering']

        # İlk olarak, her türden bir soru seç
        for qtype in required_types:
            available_questions = [
                q for q in questions_in_section
                if q['type'] == qtype and q['id'] not in self.used_question_ids
            ]
            if available_questions:
                question = random.choice(available_questions)
                section_questions.append(question)
                self.used_question_ids.add(question['id'])
            else:
                print(f"Uyarı: Bölüm {section_number} için '{qtype}' türünden yeterli soru yok.")

        # 5 soruya ulaşmak için kalan soruları rastgele seç
        remaining_needed = 5 - len(section_questions)

        if remaining_needed > 0:
            available_questions = [
                q for q in questions_in_section
                if q['id'] not in self.used_question_ids
            ]
            if len(available_questions) < remaining_needed:
                print(f"Uyarı: Bölüm {section_number} için 5 soruya ulaşmak adına yeterli soru yok.")
                remaining_needed = len(available_questions)
            additional_questions = random.sample(available_questions, remaining_needed)
            section_questions.extend(additional_questions)
            for q in additional_questions:
                self.used_question_ids.add(q['id'])

        # Soruları karıştır
        random.shuffle(section_questions)
        return section_questions

    def present_question(self, question, section_number):
        """Soruyu kullanıcıya sunar ve cevabını kaydeder."""
        while True:
            try:
                clear_screen()
                remaining_time = int(self.end_time - time.time())
                if remaining_time <= 0:
                    print("Sınav süresi doldu!")
                    raise TimeUpException("Sınav süresi doldu.")
                mins, secs = divmod(remaining_time, 60)
                time_format = '{:02d}:{:02d}'.format(mins, secs)
                print(f"Kalan Süre: {time_format}\n")

                print(f"Soru {self.current_question_number}: {question['question']}")
                if 'options' in question:
                    for idx, option in enumerate(question['options'], 1):
                        print(f"{idx}. {option}")
                if question['type'] == 'multiple_choice':
                    print("Birden fazla seçenek seçmek için numaraları virgülle ayırın (örn., 1,3,4)")
                elif question['type'] == 'single_choice':
                    print("Cevabınızı seçenek numarası olarak girin.")
                elif question['type'] == 'ordering':
                    print("Seçenekleri doğru sırayla numaralarla girin, virgülle ayırın (örn., 2,3,1,4)")
                else:
                    print("1. Doğru")
                    print("2. Yanlış")
                
                # Kullanıcının cevabını al
                user_input = input("Cevabınız: ")

                if self.is_time_up():
                    print("\nSınav süresi doldu!")
                    raise TimeUpException("Sınav süresi doldu.")

                if not user_input.strip():
                    print("\nLütfen bir cevap girin.")
                    input("Devam etmek için Enter tuşuna basın...")
                    continue  # Aynı soruyu tekrar sun

                answers = self.process_input(user_input.strip(), question)
                self.answers[str(question['id'])] = answers

                # Doğruluğu kontrol et ve kazanılan puanı hesapla
                is_correct = self.check_correctness(question['id'], answers)
                points_earned = self.calculate_points(question, is_correct)

                # Cevabı bölüm numarası ile kaydet
                self.answers_record.append({
                    "question_id": str(question['id']),
                    "section_number": section_number,  # Bölüm numarası
                    "user_answer": answers,
                    "is_correct": is_correct,
                    "points_earned": points_earned
                })

                self.current_question_number += 1  # Sayacı artır
                break

            except ValueError as ve:
                print(f"\nHata: {ve}")
                input("Devam etmek için Enter tuşuna basın...")
                continue  # Aynı soruyu tekrar sun
            except TimeUpException as tue:
                # Sınav süresi dolduğunda işlemi sonlandır
                raise tue
            except Exception as e:
                print(f"\nBeklenmeyen bir hata oluştu: {e}")
                input("Devam etmek için Enter tuşuna basın...")
                continue  # Aynı soruyu tekrar sun

    def process_input(self, user_input, question):
        """Kullanıcının cevabını işler."""
        if question['type'] == 'ordering':
            indices = user_input.split(',')
            if len(indices) != len(question['options']):
                raise ValueError("Lütfen doğru sayıda seçenek girin.")
            answers = []
            for idx_str in indices:
                idx_str = idx_str.strip()
                if not idx_str.isdigit():
                    raise ValueError("Lütfen geçerli seçenek numaraları girin.")
                idx = int(idx_str) - 1
                if idx < 0 or idx >= len(question['options']):
                    raise ValueError(f"Lütfen 1 ile {len(question['options'])} arasında bir sayı girin.")
                selected_option = question['options'][idx]
                answers.append(selected_option)
            return answers
        if question['type'] == 'multiple_choice':
            indices = user_input.split(',')
            answers = []
            for idx_str in indices:
                idx_str = idx_str.strip()
                if not idx_str.isdigit():
                    raise ValueError("Lütfen seçenek numaralarını virgülle ayırarak girin.")
                idx = int(idx_str) - 1
                if idx < 0 or idx >= len(question['options']):
                    raise ValueError(f"Lütfen 1 ile {len(question['options'])} arasında bir sayı girin.")
                # Seçilen seçeneğin metnini al
                if '. ' in question['options'][idx]:
                    selected_option = question['options'][idx].split('. ', 1)[1]
                else:
                    selected_option = question['options'][idx]
                answers.append(selected_option)
            return answers
        elif question['type'] == 'single_choice':
            if not user_input.isdigit():
                raise ValueError("Lütfen bir seçenek numarası girin.")
            idx = int(user_input.strip()) - 1
            if idx < 0 or idx >= len(question['options']):
                raise ValueError(f"Lütfen 1 ile {len(question['options'])} arasında bir sayı girin.")
            # Seçilen seçeneğin metnini al
            if '. ' in question['options'][idx]:
                selected_option = question['options'][idx].split('. ', 1)[1]
            else:
                selected_option = question['options'][idx]
            return selected_option
        else:  # Doğru/Yanlış
            if user_input not in ['1', '2']:
                raise ValueError("Lütfen sadece 1 veya 2 girin.")
            return ["Doğru", "Yanlış"][int(user_input.strip()) - 1]

    def check_correctness(self, question_id, user_answer):
        """Kullanıcının cevabının doğru olup olmadığını kontrol eder."""
        correct_answer = self.correct_answers.get(str(question_id))
        if not correct_answer:
            return False
        return self.check_answer(user_answer, correct_answer)

    def check_answer(self, user_answer, correct_answer):
        """Kullanıcının cevabını doğru cevapla karşılaştırır."""
        if user_answer is None or correct_answer is None:
            return False

        if isinstance(correct_answer, list):
            if not isinstance(user_answer, list):
                return False
            return set(user_answer) == set(correct_answer)
        else:
            # Kullanıcının cevabını ve doğru cevabı güvenli bir şekilde işle
            user_processed = user_answer.strip().lower() if isinstance(user_answer, str) else ''
            correct_processed = correct_answer.strip().lower() if isinstance(correct_answer, str) else ''
            return user_processed == correct_processed

    def calculate_points(self, question, is_correct):
        """Doğruluğa bağlı olarak kazanılan puanı hesaplar."""
        if is_correct:
            return question.get('points', 1)
        else:
            # Basitlik için negatif puan yok. Gerektiğinde ayarlanabilir.
            return 0

    def end_exam(self, all_questions_by_id):
        """Sınavı bitirir ve sonuçları hesaplar."""
        print("\nSınav tamamlandı.")
        try:
            result = Result(self.user, self.answers_record, self.used_question_ids, self.sections)
            result.calculate_results()
            # Sonuçları aldıktan sonra toplam puanı ve geçip geçmediğini ayarla
            self.total_score = result.total_score
            self.passed = result.passed
        except Exception as e:
            print(f"Sonuçları hesaplarken bir hata oluştu: {e}")
            input("Devam etmek için Enter tuşuna basın...")
            self.total_score = 0  # Varsayılan değer
            self.passed = False

        # Organize edilmiş bölümlerle sınav denemesini kaydet
        organized_sections = getattr(result, 'organized_sections', {})
        self.record_attempt(all_questions_by_id, organized_sections)

    def record_attempt(self, all_questions_by_id, organized_sections):
        """Sınav denemesini user_answers.json dosyasına kaydeder."""

        # Admin ve öğretmenleri denemeleri kaydetmekten hariç tut
        if self.user.role != 'user':
            return  # Admin veya öğretmen roller için denemeleri kaydetme

        user_answers_data = read_user_answers()

        # Sınıf adı ve okul adı al
        classes = read_json(CLASSES_FILE)
        schools = read_json(SCHOOLS_FILE)
        user_class = next((cls['class_name'] for cls in classes if cls['class_id'] == self.user.class_id), 'Unknown Class')
        school = next((sch['school_name'] for sch in schools if sch['school_id'] == self.user.school_id), 'Unknown School')

        attempt_record = {
            "attempt_id": self.attempt_id,
            "user_id": self.user.user_id,
            "name": self.user.name,
            "surname": self.user.surname,
            "phone_number": self.user.phone_number,
            "user_class": user_class,
            "school": school,
            "start_time": self.start_time,
            "end_time": datetime.now(timezone.utc).isoformat(),
            "sections": organized_sections,  # organized_sections'ı doğrudan ekle
            "total_score": self.total_score,
            "passed": self.passed
        }

        user_answers_data["attempts"].append(attempt_record)
        write_user_answers(user_answers_data)

    def calculate_total_score(self):
        """Tüm bölümlerden toplam puanı hesaplar."""
        # Artık kullanılmıyor çünkü 'Result' toplam puanı hesaplıyor
        pass

    def process_simulated_input(self, user_input, question):
        """Simüle edilmiş kullanıcı girişi için cevabı işler."""
        try:
            answers = self.process_input(user_input.strip(), question)
            self.answers[str(question['id'])] = answers
            # Doğruluğu kontrol et ve kazanılan puanı hesapla
            is_correct = self.check_correctness(question['id'], answers)
            points_earned = self.calculate_points(question, is_correct)
            # Cevabı kaydet
            self.answers_record.append({
                "question_id": str(question['id']),
                "user_answer": answers,
                "is_correct": is_correct,
                "points_earned": points_earned
            })
        except Exception as e:
            print(f"Soru ID {question['id']} işlenirken hata oluştu: {e}")
