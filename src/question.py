# src/question.py

import os
import uuid
from utils import read_json, write_json

QUESTIONS_FOLDER = 'data/questions/'
ANSWERS_FILE = 'data/answers/answers.json'

class QuestionManager:
    def __init__(self):
        self.section_files = {
            1: 'section1_questions.json',
            2: 'section2_questions.json',
            3: 'section3_questions.json',
            4: 'section4_questions.json'
        }

    def add_question(self):
        """Adds a new question."""
        print("\n=== Add New Question ===")
        question_type = input("Question type (true_false, single_choice, multiple_choice): ").strip().lower()
        if question_type not in ['true_false', 'single_choice', 'multiple_choice']:
            print("Invalid question type.")
            return

        section_input = input("Section number (1-4): ").strip()
        try:
            section = int(section_input)
            if section not in self.section_files:
                raise ValueError
        except ValueError:
            print("Invalid section number. Please enter a number between 1 and 4.")
            return

        question_text = input("Question text: ").strip()
        points_input = input("Question points: ").strip()
        try:
            points = float(points_input)
            if points <= 0:
                raise ValueError
        except ValueError:
            print("Invalid points. Please enter a positive number.")
            return

        if question_type == 'true_false':
            options = ["True", "False"]
        else:
            options_input = input("Enter options separated by commas: ").strip()
            options = [opt.strip() for opt in options_input.split(',')]
            if len(options) < 2:
                print("You must enter at least two options.")
                return

        correct_answer_input = input("Correct answer(s) (separate multiple answers with commas): ").strip()
        if question_type == 'multiple_choice':
            correct_answer = [ans.strip() for ans in correct_answer_input.split(',')]
            if not correct_answer:
                print("You must enter at least one correct answer.")
                return
        else:
            correct_answer = correct_answer_input.strip()
            if not correct_answer:
                print("You must enter a correct answer.")
                return

        # Assign a unique ID
        question_id = str(uuid.uuid4())

        question = {
            'id': question_id,
            'section': section,
            'question': question_text,
            'points': points,
            'type': question_type
        }
        if question_type != 'true_false':
            question['options'] = options

        # Add the question to the correct section file
        file_path = os.path.join(QUESTIONS_FOLDER, self.section_files[section])
        questions = []
        if os.path.exists(file_path):
            questions = read_json(file_path)
        questions.append(question)
        write_json(questions, file_path)

        # Add the correct answer to answers.json
        answers = {}
        if os.path.exists(ANSWERS_FILE):
            answers = read_json(ANSWERS_FILE)
        answers[question_id] = correct_answer
        write_json(answers, ANSWERS_FILE)

        print(f"Question added. Question ID: {question_id}")

    def list_questions(self, section_number):
        """Lists questions in the specified section."""
        try:
            section_number = int(section_number)
            if section_number not in self.section_files and section_number != 0:
                raise ValueError
        except ValueError:
            print("Invalid section number.")
            return

        if section_number == 0:
            print("\n=== All Questions ===")
            sections = self.section_files.keys()
        else:
            sections = [section_number]

        for section in sections:
            file_path = os.path.join(QUESTIONS_FOLDER, self.section_files[section])
            if not os.path.exists(file_path):
                print(f"\n=== Section {section} Questions ===")
                print("Question file not found.")
                continue

            questions = read_json(file_path)
            print(f"\n=== Section {section} Questions ===")
            if not questions:
                print("No questions available.")
                continue

            for q in questions:
                print(f"ID: {q['id']}, Question Type: {q['type']}, Question: {q['question']}, Points: {q['points']}")
                if 'options' in q:
                    for idx, option in enumerate(q['options'], 1):
                        print(f"   {idx}. {option}")
                print("-" * 40)

    def delete_question(self, question_id):
        """Deletes the question with the specified ID."""
        found = False
        for section, filename in self.section_files.items():
            file_path = os.path.join(QUESTIONS_FOLDER, filename)
            if os.path.exists(file_path):
                questions = read_json(file_path)
                new_questions = [q for q in questions if q['id'] != question_id]
                if len(questions) != len(new_questions):
                    write_json(new_questions, file_path)
                    found = True
                    print(f"Question ID {question_id} has been deleted.")
                    break
        if not found:
            print(f"Question ID {question_id} not found.")

        # Also remove from answers
        if os.path.exists(ANSWERS_FILE):
            answers = read_json(ANSWERS_FILE)
            if question_id in answers:
                del answers[question_id]
                write_json(answers, ANSWERS_FILE)

    def update_question(self, question_id):
        """Updates the question with the specified ID."""
        found = False
        for section, filename in self.section_files.items():
            file_path = os.path.join(QUESTIONS_FOLDER, filename)
            if os.path.exists(file_path):
                questions = read_json(file_path)
                for q in questions:
                    if q['id'] == question_id:
                        print(f"\n=== Update Question ID {question_id} ===")
                        print(f"Current Question Text: {q['question']}")
                        new_question_text = input("New question text (leave blank to keep the same): ").strip()
                        if new_question_text:
                            q['question'] = new_question_text

                        print(f"Current Points: {q['points']}")
                        new_points_input = input("New points (leave blank to keep the same): ").strip()
                        if new_points_input:
                            try:
                                new_points = float(new_points_input)
                                if new_points <= 0:
                                    raise ValueError
                                q['points'] = new_points
                            except ValueError:
                                print("Invalid points. Points were not updated.")

                        if q['type'] != 'true_false':
                            print(f"Current Options: {', '.join(q['options'])}")
                            options_input = input("New options (enter separated by commas, leave blank to keep the same): ").strip()
                            if options_input:
                                new_options = [opt.strip() for opt in options_input.split(',')]
                                if len(new_options) < 2:
                                    print("You must enter at least two options. Options were not updated.")
                                else:
                                    q['options'] = new_options
                                    # May need to update the correct answer as well
                                    correct_answer_input = input("New correct answer(s) (separate with commas if multiple, leave blank to keep the same): ").strip()
                                    if correct_answer_input:
                                        if q['type'] == 'multiple_choice':
                                            new_correct_answer = [ans.strip() for ans in correct_answer_input.split(',')]
                                        else:
                                            new_correct_answer = correct_answer_input.strip()
                                        # Update the correct answer in answers.json
                                        answers = {}
                                        if os.path.exists(ANSWERS_FILE):
                                            answers = read_json(ANSWERS_FILE)
                                        answers[question_id] = new_correct_answer
                                        write_json(answers, ANSWERS_FILE)
                        write_json(questions, file_path)
                        print(f"Question ID {question_id} has been updated.")
                        found = True
                        break
                if found:
                    break
        if not found:
            print(f"Question ID {question_id} not found.")
