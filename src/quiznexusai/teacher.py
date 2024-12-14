# src/teacher.py

from quiznexusai.utils import clear_screen, read_json, write_json, ANSWERS_FILE, QUESTIONS_DIR
from quiznexusai.question import QuestionManager
from quiznexusai.user import User
from quiznexusai.statistics_module import StatisticsManager
import os
import uuid
from quiznexusai.token_generator import renew_token_if_needed

class Teacher:
    def __init__(self, teacher_user):
        self.teacher_user = teacher_user
        self.question_manager = QuestionManager()
        self.statistics_manager = StatisticsManager()

    def teacher_menu(self):
        """Teacher user menu."""
        while True:
            clear_screen()
            print(f"=== Teacher Menu ({self.teacher_user.name} {self.teacher_user.surname}) ===")
            print("1. Add Question to My Sections")
            print("2. Update Question in My Sections")
            print("3. Delete Question from My Sections")
            print("4. View Questions in My Sections")
            print("5. View Statistics")
            print("6. Logout")
            choice = input("Your choice: ").strip()
            renew_token_if_needed()
            if choice == '1':
                self.add_question_by_teacher()
            elif choice == '2':
                self.update_question_by_teacher()
            elif choice == '3':
                self.delete_question_by_teacher()
            elif choice == '4':
                self.list_questions_by_teacher()
            elif choice == '5':
                self.statistics_manager.view_teacher_statistics(self.teacher_user)
                input("Press Enter to continue...")
                renew_token_if_needed()
            elif choice == '6':
                print("Logging out...")
                break
            else:
                print("Invalid choice.")
                input("Press Enter to continue...")
                renew_token_if_needed()

    def add_question_by_teacher(self):
        """Allows a teacher to add a question to their assigned sections."""
        print("\n=== Add New Question ===")
        # Only allow sections assigned to the teacher
        sections_str = ', '.join(str(sec) for sec in self.teacher_user.teacher_sections)
        print(f"You can add questions to the following sections: {sections_str}")

        section_input = input(f"Select section ({sections_str}): ").strip()
        renew_token_if_needed()
        try:
            section = int(section_input)
            if section not in self.teacher_user.teacher_sections:
                print("You are not authorized to add questions to this section.")
                input("Press Enter to continue...")
                renew_token_if_needed()
                return
        except ValueError:
            print("Invalid section number.")
            input("Press Enter to continue...")
            renew_token_if_needed()
            return

        # Rest of the question adding process
        question_type = input("Question type (true_false, single_choice, multiple_choice, ordering): ").strip().lower()
        renew_token_if_needed()
        if question_type not in ['true_false', 'single_choice', 'multiple_choice', 'ordering']:
            print("Invalid question type.")
            input("Press Enter to continue...")
            renew_token_if_needed()
            return

        question_text = input("Question text: ").strip()
        renew_token_if_needed()
        points_input = input("Question points: ").strip()
        renew_token_if_needed()
        try:
            points = float(points_input)
            if points <= 0:
                raise ValueError
        except ValueError:
            print("Invalid points. Please enter a positive number.")
            input("Press Enter to continue...")
            renew_token_if_needed()
            return

        if question_type == 'true_false':
            options = ["True", "False"]
        else:
            options_input = input("Enter options separated by commas: ").strip()
            options = [opt.strip() for opt in options_input.split(',')]
            if len(options) < 2:
                print("You must enter at least two options.")
                input("Press Enter to continue...")
                renew_token_if_needed()
                return

        correct_answer_input = input("Correct answer(s) (separate multiple answers with commas): ").strip()
        renew_token_if_needed()
        if question_type == 'multiple_choice' or question_type == 'ordering':
            correct_answer = [ans.strip() for ans in correct_answer_input.split(',')]
            if not correct_answer:
                print("You must enter at least one correct answer.")
                input("Press Enter to continue...")
                renew_token_if_needed()
                return
        else:
            correct_answer = correct_answer_input.strip()
            if not correct_answer:
                print("You must enter a correct answer.")
                input("Press Enter to continue...")
                renew_token_if_needed()
                return

        # Assign a unique UUID
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

        # Write to the appropriate section file
        file_path = os.path.join(QUESTIONS_DIR, self.question_manager.section_files[section])
        questions = []
        if os.path.exists(file_path):
            questions = read_json(file_path, encrypted=True)
        questions.append(question)
        write_json(questions, file_path, encrypted=True)
        print(f"Question added to Section {section}. Question ID: {question_id}")

        # Add the correct answer to answers.json
        answers = {}
        if os.path.exists(ANSWERS_FILE):
            answers = read_json(ANSWERS_FILE, encrypted=True)
        answers[question_id] = correct_answer
        write_json(answers, ANSWERS_FILE, encrypted=True)
        input("Press Enter to continue...")
        renew_token_if_needed()

    def list_questions_by_teacher(self, show_ids=False):
        """Lists questions in the sections assigned to the teacher."""
        try:
            for section in self.teacher_user.teacher_sections:
                file_path = os.path.join(QUESTIONS_DIR, self.question_manager.section_files.get(section, ''))
                if not os.path.exists(file_path):
                    print(f"\n=== Section {section} Questions ===")
                    print("Question file not found.")
                    continue

                questions = read_json(file_path, encrypted=True)  # Read as encrypted
                print(f"\n=== Section {section} Questions ===")
                if not questions:
                    print("No questions available.")
                    continue

                for q in questions:
                    if show_ids:
                        print(f"ID: {q['id']}")
                    print(f"Question Type: {q['type']}, Question: {q['question']}, Points: {q['points']}")
                    if 'options' in q:
                        for idx, option in enumerate(q['options'], 1):
                            print(f"   {idx}. {option}")
                    print("-" * 40)
            # Add input here to pause before returning to the menu
            input("Press Enter to continue...")
            renew_token_if_needed()
        except Exception as e:
            print(f"An error occurred while listing questions: {e}")
            input("Press Enter to continue...")
            renew_token_if_needed()

    def update_question_by_teacher(self):
        """Allows a teacher to update a question in their assigned sections."""
        print("\n=== Update Question ===")
        self.list_questions_by_teacher(show_ids=True)
        question_id = input("Enter the ID of the question you want to update: ").strip()
        if not question_id:
            print("Question ID cannot be empty.")
            input("Press Enter to continue...")
            renew_token_if_needed()
            return

        # Check if the question belongs to the teacher's sections
        if not self.question_belongs_to_teacher(question_id):
            print("You are not authorized to update this question.")
            input("Press Enter to continue...")
            renew_token_if_needed()
            return

        # Proceed with updating the question
        self.question_manager.update_question(question_id)
        input("Press Enter to continue...")
        renew_token_if_needed()

    def delete_question_by_teacher(self):
        """Allows a teacher to delete a question from their assigned sections."""
        print("\n=== Delete Question ===")
        self.list_questions_by_teacher(show_ids=True)
        question_id = input("Enter the ID of the question you want to delete: ").strip()
        renew_token_if_needed()
        if not question_id:
            print("Question ID cannot be empty.")
            input("Press Enter to continue...")
            renew_token_if_needed()
            return

        # Check if the question belongs to the teacher's sections
        if not self.question_belongs_to_teacher(question_id):
            print("You are not authorized to delete this question.")
            input("Press Enter to continue...")
            renew_token_if_needed()
            return

        # Proceed with deleting the question
        self.question_manager.delete_question(question_id)
        input("Press Enter to continue...")
        renew_token_if_needed()

    def question_belongs_to_teacher(self, question_id):
        """Checks if a question belongs to the teacher's assigned sections."""
        for section in self.teacher_user.teacher_sections:
            file_path = os.path.join(QUESTIONS_DIR, self.question_manager.section_files.get(section, ''))
            if os.path.exists(file_path):
                questions = read_json(file_path, encrypted=True)
                if any(q['id'] == question_id for q in questions):
                    return True
        return False

