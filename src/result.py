# result.py

from utils import read_json
import os

ANSWERS_FILE = 'data/answers/answers.json'

class Result:
    def __init__(self, user, user_answers, used_question_ids, total_sections):
        self.user = user
        self.user_answers = user_answers
        self.correct_answers = read_json(ANSWERS_FILE)
        self.section_scores = {}
        self.total_score = 0
        self.passed = False
        self.used_question_ids = used_question_ids
        self.total_sections = total_sections 
            
    def calculate_results(self):
        print("\n=== Sınav Sonuçları ===")
        
        # Tüm soru bilgilerini yükle
        all_questions = self.load_all_questions()

        # Bölüm bazında toplam puanları hesapla
        section_total_points = {section: 0 for section in range(1, self.total_sections + 1)}
        for qid in self.used_question_ids:
            question_info = self.get_question_info(qid, all_questions)
            if question_info:
                section = question_info['section']
                points = question_info.get('points', 1)
                section_total_points[section] += points

        # Her soruyu değerlendir ve bölüm puanlarını güncelle
        for qid, user_answer in self.user_answers.items():
            correct_answer = self.correct_answers.get(qid)
            question_info = self.get_question_info(qid, all_questions)
            if not question_info:
                print(f"Soru ID {qid} bilgisi bulunamadı.")
                continue
            if correct_answer is None:
                print(f"Hata: Soru ID {qid} için doğru cevap bulunamadı.")
                continue
            section = question_info['section']
            points = question_info.get('points', 1)
            max_score_per_question = points  # Her soru için maksimum puan

            # Soru puanını başlangıçta 0 olarak ata
            question_score = 0

            # Soru tipi ve seçenek sayısına göre puanlama
            question_type = question_info['type']
            if question_type == 'multiple_choice':
                total_options = len(question_info.get('options', []))
                correct_set = set(correct_answer) if isinstance(correct_answer, list) else {correct_answer}
                user_set = set(user_answer) if isinstance(user_answer, list) else {user_answer}

                true_positives = user_set & correct_set
                false_positives = user_set - correct_set

                total_correct = len(correct_set)
                points_per_correct = points / total_correct if total_correct > 0 else 0
                points_per_wrong = -1 / (total_options - 1) * points if total_options > 1 else 0

                correct_point = len(true_positives) * points_per_correct
                wrong_penalty = len(false_positives) * points_per_wrong

                question_score = correct_point + wrong_penalty

                # Soru puanını sınırla
                question_score = max(question_score, 0)  # Negatif puanları sıfırla

            elif question_type == 'single_choice':
                # Tek seçimli sorularda ceza uygulanmaz
                if self.check_answer(user_answer, correct_answer):
                    question_score = points  # Doğru cevap için tam puan
                else:
                    question_score = 0  # Yanlış cevap için puan 0

            elif question_type == 'true_false':
                # Doğru/Yanlış sorularında ceza uygulanmaz
                if self.check_answer(user_answer, correct_answer):
                    question_score = points  # Doğru cevap için tam puan
                else:
                    question_score = 0  # Yanlış cevap için puan 0

            else:
                print(f"Desteklenmeyen soru tipi: {question_type}")
                continue

            # Bölüm puanlarını güncelle
            if section not in self.section_scores:
                self.section_scores[section] = {'earned': 0, 'total': 0}
            self.section_scores[section]['earned'] += question_score
            self.section_scores[section]['total'] += max_score_per_question

            # Hesaplama detaylarını ekrana yazdırın
            print(f"Soru ID: {qid}, Bölüm: {section}, Soru Tipi: {question_type}, Puan: {points}, Kazanılan: {question_score}")

        # Tamamlanmayan bölümler için puanları 0 olarak ekle
        for section in range(1, self.total_sections + 1):
            if section not in self.section_scores:
                self.section_scores[section] = {'earned': 0, 'total': section_total_points.get(section, 0)}
                print(f"Bölüm {section}: Henüz tamamlanmadı. Puan: 0")

        # Bölüm başarı yüzdelerini ve toplam puanı hesapla
        total_earned = 0
        total_possible = 0
        for section, scores in sorted(self.section_scores.items()):
            earned = scores['earned']
            total = scores['total']
            percentage = (earned / total) * 100 if total > 0 else 0
            print(f"Bölüm {section}: {percentage:.2f}% başarı")
            total_earned += earned
            total_possible += total

        self.total_score = (total_earned / total_possible) * 100 if total_possible > 0 else 0
        print(f"\nToplam Başarı Yüzdesi: {self.total_score:.2f}%")

        # Başarı durumunu belirle
        self.passed = self.check_pass_fail()
        if self.passed:
            print("Tebrikler, sınavı geçtiniz!")
        else:
            print("Maalesef, sınavı geçemediniz.")

        # Kullanıcı skorlarını güncelle
        self.update_user_scores()

    def load_all_questions(self):
        from question import QuestionManager
        qm = QuestionManager()
        all_questions = {}
        for section, filename in qm.section_files.items():
            file_path = os.path.join('data/questions/', filename)
            if os.path.exists(file_path):
                questions = read_json(file_path)
                for q in questions:
                    all_questions[str(q['id'])] = q  # ID'leri string yapıyoruz
        return all_questions

    def get_question_info(self, question_id, all_questions):
        return all_questions.get(str(question_id))

    def check_answer(self, user_answer, correct_answer):
        """Kullanıcının cevabını doğru cevapla karşılaştırır."""
        if user_answer is None or correct_answer is None:
            return False

        if isinstance(correct_answer, list):
            if not isinstance(user_answer, list):
                return False
            return set(user_answer) == set(correct_answer)
        else:
            # Kullanıcı cevabını ve doğru cevabı güvenli bir şekilde işlemek
            user_processed = user_answer.strip().lower() if isinstance(user_answer, str) else ''
            correct_processed = correct_answer.strip().lower() if isinstance(correct_answer, str) else ''
            return user_processed == correct_processed

    def check_pass_fail(self):
        """Kullanıcının sınavı geçip geçmediğini kontrol eder."""
        for section, scores in self.section_scores.items():
            percentage = (scores['earned'] / scores['total']) * 100 if scores['total'] > 0 else 0
            if percentage < 75:
                return False
        overall_pass = self.total_score >= 75
        return overall_pass

    def update_user_scores(self):
        """
        Kullanıcının skorlarını günceller ve kaydeder.
        """
        # Kullanıcının sınav giriş sayısına göre skoru güncelle
        if self.user.attempts == 1:
            self.user.score1 = self.total_score
        elif self.user.attempts == 2:
            self.user.score2 = self.total_score
            # Ortalama skoru hesapla
            if self.user.score1 is not None:
                self.user.score_avg = (self.user.score1 + self.user.score2) / 2
            else:
                self.user.score_avg = self.user.score2
        else:
            print("Kullanıcının sınava girme hakkı kalmadı.")

        # Kullanıcı verilerini kaydet
        self.user.save_user()
