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
        self.used_question_ids = set()  # Track used question IDs
        self.current_question_number = 1  # Question counter
        self.time_up = False  # To track if time is up
        self.lock = threading.Lock()  # Lock for thread safety

    def start_exam(self):
        """Starts the exam."""
        try:
            clear_screen()
            self.user.increment_attempts()
            self.start_time = time.time()
            self.end_time = self.start_time + self.duration

            # Start the timer thread
            timer_thread = threading.Thread(target=self.timer)
            timer_thread.daemon = True
            timer_thread.start()
            print("The exam has started...")

            # Load the questions
            all_questions = self.load_questions()
            
            # Prepare the list of questions to be used during the exam
            self.used_question_ids = set()

            # Present questions for each section
            for section_number in range(1, self.sections + 1):
                if self.time_up:
                    print("\nTime is up.")
                    break

                # Section header
                print(f"\n=== Section {section_number} ===")
                if section_number != 1:
                    input(f"Section {section_number} is starting. Press Enter to continue...")

                # Select questions for the section
                section_questions = self.select_questions_for_section(all_questions, section_number)

                # Present questions
                index = 0
                while index < len(section_questions):
                    print(f"Question {index + 1}/{len(section_questions)} ")
                    question = section_questions[index]
                    if self.time_up:
                        print("\nTime is up.")
                        raise TimeUpException("Time is up.")

                     # Call the function with the question's index
                    indexResult = self.present_question(question, index, section_questions, section_number)
                    # Eğer result'a bağlı bir işlem yapacaksak burada değerlendirebiliriz
                    print(f"Soru {index + 1}: Dönüş değeri: {indexResult}")
                    if indexResult=="n":
                        # Move to the next index

                        index += 1
                    elif indexResult == "p":
                        # Move to the previous index
                        if index > 0:
                            index -= 1
                    elif indexResult == "e":
                        index = len(section_questions) + 1
                    else:
                        index += 1
                    if index >= len(section_questions):
                        if input(f"\nDo you want to end Section {section_number}? (Y/N)").lower() == "n":
                            # Set index modulo the number of questions
                            index = index % len(section_questions)

                # End of section message
                if section_number < self.sections:
                    print(f"\nSection {section_number} has ended.")
                    input(f"Press Enter to proceed to Section {section_number + 1}...")
                else:
                    print(f"\nSection {section_number} has ended. The exam is over.")

        except TimeUpException as tue:
            print("\nTime is up!")
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
        """Checks if the exam time is up."""
        with self.lock:
            return self.time_up or time.time() >= self.end_time

    def load_questions(self):
        """Loads all questions and groups them by section."""
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
        # First, take one question of each type
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

        # Shuffle the questions
        random.shuffle(section_questions)
        return section_questions


    def present_question(self, question, index, section_questions, section_number):
        """Presents a question to the user and collects their answer."""

        while True:
            clear_screen()
            try:
                keys = list(self.answers)
                key = keys[(section_number-1) * 5 + index]

                if isinstance(self.answers[key], list):  # Check if it's a list
                    for item in self.answers[key]:
                        print(item)
                else:
                    print(self.answers[key])  # Print directly if it's not a list

            except:
                pass
            try:
                print(f"Question {index + 1}/{len(section_questions)} ")
                
                remaining_time = int(self.end_time - time.time())
                if remaining_time <= 0:
                    print("Time is up!")
                    raise TimeUpException("Time is up.")
                mins, secs = divmod(remaining_time, 60)
                time_format = '{:02d}:{:02d}'.format(mins, secs)
                print(f"Remaining Time: {time_format}\n")

                print(f"Question {index}: {question['question']}")
                if 'options' in question:
                    for idx, option in enumerate(question['options'], 1):
                        print(f"{idx}. {option}")
                if question['type'] == 'multiple_choice':
                    print("Enter multiple choices separated by commas (e.g., 1,3,4).")
                elif question['type'] == 'single_choice':
                    print("Enter your answer as the option number.")
                else:
                    print("1. True")
                    print("2. False")
                
                user_input = input("((N)ext,(P)rev,(E)nd) Your answer: ")

                if self.is_time_up():
                    print("\nTime is up!")
                    raise TimeUpException("Time is up.")

                if not user_input.strip():
                    print("\nPlease enter an answer.")
                    input("Press Enter to continue...")
                    continue
                if user_input.lower() not in ['p', 'n', 'e']:
                    answers = self.process_input(user_input.strip(), question)
                    self.answers[str(question['id'])] = answers
                else:   
                    return user_input.lower()
                    pass
                break

            except ValueError as ve:
                print(f"\nError: {ve}")
                input("Press Enter to continue...")
                continue
            except TimeUpException as tue:
                raise tue
            except Exception as e:
                print(f"\nAn unknown error occurred: {e}")
                input("Press Enter to continue...")
                continue

    def process_input(self, user_input, question):
        """Processes the user's answer."""
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
        print("\nThe exam is completed.")
        from result import Result
        try:
            result = Result(self.user, self.answers, self.used_question_ids, self.sections)
            result.calculate_results()
        except Exception as e:
            print(f"An error occurred while calculating results: {e}")
            input("Press Enter to continue...")
