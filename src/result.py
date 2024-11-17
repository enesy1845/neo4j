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
        print("\n=== Exam Results ===")
        
        # Load all question information
        all_questions = self.load_all_questions()

        # Calculate total points per section
        section_total_points = {section: 0 for section in range(1, self.total_sections + 1)}
        for qid in self.used_question_ids:
            question_info = self.get_question_info(qid, all_questions)
            if question_info:
                section = question_info['section']
                points = question_info.get('points', 1)
                section_total_points[section] += points

        # Evaluate each question and update section scores
        for qid, user_answer in self.user_answers.items():
            correct_answer = self.correct_answers.get(qid)
            question_info = self.get_question_info(qid, all_questions)
            if not question_info:
                print(f"Question ID {qid} information not found.")
                continue
            if correct_answer is None:
                print(f"Error: No correct answer found for Question ID {qid}.")
                continue
            section = question_info['section']
            points = question_info.get('points', 1)
            max_score_per_question = points  # Maximum points per question

            # Initialize question score to 0
            question_score = 0

            # Scoring based on question type and number of options
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

                # Limit the question score
                question_score = max(question_score, 0)  # Set negative scores to zero

            elif question_type == 'single_choice':
                # No penalty for single-choice questions
                if self.check_answer(user_answer, correct_answer):
                    question_score = points  # Full points for correct answer
                else:
                    question_score = 0  # Zero points for incorrect answer

            elif question_type == 'true_false':
                # No penalty for true/false questions
                if self.check_answer(user_answer, correct_answer):
                    question_score = points  # Full points for correct answer
                else:
                    question_score = 0  # Zero points for incorrect answer

            else:
                print(f"Unsupported question type: {question_type}")
                continue

            # Update section scores
            if section not in self.section_scores:
                self.section_scores[section] = {'earned': 0, 'total': 0}
            self.section_scores[section]['earned'] += question_score
            self.section_scores[section]['total'] += max_score_per_question

            # Print calculation details to the screen
            print(f"Question ID: {qid}, Section: {section}, Question Type: {question_type}, Points: {points}, Earned: {question_score}")

        # Add scores of incomplete sections as 0
        for section in range(1, self.total_sections + 1):
            if section not in self.section_scores:
                self.section_scores[section] = {'earned': 0, 'total': section_total_points.get(section, 0)}
                print(f"Section {section}: Not completed yet. Points: 0")

        # Calculate section success percentages and total score
        total_earned = 0
        total_possible = 0
        for section, scores in sorted(self.section_scores.items()):
            earned = scores['earned']
            total = scores['total']
            percentage = (earned / total) * 100 if total > 0 else 0
            print(f"Section {section}: {percentage:.2f}% success")
            total_earned += earned
            total_possible += total

        self.total_score = (total_earned / total_possible) * 100 if total_possible > 0 else 0
        print(f"\nTotal Success Percentage: {self.total_score:.2f}%")

        # Determine pass/fail status
        self.passed = self.check_pass_fail()
        if self.passed:
            print("Congratulations, you passed the exam!")
        else:
            print("Unfortunately, you did not pass the exam.")

        # Update user scores
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
                    all_questions[str(q['id'])] = q  # Convert IDs to strings
        return all_questions

    def get_question_info(self, question_id, all_questions):
        return all_questions.get(str(question_id))

    def check_answer(self, user_answer, correct_answer):
        """Compares the user's answer with the correct answer."""
        if user_answer is None or correct_answer is None:
            return False

        if isinstance(correct_answer, list):
            if not isinstance(user_answer, list):
                return False
            return set(user_answer) == set(correct_answer)
        else:
            # Process user's answer and correct answer safely
            user_processed = user_answer.strip().lower() if isinstance(user_answer, str) else ''
            correct_processed = correct_answer.strip().lower() if isinstance(correct_answer, str) else ''
            return user_processed == correct_processed

    def check_pass_fail(self):
        """Checks whether the user passed the exam."""
        for section, scores in self.section_scores.items():
            percentage = (scores['earned'] / scores['total']) * 100 if scores['total'] > 0 else 0
            if percentage < 75:
                return False
        overall_pass = self.total_score >= 75
        return overall_pass

    def update_user_scores(self):
        """
        Updates and saves the user's scores based on their exam attempts.
        """
        # Update the user's score based on their exam attempt count
        if self.user.attempts == 1:
            self.user.score1 = self.total_score
        elif self.user.attempts == 2:
            self.user.score2 = self.total_score
            # Calculate the average score
            if self.user.score1 is not None:
                self.user.score_avg = (self.user.score1 + self.user.score2) / 2
            else:
                self.user.score_avg = self.user.score2
        else:
            print("The user has no remaining exam attempts.")

        # Save the user's data
        self.user.save_user()
