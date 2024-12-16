# tools/exam.py

import uuid
import json
import random
from datetime import datetime
from tools.utils import load_json, save_json

QUESTIONS_DIR = 'questions/'
ANSWERS_FILE = 'answers/answers.json'
USER_ANSWERS_FILE = 'users/user_answers.json'
STATISTICS_FILE = 'users/statistics.json'

def load_questions():
    questions = []
    for section in range(1, 5):
        file_path = f"{QUESTIONS_DIR}questions_section{section}.json"
        data = load_json(file_path)
        questions.extend(data.get('questions', []))
    return questions

def select_questions(user):
    if user['attempts'] >= 2:
        print("You have no remaining exam attempts.")
        return None
    questions = load_questions()
    selected_questions = {}
    sections = {1: [], 2: [], 3: [], 4: []}
    # Select 5 random questions from each section
    for section in range(1,5):
        section_questions = [q for q in questions if q['section'] == section]
        if len(section_questions) < 5:
            selected = section_questions
        else:
            selected = random.sample(section_questions, 5)
        sections[section] = selected
    selected_questions = sections
    return selected_questions

def start_exam(user):
    selected_questions = select_questions(user)
    if not selected_questions:
        return
    # Start timer (e.g., 30 minutes)
    import threading
    time_limit = 30 * 60  # 30 minutes in seconds
    timer = threading.Timer(time_limit, lambda: print("\nTime is up! Exam ended."))
    print("Exam started. You have 30 minutes.")
    timer.start()
    user_answers = {}
    for section, qs in selected_questions.items():
        print(f"\n--- Section {section} ---")
        for q in qs:
            print(f"Q: {q['question']} ({q['type']})")
            user_response = input("Your answer: ")
            user_answers[q['id']] = user_response
    timer.cancel()
    end_time = datetime.now().isoformat()
    process_results(user, selected_questions, user_answers, end_time)

