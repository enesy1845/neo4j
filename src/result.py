# result.py

from utils import read_json
import os

ANSWERS_FILE = 'data/answers/answers.json'

class Result:
    def __init__(self, user, user_answers, used_question_ids, total_sections):
        """
        Result sınıfı, sınav sonuçlarını hesaplama ve yönetme işlemlerini yapar.

        Args:
            user (User): Sınava katılan kullanıcı nesnesi.
            user_answers (dict): Kullanıcının verdiği cevaplar.
            used_question_ids (list): Kullanılan soru ID'leri.
            total_sections (int): Sınavdaki toplam bölüm sayısı.
        """      
        self.user = user
        self.user_answers = user_answers
        self.correct_answers = read_json(ANSWERS_FILE)
        self.section_scores = {}
        self.total_score = 0
        self.passed = False
        self.used_question_ids = used_question_ids
        self.total_sections = total_sections        # Toplam bölüm sayısı
        
    def calculate_results(self):
        """
        Sonuçları hesaplar ve kullanıcıya gösterir.
        
        Kullanıcının her bölüme göre doğru cevaplarını değerlendirir, bölüm başarı 
        yüzdelerini ve toplam başarı yüzdesini hesaplar. Sonuçlar kullanıcının 
        sınavı geçip geçmediğini belirler.
        """
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
            question_info = self.get_question_info(int(qid), all_questions)
            if not question_info:
                print(f"Soru ID {qid} bilgisi bulunamadı.")
                continue
            section = question_info['section']
            points = question_info.get('points', 1)
            max_score_per_question = points  # Her soru için maksimum puan

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
                total_options = len(question_info.get('options', []))
                if self.check_answer(user_answer, correct_answer):
                    question_score = 1 * points  # Doğru cevap için 1 * points puan
                else:
                    wrong_penalty = -1 / (total_options - 1) * points if total_options > 1 else 0
                    question_score = wrong_penalty
                    question_score = max(question_score, 0)  # Negatif puanları sıfırla
            else:  # true_false
                total_options = 2  # Doğru/Yanlış soruları için 2 seçenek var
                if self.check_answer(user_answer, correct_answer):
                    question_score = 1 * points  # Doğru cevap için 1 * points puan
                else:
                    wrong_penalty = -1 / (total_options - 1) * points
                    question_score = wrong_penalty
                    question_score = max(question_score, 0)  # Negatif puanları sıfırla

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
        """
        Tüm soruları yükler ve soru tiplerine göre gruplar.

        Returns:
            dict: Her soru tipi için JSON dosyalarından okunan soruların listesi.
        """
        from question import QuestionManager
        qm = QuestionManager()
        all_questions = {}
        for qtype, filename in qm.question_types.items():
            file_path = 'data/questions/' + filename
            if os.path.exists(file_path):
                questions = read_json(file_path)
                for q in questions:
                    q['type'] = qtype
                all_questions[qtype] = questions
        return all_questions

    def get_question_info(self, question_id, all_questions):
        """
        Soru ID'sine göre soru bilgilerini getirir.

        Args:
            question_id (int): Bilgisi getirilecek soru ID'si.
            all_questions (dict): Tüm soruları içeren sözlük.

        Returns:
            dict or None: Soru bilgileri, bulunamazsa None.
        """
        for qtype, questions in all_questions.items():
            for q in questions:
                if q['id'] == question_id:
                    return q
        return None

    def check_answer(self, user_answer, correct_answer):
        """
        Kullanıcının cevabını doğru cevapla karşılaştırır.

        Args:
            user_answer (str or list): Kullanıcının verdiği cevap.
            correct_answer (str or list): Doğru cevap.

        Returns:
            bool: Kullanıcı cevabı doğruysa True, değilse False.
        """
        if isinstance(correct_answer, list):
            return set(user_answer) == set(correct_answer)
        else:
            return user_answer.strip().lower() == correct_answer.strip().lower()

    def check_pass_fail(self):
        """
        Kullanıcının sınavı geçip geçmediğini kontrol eder.

        Returns:
            bool: Kullanıcı sınavı geçtiyse True, geçemediyse False.
        """
        for section, scores in self.section_scores.items():
            percentage = (scores['earned'] / scores['total']) * 100 if scores['total'] > 0 else 0
            if percentage < 75:
                return False
        overall_pass = self.total_score >= 75
        return overall_pass

    def update_user_scores(self):
        """
        Kullanıcının skorlarını günceller ve kaydeder.
        
        Kullanıcının puanlarını kullanıcı nesnesine ekler ve güncel veriyi kaydeder.
        """
        self.user.scores.append({
            'total_score': self.total_score,
            'section_scores': self.section_scores
        })
        self.user.save_user()
