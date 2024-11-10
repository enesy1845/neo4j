# question.py

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
        pass


    def list_questions(self, question_type):
        """Belirtilen tipteki veya tüm soruları listeler."""
        pass

    def delete_question(self, question_id):
        """Belirtilen ID'ye sahip soruyu siler."""
        pass

    def update_question(self, question_id):
        """Belirtilen ID'ye sahip soruyu günceller."""
        pass