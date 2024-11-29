# src/result.py

from quiznexusai.utils import read_json, ANSWERS_FILE, read_statistics, write_statistics, print_table
import os

class Result:
    def __init__(self, user, answers_record, used_question_ids, total_sections):
        self.user = user
        self.answers_record = answers_record  # Bu, sözlükler listesi olmalıdır
        self.correct_answers = read_json(ANSWERS_FILE, encrypted=True)  # Şifreli
        self.section_scores = {}
        self.total_score = 0
        self.passed = False
        self.used_question_ids = used_question_ids
        self.total_sections = total_sections
        self.organized_sections = {}  # Organize edilmiş bölümler

    def calculate_results(self):
        print("\n=== Sınav Sonuçları ===")

        # Tüm soru bilgilerini yükle
        all_questions = self.load_all_questions()

        # Her bölüm için toplam puanları hesapla
        section_total_points = {section: 0 for section in range(1, self.total_sections + 1)}
        for qid in self.used_question_ids:
            question_info = self.get_question_info(qid, all_questions)
            if question_info:
                section = question_info['section']
                points = question_info.get('points', 1)
                section_total_points[section] += points

        # Her soruyu değerlendir ve bölüm puanlarını güncelle
        for answer in self.answers_record:
            qid = answer["question_id"]
            user_answer = answer["user_answer"]
            correct_answer = self.correct_answers.get(str(qid))
            question_info = self.get_question_info(qid, all_questions)
            if not question_info:
                continue
            section = question_info['section']
            points = question_info.get('points', 1)
            max_score_per_question = points  # Soru başına maksimum puan

            # Soru puanını 0 olarak başlat
            question_score = 0

            # Soru türüne ve seçenek sayısına bağlı olarak puanlama
            question_type = question_info['type']
            if question_type == 'multiple_choice':
                total_options = len(question_info.get('options', []))
                correct_set = set(correct_answer) if isinstance(correct_answer, list) else {correct_answer}
                user_set = set(user_answer) if isinstance(user_answer, list) else {user_answer}

                true_positives = user_set & correct_set
                false_positives = user_set - correct_set

                total_correct = len(correct_set)
                points_per_correct = points / total_correct if total_correct > 0 else 0
                points_per_wrong = -1 / (total_options - len(correct_set)) * points if (total_options - len(correct_set)) > 0 else 0

                correct_point = len(true_positives) * points_per_correct
                wrong_penalty = len(false_positives) * points_per_wrong

                question_score = correct_point + wrong_penalty

                # Soru puanını sınırlama
                question_score = max(question_score, 0)  # Negatif puanları sıfırla

            elif question_type == 'single_choice':
                # Tek seçenekli sorular için ceza yok
                if self.check_answer(user_answer, correct_answer):
                    question_score = points  # Doğru cevap için tam puan
                else:
                    question_score = 0  # Yanlış cevap için sıfır puan

            elif question_type == 'true_false':
                # Doğru/Yanlış sorular için ceza yok
                if self.check_answer(user_answer, correct_answer):
                    question_score = points  # Doğru cevap için tam puan
                else:
                    question_score = 0  # Yanlış cevap için sıfır puan
            elif question_type == 'ordering':
                # Sıralama soruları için yeni puanlama mantığı
                question_score = self.score_ordering_question(user_answer, correct_answer, points)
            else:
                print(f"Desteklenmeyen soru türü: {question_type}")
                continue

            # Bölüm puanlarını güncelle
            if section not in self.section_scores:
                self.section_scores[section] = {'earned': 0, 'total': 0}
            self.section_scores[section]['earned'] += question_score
            self.section_scores[section]['total'] += max_score_per_question

            # Hesaplama detaylarını ekrana yazdır
            print(f"Soru ID: {qid}, Bölüm: {section}, Soru Türü: {question_type}, Puan: {points}, Kazanılan Puan: {question_score}")

        # Tamamlanmamış bölümlerin puanlarını 0 olarak ekle
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

        # Geçme/Kalma durumunu belirle
        self.passed = self.check_pass_fail()
        if self.passed:
            print("Tebrikler, sınavı geçtiniz!")
        else:
            print("Maalesef, sınavı geçemediniz.")

        # Kullanıcı puanlarını güncelle
        self.update_user_scores()

        # Bölümleri organize et ve istatistikleri güncelle
        organized_sections = self.organize_sections(all_questions)
        self.organized_sections = organized_sections  # Öznitelik olarak ata
        self.update_statistics(organized_sections)

    def organize_sections(self, all_questions_by_id):
        """answers_record listesini kullanarak bölümleri detaylandırır."""
        sections = {}

        for answer in self.answers_record:
            qid = answer["question_id"]
            question_info = all_questions_by_id.get(qid)
            if not question_info:
                print(f"Uyarı: Soru ID {qid} all_questions_by_id içinde bulunamadı.")
                continue
            section = question_info['section']
            if section not in sections:
                sections[section] = {
                    "section_number": section,
                    "questions": [],
                    "section_score": 0,
                    "section_total": 0
                }
            # Detaylı soru bilgisi ekle
            detailed_question = {
                "question_id": str(question_info['id']),
                "question_text": question_info['question'],
                "question_type": question_info['type'],
                "user_answer": answer["user_answer"],
                "correct_answer": self.correct_answers.get(str(qid)),
                "is_correct": answer["is_correct"],
                "points_earned": answer["points_earned"]
            }
            sections[section]["questions"].append(detailed_question)
            sections[section]["section_score"] += answer["points_earned"]
            sections[section]["section_total"] += question_info.get('points', 1)

        # Bölüm numarasına göre sıralı bir sözlük oluştur
        organized_sections = dict(sorted(sections.items(), key=lambda item: int(item[0])))
        return organized_sections

    def load_all_questions(self):
        """Tüm soruları yükler."""
        from quiznexusai.question import QuestionManager
        qm = QuestionManager()
        all_questions = {}
        for section, filename in qm.section_files.items():
            file_path = os.path.join('data/questions/', filename)
            if os.path.exists(file_path):
                questions = read_json(file_path, encrypted=True)  # Şifreli dosyaları oku
                for q in questions:
                    all_questions[str(q['id'])] = q  # ID'leri stringe çevir
        return all_questions

    def get_question_info(self, question_id, all_questions):
        """Belirli bir soru ID'si için soru bilgisini getirir."""
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
            # Kullanıcının cevabını ve doğru cevabı güvenli bir şekilde işle
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
        """Kullanıcının puanlarını sınav denemelerine göre günceller ve kaydeder."""
        # Kullanıcının sınav deneme sayısına göre puanını güncelle
        if self.user.attempts == 1:
            self.user.score1 = self.total_score
        elif self.user.attempts == 2:
            self.user.score2 = self.total_score

        # Ortalama puanı hesapla
        if self.user.score1 is not None and self.user.score2 is not None:
            self.user.score_avg = (self.user.score1 + self.user.score2) / 2
        elif self.user.score1 is not None:
            self.user.score_avg = self.user.score1
        elif self.user.score2 is not None:
            self.user.score_avg = self.user.score2
        else:
            self.user.score_avg = 0  # Veya tercih ederseniz None yapabilirsiniz

        # Kullanıcının verilerini kaydet
        self.user.save_user()

    def update_statistics(self, organized_sections):
        """Sınavdan sonra sınıf ve okul istatistiklerini günceller, her bölüm ve soru için ortalamaları dahil eder."""
        # Admin ve öğretmenleri istatistiklerden hariç tut
        if self.user.role != 'user':
            return  # Admin veya öğretmen roller için istatistikleri güncelleme

        statistics = read_statistics()

        # Kullanıcının sınıf_id'sini ve okul_id'sini al
        class_id = self.user.class_id
        school_id = self.user.school_id

        # Sınıf istatistiklerini güncelle
        class_stats = statistics['classes'].get(class_id, {
            'average_score': 0.0,
            'student_count': 0,
            'passed': False,
            'sections': {}
        })

        # Okul istatistiklerini güncelle
        school_stats = statistics['schools'].get(school_id, {
            'average_score': 0.0,
            'student_count': 0,
            'passed': False,
            'sections': {}
        })

        # Kullanıcının toplam puanı
        total_score = self.total_score

        # Sınıfın toplam puanını ve öğrenci sayısını güncelle
        class_stats['student_count'] += 1
        class_stats['average_score'] = ((class_stats['average_score'] * (class_stats['student_count'] - 1)) + total_score) / class_stats['student_count']

        # Okulun toplam puanını ve öğrenci sayısını güncelle
        school_stats['student_count'] += 1
        school_stats['average_score'] = ((school_stats['average_score'] * (school_stats['student_count'] - 1)) + total_score) / school_stats['student_count']

        # Sınıf ve okulun geçip geçmediğini belirle (ortalama puan >= 50)
        class_stats['passed'] = class_stats['average_score'] >= 50
        school_stats['passed'] = school_stats['average_score'] >= 50

        # Bölüm ve soru bazında istatistikleri güncelle
        for section_num, section_data in organized_sections.items():
            section_str = str(section_num)
            section_score = section_data['section_score']
            section_total = section_data['section_total']
            section_percentage = (section_score / section_total) * 100 if section_total > 0 else 0

            # Sınıf bölüm istatistiklerini güncelle
            class_sections = class_stats.get('sections', {})
            class_section_stats = class_sections.get(section_str, {
                'average_score': 0.0,
                'student_count': 0,
                'section_percentage': 0.0,
                'questions': {}
            })
            class_section_stats['student_count'] += 1
            class_section_stats['average_score'] = ((class_section_stats['average_score'] * (class_section_stats['student_count'] - 1)) + section_percentage) / class_section_stats['student_count']
            class_section_stats['section_percentage'] = class_section_stats['average_score']  # veya uygun başka bir hesaplama

            # Soruların doğruluğunu güncelle
            for question in section_data['questions']:
                qid = question['question_id']
                is_correct = question['is_correct']
                if qid not in class_section_stats['questions']:
                    class_section_stats['questions'][qid] = {'correct': 0, 'wrong': 0}
                if is_correct:
                    class_section_stats['questions'][qid]['correct'] += 1
                else:
                    class_section_stats['questions'][qid]['wrong'] += 1
            class_sections[section_str] = class_section_stats
            class_stats['sections'] = class_sections
            
            # Okul bölüm istatistiklerini güncelle
            school_sections = school_stats.get('sections', {})
            school_section_stats = school_sections.get(section_str, {
                'average_score': 0.0,
                'student_count': 0,
                'section_percentage': 0.0,
                'questions': {}
            })
            school_section_stats['student_count'] += 1
            school_section_stats['average_score'] = ((school_section_stats['average_score'] * (school_section_stats['student_count'] - 1)) + section_percentage) / school_section_stats['student_count']
            school_section_stats['section_percentage'] = school_section_stats['average_score']  # veya uygun başka bir hesaplama

            # Soruların doğruluğunu güncelle
            for question in section_data['questions']:
                qid = question['question_id']
                is_correct = question['is_correct']
                if qid not in school_section_stats['questions']:
                    school_section_stats['questions'][qid] = {'correct': 0, 'wrong': 0}
                if is_correct:
                    school_section_stats['questions'][qid]['correct'] += 1
                else:
                    school_section_stats['questions'][qid]['wrong'] += 1
            #school_sections[section_str] = school_section_stats
            #school_stats['sections'] = school_section_stats
            
            school_sections[section_str] = school_section_stats
            school_stats['sections'] = school_sections  # Doğru
        # Güncellenen istatistikleri kaydet
        statistics['classes'][class_id] = class_stats
        statistics['schools'][school_id] = school_stats

        # Genel istatistikleri güncelle
        statistics['total_students'] += 1
        statistics['total_exams'] += 1
        if self.passed:
            statistics['successful_exams'] += 1
        else:
            statistics['failed_exams'] += 1

        write_statistics(statistics)

    def score_ordering_question(self, user_answer, correct_answer, points):
        """Sıralama soruları için puan hesaplar."""
        # Hem kullanıcı cevabı hem de doğru cevap listeler olmalı
        if not isinstance(user_answer, list) or not isinstance(correct_answer, list):
            print("Sıralama sorusu için geçersiz cevap formatı.")
            return 0

        total_items = len(correct_answer)
        if total_items == 0:
            print("Bu soruda sıralanacak öğe yok.")
            return 0

        # Doğru pozisyon sayısını hesapla
        correct_positions = sum(1 for u_item, c_item in zip(user_answer, correct_answer) if u_item == c_item)
        points_per_item = points / total_items
        question_score = points_per_item * correct_positions

        # Puanın negatif olmamasını sağla
        question_score = max(question_score, 0)
        return question_score

    def load_all_questions(self):
        """Tüm soruları yükler."""
        from quiznexusai.question import QuestionManager
        qm = QuestionManager()
        all_questions = {}
        for section, filename in qm.section_files.items():
            file_path = os.path.join('data/questions/', filename)
            if os.path.exists(file_path):
                questions = read_json(file_path, encrypted=True)  # Şifreli dosyaları oku
                for q in questions:
                    all_questions[str(q['id'])] = q  # ID'leri stringe çevir
        return all_questions

    def get_question_info(self, question_id, all_questions):
        """Belirli bir soru ID'si için soru bilgisini getirir."""
        return all_questions.get(str(question_id))
