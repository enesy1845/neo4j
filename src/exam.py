# exam.py

import time
import os
import threading
import sys
import platform
from question import QuestionManager
from utils import clear_screen, read_json
import random

if platform.system() == 'Windows':
    import msvcrt
else:
    import select
    import tty
    import termios

class Exam:
    def __init__(self, user):
        self.user = user
        self.duration = 60  # Sınav süresi (saniye cinsinden)
        self.start_time = None
        self.end_time = None
        self.sections = 4  # 4 bölüm
        self.question_manager = QuestionManager()
        self.answers = {}  # Kullanıcının cevapları
        self.used_question_ids = set()  # Kullanılan soru ID'lerini takip etmek için

    def start_exam(self):
        """Sınavı başlatır."""
        clear_screen()
        print("Sınav başlıyor...")
        self.user.increment_attempts()
        self.start_time = time.time()
        self.end_time = self.start_time + self.duration

        # Soruları yükle
        all_questions = self.load_questions()

        # Sınav boyunca kullanılacak soruların listesini hazırlıyoruz
        self.used_question_ids = set()

        # Her bölüm için soruları sun
        for section_number in range(1, self.sections + 1):
            if self.is_time_up():
                print("\nSınav süresi doldu.")
                break

            # Bölüm başlığı
            print(f"\n=== Bölüm {section_number} ===")
            input(f"Bölüm {section_number} başlıyor. Devam etmek için Enter'a basınız...")

            # Bölüm için soruları seç
            section_questions = self.select_questions_for_section(all_questions)

            # Soruları sun
            for question in section_questions:
                if self.is_time_up():
                    print("\nSınav süresi doldu.")
                    break
                self.present_question(question)

            # Bölüm sonu mesajı
            if section_number < self.sections:
                print(f"\nBölüm {section_number} bitti.")
                input(f"Bölüm {section_number + 1}'e geçmek için Enter'a basınız...")
            else:
                print(f"\nBölüm {section_number} bitti. Sınav sona erdi.")

        # Sınavı sonlandır
        self.end_exam()
    def is_time_up(self):
        """Sınav süresinin dolup dolmadığını kontrol eder."""
        return time.time() >= self.end_time

    def load_questions(self):
        """Tüm soruları yükler ve soru tiplerine göre gruplar."""
        all_questions = {}
        # Tüm soru dosyalarını yükle
        for qtype, filename in self.question_manager.question_types.items():
            file_path = 'data/questions/' + filename
            if os.path.exists(file_path):
                questions = read_json(file_path)
                # Her soruya 'type' anahtarını ekliyoruz
                for q in questions:
                    q['type'] = qtype
                # Soruları doğrudan soru tipine göre grupluyoruz
                all_questions[qtype] = questions
        return all_questions

    def select_questions_for_section(self, all_questions):
        """Her bölüm için soruları seçer."""
        section_questions = []
        # Öncelikle her soru tipinden birer tane alıyoruz
        for qtype in ['true_false', 'single_choice', 'multiple_choice']:
            available_questions = [q for q in all_questions.get(qtype, []) if q['id'] not in self.used_question_ids]
            if available_questions:
                question = random.choice(available_questions)
                section_questions.append(question)
                self.used_question_ids.add(question['id'])
            else:
                print(f"Uyarı: {qtype} tipi için yeterli soru yok.")
        # Kalan soruları rastgele seçiyoruz
        remaining_needed = 5 - len(section_questions)
        all_available_questions = []
        for qtype in ['true_false', 'single_choice', 'multiple_choice']:
            all_available_questions.extend([q for q in all_questions.get(qtype, []) if q['id'] not in self.used_question_ids])
        if len(all_available_questions) < remaining_needed:
            print("Uyarı: Yeterli sayıda soru yok.")
        else:
            additional_questions = random.sample(all_available_questions, remaining_needed)
            section_questions.extend(additional_questions)
            for q in additional_questions:
                self.used_question_ids.add(q['id'])
        # Soruların sırasını karıştıralım
        random.shuffle(section_questions)
        return section_questions

    def present_question(self, question):
        """Kullanıcıya soruyu sunar ve cevabını alır."""
        user_input = ''
        while True:
            try:
                # Ekranı güncelle
                clear_screen()
                remaining_time = int(self.end_time - time.time())
                if remaining_time <= 0:
                    print("Sınav süresi doldu!")
                    return
                mins, secs = divmod(remaining_time, 60)
                time_format = '{:02d}:{:02d}'.format(mins, secs)
                print(f"Kalan Süre: {time_format}")
                print(f"\nSoru ID {question['id']}: {question['question']}")
                if 'options' in question:
                    for idx, option in enumerate(question['options'], 1):
                        print(f"{idx}. {option}")
                if question['type'] == 'multiple_choice':
                    print("Birden fazla seçeneği seçmek için numaraları virgülle ayırın (örneğin: 1,3,4)")
                    print(f"Cevabınız: {user_input}", end='', flush=True)
                elif question['type'] == 'single_choice':
                    print("Cevabınızı seçenek numarası olarak giriniz.")
                    print(f"Cevabınız: {user_input}", end='', flush=True)
                else:
                    print("1. Doğru")
                    print("2. Yanlış")
                    print(f"Cevabınız: {user_input}", end='', flush=True)

                # Non-blocking input
                char = self.get_char()
                if char:
                    if char == '\r' or char == '\n':
                        # Enter tuşuna basıldı, girişi işle
                        answers = self.process_input(user_input.strip(), question)
                        self.answers[str(question['id'])] = answers
                        break
                    elif char == '\x08' or char == '\x7f':
                        # Backspace tuşu
                        user_input = user_input[:-1]
                    else:
                        user_input += char
                time.sleep(0.1)  # Ekranı çok hızlı yenilememek için

            except ValueError as ve:
                print(f"\nHata: {ve}")
                input("Devam etmek için Enter tuşuna basın...")
                user_input = ''
            except Exception as e:
                print(f"\nBilinmeyen bir hata oluştu: {e}")
                input("Devam etmek için Enter tuşuna basın...")
                user_input = ''

    def get_char(self):
        """Kullanıcıdan non-blocking şekilde karakter okur."""
        if platform.system() == 'Windows':
            if msvcrt.kbhit():
                char = msvcrt.getwch()
                return char
        else:
            # Unix tabanlı sistemler için
            import sys, select, tty, termios
            fd = sys.stdin.fileno()
            old_settings = termios.tcgetattr(fd)
            try:
                tty.setcbreak(sys.stdin.fileno())
                dr, dw, de = select.select([sys.stdin], [], [], 0)
                if dr:
                    char = sys.stdin.read(1)
                    return char
            finally:
                termios.tcsetattr(fd, termios.TCSADRAIN, old_settings)
        return None

    def process_input(self, user_input, question):
        """Kullanıcının girdiği cevabı işler."""
        if question['type'] == 'multiple_choice':
            indices = user_input.split(',')
            answers = []
            for idx_str in indices:
                idx_str = idx_str.strip()
                if not idx_str.isdigit():
                    raise ValueError("Lütfen seçenek numaralarını giriniz.")
                idx = int(idx_str) - 1
                if idx < 0 or idx >= len(question['options']):
                    raise ValueError(f"Lütfen 1 ile {len(question['options'])} arasında bir sayı giriniz.")
                answers.append(question['options'][idx])
            return answers
        elif question['type'] == 'single_choice':
            if not user_input.isdigit():
                raise ValueError("Lütfen bir seçenek numarası giriniz.")
            idx = int(user_input.strip()) - 1
            if idx < 0 or idx >= len(question['options']):
                raise ValueError(f"Lütfen 1 ile {len(question['options'])} arasında bir sayı giriniz.")
            return question['options'][idx]
        else:  # True/False
            if user_input not in ['1', '2']:
                raise ValueError("Lütfen sadece 1 veya 2 giriniz.")
            idx = int(user_input.strip()) - 1
            return ["Doğru", "Yanlış"][idx]

    def end_exam(self):
        """Sınavı sonlandırır ve sonuçları hesaplar."""
        print("\nSınav tamamlandı.")
        from result import Result
        result = Result(self.user, self.answers)
        result.calculate_results()
