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

    def start_exam(self):
        """Sınavı başlatır."""
        try:
            clear_screen()
            self.user.increment_attempts()
            self.start_time = time.time()
            self.end_time = self.start_time + self.duration

            # Zamanlayıcı thread'i başlat
            timer_thread = threading.Thread(target=self.timer)
            timer_thread.daemon = True
            timer_thread.start()
            print("Sınav başladı...")

            # Soruları yükle
            all_questions = self.load_questions()
            
            # Sınav boyunca kullanılacak soruların listesini hazırlıyoruz
            self.used_question_ids = set()

            # Her bölüm için soruları sun
            for section_number in range(1, self.sections + 1):
                if self.time_up:
                    print("\nSınav süresi doldu.")
                    break

                # Bölüm başlığı
                print(f"\n=== Bölüm {section_number} ===")
                if section_number != 1:
                    input(f"Bölüm {section_number} başlıyor. Devam etmek için Enter'a basınız...")

                # Bölüm için soruları seç
                section_questions = self.select_questions_for_section(all_questions, section_number)

                # Soruları sun
                # for question in section_questions:
                #     if self.time_up:
                #         print("\nSınav süresi doldu.")
                #         raise TimeUpException("Sınav süresi doldu.")
                #     self.present_question(question)
                index = 0
                while index < len(section_questions):
                    print(f"Soru {index + 1}/{len(section_questions)} ")
                    question = section_questions[index]
                    if self.time_up:
                        print("\nSınav süresi doldu.")
                        raise TimeUpException("Sınav süresi doldu.")
                    
                    # Fonksiyona sorunun indexini bildirerek çağırıyoruz
                    indexResult = self.present_question(question, index, section_questions, section_number)
                    # Eğer result'a bağlı bir işlem yapacaksak burada değerlendirebiliriz
                    print(f"Soru {index + 1}: Dönüş değeri: {indexResult}")
                    if indexResult=="n":
                        # Bir sonraki indexe geç
                        index += 1
                    elif indexResult=="p":
                        # Bir sonraki indexe geç
                        if index > 0:
                            index -= 1
                    elif indexResult=="e":
                        index = len(section_questions)+1
                    else:
                        index += 1
                    if index >= len(section_questions):
                        if input(f"\nBölüm {section_number} bittirmek istiyormusunuz? (E/H)").lower() == "h":
                            #indexin modunu len(section_questions) olarak al
                            index = index % len(section_questions)
                
            


                # Bölüm sonu mesajı
                if section_number < self.sections:
                    print(f"\nBölüm {section_number} bitti.")
                    input(f"Bölüm {section_number + 1}'e geçmek için Enter'a basınız...")
                else:
                    print(f"\nBölüm {section_number} bitti. Sınav sona erdi.")

        except TimeUpException as tue:
            print("\nSınav süresi doldu!")
        except Exception as e:
            print(f"\nBeklenmeyen bir hata oluştu: {e}")
        finally:
            # Sınavı sonlandır
            self.end_exam()

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
        """Tüm soruları yükler ve bölüm numarasına göre gruplar."""
        all_questions = {}
        for section, filename in self.question_manager.section_files.items():
            file_path = os.path.join('data/questions/', filename)
            if os.path.exists(file_path):
                questions = read_json(file_path)
                # Her sorunun 'section' ve 'type' bilgisi zaten mevcut
                all_questions[section] = questions
        return all_questions

    def select_questions_for_section(self, all_questions, section_number):
        """Her bölüm için soruları seçer."""
        section_questions = []
        # Öncelikle her soru tipinden birer tane alıyoruz
        question_types = ['true_false', 'single_choice', 'multiple_choice']
        for qtype in question_types:
            available_questions = [
                q for q in all_questions.get(section_number, [])
                if q['id'] not in self.used_question_ids and q['type'] == qtype
            ]
            if available_questions:
                question = random.choice(available_questions)
                section_questions.append(question)
                self.used_question_ids.add(question['id'])
            else:
                print(f"Uyarı: {qtype} tipi için Bölüm {section_number} de yeterli soru yok.")

        # Kalan soruları rastgele seçiyoruz
        remaining_needed = 5 - len(section_questions)
        if remaining_needed > 0:
            all_available_questions = [
                q for q in all_questions.get(section_number, [])
                if q['id'] not in self.used_question_ids
            ]
            if len(all_available_questions) < remaining_needed:
                print(f"Uyarı: Bölüm {section_number} için yeterli sayıda soru yok.")
            else:
                additional_questions = random.sample(all_available_questions, remaining_needed)
                section_questions.extend(additional_questions)
                for q in additional_questions:
                    self.used_question_ids.add(q['id'])

        # Soruların sırasını karıştıralım
        random.shuffle(section_questions)
        return section_questions

    def present_question(self, question, index, section_questions, section_number):
        """Kullanıcıya soruyu sunar ve cevabını alır."""
        while True:
            clear_screen()
            try:
                keys = list(self.answers)
                key = keys[(section_number-1) * 5 + index]

                if isinstance(self.answers[key], list):  # Diziyi kontrol et
                    for item in self.answers[key]:
                        print(item)
                else:
                    print(self.answers[key])  # Dizi değilse direkt yazdır
            except:
                pass
            try:
                print(f"Soru {index + 1}/{len(section_questions)} ")
                
                remaining_time = int(self.end_time - time.time())
                if remaining_time <= 0:
                    print("Sınav süresi doldu!")
                    raise TimeUpException("Sınav süresi doldu.")
                mins, secs = divmod(remaining_time, 60)
                time_format = '{:02d}:{:02d}'.format(mins, secs)
                print(f"Kalan Süre: {time_format}\n")

                print(f"Soru {'index'}: {question['question']}")
                if 'options' in question:
                    for idx, option in enumerate(question['options'], 1):
                        print(f"{idx}. {option}")
                if question['type'] == 'multiple_choice':
                    print("Birden fazla seçeneği seçmek için numaraları virgülle ayırın (örneğin: 1,3,4)")
                elif question['type'] == 'single_choice':
                    print("Cevabınızı seçenek numarası olarak giriniz.")
                else:
                    print("1. Doğru")
                    print("2. Yanlış")
                
                # Kalan süreyi güncellemek için hızlıca sleep etmeyelim
                # Kullanıcıdan cevap al
                user_input = input("((N)ext,(P)rev,(E)nd to) Cevabınız: ")

                if self.is_time_up():
                    print("\nSınav süresi doldu!")
                    raise TimeUpException("Sınav süresi doldu.")

                if not user_input.strip():
                    print("\nLütfen bir cevap giriniz.")
                    input("Devam etmek için Enter tuşuna basın...")
                    continue  # Aynı soruyu tekrar sun
                if user_input.lower() != 'p' and user_input.lower() != 'n'and user_input.lower() != 'e':
                    # user_input 'p' VEYA 'n' DEĞİLSE bu blok çalışır
                    answers = self.process_input(user_input.strip(), question)
                    self.answers[str(question['id'])] = answers
                    #self.current_question_number += 1  # Sayaç artırıldı
                else:   
                    return user_input.lower()
                    pass
                break

            except ValueError as ve:
                print(f"\nHata: {ve}")
                input("Devam etmek için Enter tuşuna basın...")
                continue  # Aynı soruyu tekrar sun
            except TimeUpException as tue:
                # Sınav süresi dolduğunda işlemi sonlandır
                raise tue
            except Exception as e:
                print(f"\nBilinmeyen bir hata oluştu: {e}")
                input("Devam etmek için Enter tuşuna basın...")
                continue  # Aynı soruyu tekrar sun

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
        else:  # Doğru/Yanlış
            if user_input not in ['1', '2']:
                raise ValueError("Lütfen sadece 1 veya 2 giriniz.")
            return ["Doğru", "Yanlış"][int(user_input.strip()) - 1]

    def end_exam(self):
        """Sınavı sonlandırır ve sonuçları hesaplar."""
        print("\nSınav tamamlandı.")
        from result import Result
        try:
            result = Result(self.user, self.answers, self.used_question_ids, self.sections)
            result.calculate_results()
        except Exception as e:
            print(f"Sonuçlar hesaplanırken bir hata oluştu: {e}")
            input("Devam etmek için Enter tuşuna basın...")
