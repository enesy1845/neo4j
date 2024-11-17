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
        self.duration = 180  # Exam duration (in seconds)
        self.start_time = None
        self.end_time = None
        self.sections = 4  # 4 sections
        self.question_manager = QuestionManager()
        self.answers = {}  # User's answers
        self.used_question_ids = set()  # To track used question IDs
        self.current_question_number = 1  # Question counter
        self.time_up = False  # To track if time is up
        self.lock = threading.Lock()  # Lock for thread safety

    def start_exam(self):
        """Starts the exam."""
        try:
            clear_screen()
            print("Starting the exam...")
            self.user.increment_attempts()
            self.start_time = time.time()
            self.end_time = self.start_time + self.duration

            # Start the timer thread
            timer_thread = threading.Thread(target=self.timer)
            timer_thread.daemon = True
            timer_thread.start()

            # Load questions
            all_questions = self.load_questions()
            
            # Prepare the list of questions to be used throughout the exam
            self.used_question_ids = set()

            # Present questions for each section
            for section_number in range(1, self.sections + 1):
                if self.time_up:
                    print("\nExam time is up.")
                    break

                # Section header
                print(f"\n=== Section {section_number} ===")
                input(f"Section {section_number} is starting. Press Enter to continue...")
                
                # Select questions for the section
                section_questions = self.select_questions_for_section(all_questions, section_number)

                # Present the questions
                for question in section_questions:
                    if self.time_up:
                        print("\nExam time is up.")
                        raise TimeUpException("Exam time is up.")
                    self.present_question(question)

                # Section end message
                if section_number < self.sections:
                    print(f"\nSection {section_number} is over.")
                    input(f"Press Enter to move to Section {section_number + 1}...")
                else:
                    print(f"\nSection {section_number} is over. The exam has ended.")

        except TimeUpException as tue:
            print("\nExam time has expired!")
        except Exception as e:
            print(f"\nAn unexpected error occurred: {e}")
        finally:
            # End the exam
            self.end_exam()

    def timer(self):
        """Tracks the exam duration."""
        while True:
            with self.lock:
                remaining_time = self.end_time - time.time()
                if remaining_time <= 0:
                    self.time_up = True
                    break
            time.sleep(1)

    def is_time_up(self):
        """Checks if the exam time has expired."""
        with self.lock:
            return self.time_up or time.time() >= self.end_time

    def load_questions(self):
        """Loads all questions and groups them by section number."""
        all_questions = {}
        for section, filename in self.question_manager.section_files.items():
            file_path = os.path.join('data/questions/', filename)
            if os.path.exists(file_path):
                questions = read_json(file_path)
                # Each question already has 'section' and 'type' information
                all_questions[section] = questions
        return all_questions

    def select_questions_for_section(self, all_questions, section_number):
        """Selects questions for each section."""
        section_questions = []
        # First, select one question from each type
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
                print(f"Warning: Not enough questions of type {qtype} in Section {section_number}.")

        # Randomly select the remaining questions
        remaining_needed = 5 - len(section_questions)
        if remaining_needed > 0:
            all_available_questions = [
                q for q in all_questions.get(section_number, [])
                if q['id'] not in self.used_question_ids
            ]
            if len(all_available_questions) < remaining_needed:
                print(f"Warning: Not enough questions in Section {section_number}.")
            else:
                additional_questions = random.sample(all_available_questions, remaining_needed)
                section_questions.extend(additional_questions)
                for q in additional_questions:
                    self.used_question_ids.add(q['id'])

        # Shuffle the order of questions
        random.shuffle(section_questions)
        return section_questions

    def present_question(self, question):
        """Presents the question to the user and records their answer."""
        while True:
            try:
                clear_screen()
                remaining_time = int(self.end_time - time.time())
                if remaining_time <= 0:
                    print("Exam time is up!")
                    raise TimeUpException("Exam time is up.")
                mins, secs = divmod(remaining_time, 60)
                time_format = '{:02d}:{:02d}'.format(mins, secs)
                print(f"Time Remaining: {time_format}\n")

                print(f"Question {self.current_question_number}: {question['question']}")
                if 'options' in question:
                    for idx, option in enumerate(question['options'], 1):
                        print(f"{idx}. {option}")
                if question['type'] == 'multiple_choice':
                    print("Select multiple options by separating the numbers with commas (e.g., 1,3,4)")
                elif question['type'] == 'single_choice':
                    print("Enter your answer as the option number.")
                else:
                    print("1. True")
                    print("2. False")
                
                # Don't sleep quickly to update the remaining time
                # Get user's answer
                user_input = input("Your answer: ")

                if self.is_time_up():
                    print("\nExam time is up!")
                    raise TimeUpException("Exam time is up.")

                if not user_input.strip():
                    print("\nPlease enter an answer.")
                    input("Press Enter to continue...")
                    continue  # Present the same question again

                answers = self.process_input(user_input.strip(), question)
                self.answers[str(question['id'])] = answers
                self.current_question_number += 1  # Increment the counter
                break

            except ValueError as ve:
                print(f"\nError: {ve}")
                input("Press Enter to continue...")
                continue  # Present the same question again
            except TimeUpException as tue:
                # When exam time is up, terminate the process
                raise tue
            except Exception as e:
                print(f"\nAn unknown error occurred: {e}")
                input("Press Enter to continue...")
                continue  # Present the same question again

    def process_input(self, user_input, question):
        """Processes the user's input answer."""
        if question['type'] == 'multiple_choice':
            indices = user_input.split(',')
            answers = []
            for idx_str in indices:
                idx_str = idx_str.strip()
                if not idx_str.isdigit():
                    raise ValueError("Please enter option numbers.")
                idx = int(idx_str) - 1
                if idx < 0 or idx >= len(question['options']):
                    raise ValueError(f"Please enter a number between 1 and {len(question['options'])}.")
                answers.append(question['options'][idx])
            return answers
        elif question['type'] == 'single_choice':
            if not user_input.isdigit():
                raise ValueError("Please enter an option number.")
            idx = int(user_input.strip()) - 1
            if idx < 0 or idx >= len(question['options']):
                raise ValueError(f"Please enter a number between 1 and {len(question['options'])}.")
            return question['options'][idx]
        else:  # True/False
            if user_input not in ['1', '2']:
                raise ValueError("Please enter only 1 or 2.")
            return ["True", "False"][int(user_input.strip()) - 1]

    def end_exam(self):
        """Ends the exam and calculates the results."""
        print("\nExam completed.")
        from result import Result
        try:
            result = Result(self.user, self.answers, self.used_question_ids, self.sections)
            result.calculate_results()
        except Exception as e:
            print(f"An error occurred while calculating results: {e}")
            input("Press Enter to continue...")
