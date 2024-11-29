# scripts/simulate_student_actions.py

import os
import random
import sys
import uuid
from datetime import datetime, timezone
import time

from quiznexusai.user import User
from quiznexusai.exam import Exam
from quiznexusai.utils import read_json, write_json, USERS_FILE, STATISTICS_FILE,read_statistics

def simulate_exam_for_student(user_data):
    # Create a User object
    user = User(
        user_id=user_data['user_id'],
        username=user_data['username'],
        password=user_data['password'],
        name=user_data['name'],
        surname=user_data['surname'],
        phone_number=user_data['phone_number'],
        role=user_data.get('role', 'user'),
        attempts=user_data.get('attempts', 0),
        last_attempt_date=user_data.get('last_attempt_date', ''),
        score1=user_data.get('score1'),
        score2=user_data.get('score2'),
        score_avg=user_data.get('score_avg'),
        class_id=user_data.get('class_id'),
        school_id=user_data.get('school_id'),
        teacher_sections=user_data.get('teacher_sections')
    )

    # Check if the student can attempt the exam
    if not user.can_attempt_exam():
        print(f"{user.username} has no remaining attempts.")
        return False  # Indicate exam was not attempted

    # Create an Exam object
    exam = Exam(user)
    exam.user.increment_attempts()
    exam.start_time = datetime.now(timezone.utc).isoformat()
    exam.attempt_id = str(uuid.uuid4())
    exam.answers_record = []
    exam.used_question_ids = set()
    exam.current_question_number = 1
    exam.end_time = time.time() + exam.duration  # Set the end time
    exam.time_up = False

    # Load questions for the exam
    all_questions_by_section, all_questions_by_id = exam.load_questions()
    if not all_questions_by_section:
        print(f"No questions loaded for the exam for {user.username}.")
        return False  # Indicate exam was not attempted

    # Simulate the exam per section
    for section_number in range(1, exam.sections + 1):
        if exam.time_up:
            print("\nExam time is up.")
            break
        # Select questions for the section
        section_questions = exam.select_questions_for_section(all_questions_by_section, section_number)
        for question in section_questions:
            if exam.time_up:
                print("\nExam time is up.")
                break
            exam.used_question_ids.add(question['id'])
            # Simulate the answer
            qid = question['id']
            qtype = question['type']
            if qtype == 'single_choice':
                options = question['options']
                user_input = str(random.randint(1, len(options)))
            elif qtype == 'multiple_choice':
                options = question['options']
                num_choices = random.randint(1, len(options))
                selected_indices = random.sample(range(1, len(options)+1), num_choices)
                user_input = ','.join(map(str, selected_indices))
            elif qtype == 'true_false':
                user_input = random.choice(['1', '2'])  # 1 for True, 2 for False
            elif qtype == 'ordering':
                options = question['options']
                indices = list(range(1, len(options)+1))
                random.shuffle(indices)
                user_input = ','.join(map(str, indices))
            else:
                user_input = ''
                print(f"Unsupported question type: {qtype} for Question ID: {qid}")
            # Process the simulated input
            exam.process_simulated_input(user_input, question)
            exam.current_question_number += 1
    # Simulate ending the exam
    exam.end_exam(all_questions_by_id)
    print(f"{user.username} completed the exam with score: {exam.user.score_avg}%")
    
    # Update statistics
    statistics = read_json(STATISTICS_FILE)
    if not statistics:
        statistics = {
            'schools': {},
            'classes': {},
            'total_students': 0,
            'total_exams': 0,
            'successful_exams': 0,
            'failed_exams': 0
        }
    
    # Update overall statistics
    statistics['total_students'] = statistics.get('total_students', 0) + 1
    statistics['total_exams'] = statistics.get('total_exams', 0) + 1
    if exam.user.score_avg >= 50:  # Assuming 50% as passing score
        statistics['successful_exams'] = statistics.get('successful_exams', 0) + 1
    else:
        statistics['failed_exams'] = statistics.get('failed_exams', 0) + 1
    
    # Update school statistics
    school_id = user.school_id
    if school_id not in statistics['schools']:
        statistics['schools'][school_id] = {'average_score': 0.0, 'student_count': 0}
    school_stats = statistics['schools'][school_id]
    school_stats['average_score'] = ((school_stats['average_score'] * school_stats['student_count']) + exam.user.score_avg) / (school_stats['student_count'] + 1)
    school_stats['student_count'] += 1
    
    # Update class statistics
    class_id = user.class_id
    if class_id not in statistics['classes']:
        statistics['classes'][class_id] = {'average_score': 0.0, 'student_count': 0}
    class_stats = statistics['classes'][class_id]
    class_stats['average_score'] = ((class_stats['average_score'] * class_stats['student_count']) + exam.user.score_avg) / (class_stats['student_count'] + 1)
    class_stats['student_count'] += 1
    
    write_json(statistics, STATISTICS_FILE)
    
    return True  # Indicate exam was successfully attempted

def simulate_all_students():
    users = read_json(USERS_FILE)
    students = [user for user in users if user.get('role') == 'user']
    successful = 0
    failed = 0
    for student in students:
        result = simulate_exam_for_student(student)
        if result:
            # Use read_statistics to ensure keys are initialized
            statistics = read_statistics()
            if statistics['successful_exams'] >= successful + 1:
                successful += 1
            elif statistics['failed_exams'] >= failed + 1:
                failed += 1
    print(f"\nTotal Exams Attempted: {successful + failed}")
    print(f"Successful Exams: {successful}")
    print(f"Failed Exams: {failed}")

if __name__ == "__main__":
    simulate_all_students()
