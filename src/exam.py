# exam.py

import time
import os
import threading
import sys
import platform
from question import QuestionManager
from utils import clear_screen, read_json
import random



class Exam:
    def __init__(self, user):
        self.user = user
        self.duration = 3600  # Sınav süresi (saniye cinsinden)
        self.start_time = None
        self.end_time = None
        self.sections = 4  # 4 bölüm
        self.question_manager = QuestionManager()
        self.answers = {}  # Kullanıcının cevapları
        self.used_question_ids = set()  # Kullanılan soru ID'lerini takip etmek için

    def start_exam(self):
        """Sınavı başlatır."""
        pass

        # Soruları yükle
        

        # Sınav boyunca kullanılacak soruların listesini hazırlıyoruz
        

        # Her bölüm için soruları sun
        

            # Bölüm başlığı
            

            # Bölüm için soruları seç
            

            # Soruları sun
            
            # Bölüm sonu mesajı
            

        # Sınavı sonlandır
        

    def is_time_up(self):
        """Sınav süresinin dolup dolmadığını kontrol eder."""
        pass

    def load_questions(self):
        """Tüm soruları yükler ve soru tiplerine göre gruplar."""
        pass
        # Tüm soru dosyalarını yükle
        
                # Her soruya 'type' anahtarını ekliyoruz
                
                # Soruları doğrudan soru tipine göre grupluyoruz
                

    def select_questions_for_section(self, all_questions):
        """Her bölüm için soruları seçer."""
        pass
        # Öncelikle her soru tipinden birer tane alıyoruz
        
        # Kalan soruları rastgele seçiyoruz
        
        # Soruların sırasını karıştıralım
        
    def present_question(self, question):
        """Kullanıcıya soruyu sunar ve cevabını alır."""
        pass

    def get_char(self):
        """Kullanıcıdan non-blocking şekilde karakter okur."""
        pass

    def process_input(self, user_input, question):
        """Kullanıcının girdiği cevabı işler."""
        pass

    def end_exam(self):
        """Sınavı sonlandırır ve sonuçları hesaplar."""
        pass