def process_results(user, selected_questions, user_answers, end_time):
    answers = load_json(ANSWERS_FILE)
    total_score = 0
    section_scores = {1:0, 2:0, 3:0, 4:0}
    section_correct = {1:0, 2:0, 3:0, 4:0}
    section_wrong = {1:0, 2:0, 3:0, 4:0}
    
    for section, qs in selected_questions.items():
        for q in qs:
            correct = False
            correct_answer = answers.get(q['id'])
            user_answer = user_answers.get(q['id'])
            if q['type'] == 'true_false' or q['type'] == 'single_choice':
                if user_answer.strip().lower() == correct_answer.strip().lower():
                    correct = True
            elif q['type'] == 'multiple_choice' or q['type'] == 'ordering':
                if isinstance(correct_answer, list):
                    user_ans_set = set([ans.strip().lower() for ans in user_answer.split(',')])
                    correct_ans_set = set([ans.strip().lower() for ans in correct_answer])
                    if user_ans_set == correct_ans_set:
                        correct = True
            if correct:
                section_scores[section] += q['points']
                section_correct[section] += 1
            else:
                section_wrong[section] += 1
    total_score = sum(section_scores.values())
    score_avg = (total_score / 20) * 100  # Assuming total possible points = 20
    
    # Determine pass/fail based on sections
    passed = True
    for sec in range(1,5):
        section_percentage = (section_scores[sec] / 5) * 100  # Assuming each section is 5 points
        if section_percentage < 75:
            passed = False
    if score_avg < 75:
        passed = False
    result = "Passed" if passed else "Failed"
    
    # Update user attempts and scores
    user['attempts'] += 1
    user['last_attempt_date'] = datetime.now().isoformat()
    if user['attempts'] == 1:
        user['score1'] = total_score
    elif user['attempts'] == 2:
        user['score2'] = total_score
        user['score_avg'] = (user['score1'] + user['score2']) / 2 if user['attempts'] == 2 else user['score1']
    
    # Save updated user data
    users_data = load_json('users/users.json')
    for u in users_data['users']:
        if u['username'] == user['username']:
            u.update(user)
            break
    save_json('users/users.json', users_data)
    
    # Save exam answers
    exam_id = str(uuid.uuid4())
    exam_record = {
        "exam_id": exam_id,
        "user_id": user['user_id'],
        "class_name": user['class_name'],
        "school_name": user['school_name'],
        "start_time": datetime.now().isoformat(),
        "end_time": end_time,
        "sections": []
    }
    
    for section, qs in selected_questions.items():
        section_record = {
            "section_number": section,
            "questions": []
        }
        for q in qs:
            correct_answer = answers.get(q['id'])
            user_answer = user_answers.get(q['id'])
            is_correct = False
            if q['type'] == 'true_false' or q['type'] == 'single_choice':
                if user_answer.strip().lower() == correct_answer.strip().lower():
                    is_correct = True
            elif q['type'] == 'multiple_choice' or q['type'] == 'ordering':
                if isinstance(correct_answer, list):
                    user_ans_set = set([ans.strip().lower() for ans in user_answer.split(',')])
                    correct_ans_set = set([ans.strip().lower() for ans in correct_answer])
                    if user_ans_set == correct_ans_set:
                        is_correct = True
            question_record = {
                "question_id": q['id'],
                "question_text": q['question'],
                "question_type": q['type'],
                "user_answer": user_answer,
                "correct_answer": correct_answer,
                "is_correct": is_correct,
                "points_earned": q['points'] if is_correct else 0
            }
            section_record['questions'].append(question_record)
        exam_record['sections'].append(section_record)
    user_answers_data = load_json(USER_ANSWERS_FILE)
    user_answers_data['exams'].append(exam_record)
    save_json(USER_ANSWERS_FILE, user_answers_data)
    
    # Update statistics
    statistics = load_json(STATISTICS_FILE)
    for school in statistics['schools']:
        if school['school_name'] == user['school_name']:
            class_name = user['class_name']
            if class_name not in school['classes']:
                # Sınıfı ekle
                school['classes'][class_name] = {
                    "sections": {
                        "1": {"correct_questions": 0, "wrong_questions": 0, "average_score": 0, "section_percentage": 0},
                        "2": {"correct_questions": 0, "wrong_questions": 0, "average_score": 0, "section_percentage": 0},
                        "3": {"correct_questions": 0, "wrong_questions": 0, "average_score": 0, "section_percentage": 0},
                        "4": {"correct_questions": 0, "wrong_questions": 0, "average_score": 0, "section_percentage": 0}
                    },
                    "average_score": 0.0
                }
                print(f"Class {class_name} added to statistics.")
            
            for sec in range(1,5):
                soru_bolumu = f"section-{sec}"
                if str(sec) not in school['classes'][class_name]['sections']:
                    # Bölümü ekle
                    school['classes'][class_name]['sections'][str(sec)] = {
                        "correct_questions": 0,
                        "wrong_questions": 0,
                        "average_score": 0.0,
                        "section_percentage": 0
                    }
                    print(f"Section {sec} added to class {class_name}.")
                
                school['classes'][class_name]['sections'][str(sec)]['correct_questions'] += section_correct[sec]
                school['classes'][class_name]['sections'][str(sec)]['wrong_questions'] += section_wrong[sec]
                # Update average score
                previous_avg = school['classes'][class_name]['sections'][str(sec)]['average_score']
                new_percentage = (section_scores[sec] / 5) * 100  # Assuming each section is 5 points
                new_avg = (previous_avg + new_percentage) / 2
                school['classes'][class_name]['sections'][str(sec)]['average_score'] = new_avg
                # Update section_percentage
                school['classes'][class_name]['sections'][str(sec)]['section_percentage'] = new_percentage
            # Update class average
            class_sections = school['classes'][class_name]['sections']
            class_avg = sum([sec_data['average_score'] for sec_data in class_sections.values()]) / len(class_sections)
            school['classes'][class_name]['average_score'] = class_avg
            # Update school average
            school_classes = school['classes']
            school_avg = sum([cls_data['average_score'] for cls_data in school_classes.values()]) / len(school_classes)
            school['average_score'] = school_avg
            break
    save_json(STATISTICS_FILE, statistics)
    print(f"Exam Finished. Your Score: {total_score}/20. Result: {result}\n")
