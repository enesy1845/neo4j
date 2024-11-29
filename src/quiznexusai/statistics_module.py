# src/quiznexusai/statistics_module.py

import os
from quiznexusai.utils import (
    read_json,
    CLASSES_FILE,
    SCHOOLS_FILE,
    read_statistics,
    write_statistics,
    read_user_answers,
    USERS_FILE,
    ANSWERS_FILE,
    print_table
)

class StatisticsManager:
    def view_admin_statistics(self):
        """Displays class and school statistics for admins."""
        statistics = read_statistics()
        classes = read_json(CLASSES_FILE) if os.path.exists(CLASSES_FILE) else []
        schools = read_json(SCHOOLS_FILE) if os.path.exists(SCHOOLS_FILE) else []

        print("\n=== Statistics ===")

        # Display Class Averages
        print("\n=== Class Averages ===")
        for class_id, stats in statistics.get('classes', {}).items():
            class_info = next((cls for cls in classes if cls['class_id'] == class_id), {})
            class_name = class_info.get('class_name', 'Unknown Class')
            school_id = class_info.get('school_id')
            school_info = next((sch for sch in schools if sch['school_id'] == school_id), {})
            school_name = school_info.get('school_name', 'Unknown School')
            average_score = stats.get('average_score', 0)
            student_count = stats.get('student_count', 0)
            print(f"Class {class_name} (School: {school_name}): {average_score:.2f}% (Students: {student_count})")
            
            # Display per-section statistics for the class
            headers = ["Section", "Average Score (%)", "Student Count", "Section Success (%)"]
            rows = []
            for section_num, section_stats in sorted(stats.get('sections', {}).items(), key=lambda x: int(x[0]) if x[0].isdigit() else float('inf')):
                if not section_num.isdigit():
                    continue  # Geçersiz anahtarları atla
                average = section_stats.get('average_score', 0)
                student_cnt = section_stats.get('student_count', 0)
                section_success = section_stats.get('section_percentage', 0)
                rows.append([f"Section {section_num}", f"{average:.2f}%", str(student_cnt), f"{section_success:.2f}%"])
            print_table(headers, rows, title=f"Class {class_name} - Section Statistics")

            # Display per-question statistics for the class
            print(f"\n=== Class {class_name} - Question Statistics ===")
            headers_q = ["Question ID", "Correct", "Wrong", "Percentage (%)"]
            rows_q = []
            for section_num, section_stats in sorted(stats.get('sections', {}).items(), key=lambda x: int(x[0]) if x[0].isdigit() else float('inf')):
                if not section_num.isdigit():
                    continue  # Geçersiz anahtarları atla
                for qid, q_stats in sorted(section_stats.get('questions', {}).items()):
                    correct = q_stats.get('correct', 0)
                    wrong = q_stats.get('wrong', 0)
                    total = correct + wrong
                    percentage = (correct / total) * 100 if total > 0 else 0
                    rows_q.append([qid, str(correct), str(wrong), f"{percentage:.2f}%"])
            print_table(headers_q, rows_q, title=f"Class {class_name} - Question Statistics")
            print("-" * 40)

        # Display School Averages
        print("\n=== School Averages ===")
        for school_id, stats in statistics.get('schools', {}).items():
            school_info = next((sch for sch in schools if sch['school_id'] == school_id), {})
            school_name = school_info.get('school_name', 'Unknown School')
            average_score = stats.get('average_score', 0)
            student_count = stats.get('student_count', 0)
            print(f"School {school_name}: {average_score:.2f}% (Students: {student_count})")
            
            # Display per-section statistics for the school
            headers = ["Section", "Average Score (%)", "Student Count", "Section Success (%)"]
            rows = []
            for section_num, section_stats in sorted(stats.get('sections', {}).items(), key=lambda x: int(x[0]) if x[0].isdigit() else float('inf')):
                if not section_num.isdigit():
                    continue  # Geçersiz anahtarları atla
                average = section_stats.get('average_score', 0)
                student_cnt = section_stats.get('student_count', 0)
                section_success = section_stats.get('section_percentage', 0)
                rows.append([f"Section {section_num}", f"{average:.2f}%", str(student_cnt), f"{section_success:.2f}%"])
            print_table(headers, rows, title=f"School {school_name} - Section Statistics")

            # Display per-question statistics for the school
            print(f"\n=== School {school_name} - Question Statistics ===")
            headers_q = ["Question ID", "Correct", "Wrong", "Percentage (%)"]
            rows_q = []
            for section_num, section_stats in sorted(stats.get('sections', {}).items(), key=lambda x: int(x[0]) if x[0].isdigit() else float('inf')):
                if not section_num.isdigit():
                    continue  # Geçersiz anahtarları atla
                for qid, q_stats in sorted(section_stats.get('questions', {}).items()):
                    correct = q_stats.get('correct', 0)
                    wrong = q_stats.get('wrong', 0)
                    total = correct + wrong
                    percentage = (correct / total) * 100 if total > 0 else 0
                    rows_q.append([qid, str(correct), str(wrong), f"{percentage:.2f}%"])
            print_table(headers_q, rows_q, title=f"School {school_name} - Question Statistics")
            print("-" * 40)

        # Display General Summary
        print("\n=== General Summary ===")
        total_students = statistics.get('total_students', 0)
        total_exams = statistics.get('total_exams', 0)
        successful_exams = statistics.get('successful_exams', 0)
        failed_exams = statistics.get('failed_exams', 0)
        print(f"Total Students: {total_students}")
        print(f"Total Exam Attempts: {total_exams}")
        print(f"Successful Exams: {successful_exams}")
        print(f"Failed Exams: {failed_exams}")

    def view_teacher_statistics(self, teacher_user):
        """Displays statistics for the teacher's assigned classes and schools."""
        statistics = read_statistics()
        user_answers_data = read_user_answers()
        attempts = user_answers_data.get("attempts", [])
        teacher_sections = teacher_user.teacher_sections

        # Initialize data structures
        question_correct_counts = {}  # {question_id: correct_count}
        question_total_counts = {}    # {question_id: total_count}
        section_scores = {}           # {section_number: {'total_score': 0, 'total_possible': 0, 'student_count': 0}}

        # Collect statistics from attempts
        for attempt in attempts:
            sections = attempt.get("sections", {})

            # If sections is a list, convert it to a dict
            if isinstance(sections, list):
                sections_dict = {str(sec['section_number']): sec for sec in sections}
            else:
                sections_dict = sections

            for section_num, section_data in sections_dict.items():
                if not section_num.isdigit():
                    continue  # Geçersiz anahtarları atla
                section_number = int(section_num)
                if section_number in teacher_sections:
                    section_score = section_data.get('section_score', 0)
                    section_total = section_data.get('section_total', 0)

                    if section_number not in section_scores:
                        section_scores[section_number] = {'total_score': 0, 'total_possible': 0, 'student_count': 0}

                    section_scores[section_number]['total_score'] += section_score
                    section_scores[section_number]['total_possible'] += section_total
                    section_scores[section_number]['student_count'] += 1

                    # Update question statistics
                    questions = section_data.get("questions", [])
                    for q in questions:  # Iterate over list
                        qid = q.get("question_id")
                        is_correct = q.get("is_correct", False)
                        if qid:
                            question_total_counts[qid] = question_total_counts.get(qid, 0) + 1
                            if is_correct:
                                question_correct_counts[qid] = question_correct_counts.get(qid, 0) + 1

        # Display question statistics
        print("\n=== Your Sections' Question Statistics ===")
        headers = ["Question ID", "Correct", "Total", "Percentage (%)"]
        rows = []
        for qid, total in question_total_counts.items():
            correct = question_correct_counts.get(qid, 0)
            percentage = (correct / total) * 100 if total > 0 else 0
            rows.append([qid, str(correct), str(total), f"{percentage:.2f}%"])
        print_table(headers, rows, title="Question Statistics")

        # Display section averages
        print("\n=== Your Sections' Averages ===")
        headers = ["Section", "Average Score (%)", "Students"]
        rows = []
        for section_number in sorted(section_scores.keys()):
            scores = section_scores[section_number]
            if scores['total_possible'] > 0:
                average = (scores['total_score'] / scores['total_possible']) * 100
            else:
                average = 0
            rows.append([f"Section {section_number}", f"{average:.2f}%", str(scores['student_count'])])
        print_table(headers, rows, title="Section Averages")

        # Display class and school averages
        print("\n=== Class and School Averages ===")

        # Get classes and schools assigned to the teacher
        assigned_class_ids = teacher_user.assigned_class_ids
        assigned_school_ids = teacher_user.assigned_school_ids

        # Display class averages
        print("\n=== Class Averages ===")
        headers = ["Class Name", "Average Score (%)", "Students"]
        rows = []
        classes = read_json(CLASSES_FILE) if os.path.exists(CLASSES_FILE) else []
        for class_id in assigned_class_ids:
            class_info = next((cls for cls in classes if cls['class_id'] == class_id), {})
            class_name = class_info.get('class_name', 'Unknown Class')
            class_stats = statistics.get('classes', {}).get(class_id, {})
            average_score = class_stats.get('average_score', 0)
            student_count = class_stats.get('student_count', 0)
            rows.append([class_name, f"{average_score:.2f}%", str(student_count)])
        print_table(headers, rows, title="Class Averages")

        # Display school averages
        print("\n=== School Averages ===")
        headers = ["School Name", "Average Score (%)", "Students"]
        rows = []
        schools = read_json(SCHOOLS_FILE) if os.path.exists(SCHOOLS_FILE) else []
        for school_id in assigned_school_ids:
            school_info = next((sch for sch in schools if sch['school_id'] == school_id), {})
            school_name = school_info.get('school_name', 'Unknown School')
            school_stats = statistics.get('schools', {}).get(school_id, {})
            average_score = school_stats.get('average_score', 0)
            student_count = school_stats.get('student_count', 0)
            rows.append([school_name, f"{average_score:.2f}%", str(student_count)])
        print_table(headers, rows, title="School Averages")

        # Display user grades
        print("\n=== Student Grades ===")
        headers = ["Student Name", "Average Score (%)"]
        rows = []
        users = read_json(USERS_FILE) if os.path.exists(USERS_FILE) else []
        for user in users:
            if user.get('class_id') in assigned_class_ids and user.get('role') == 'user':
                user_name = f"{user.get('name', '')} {user.get('surname', '')}".strip()
                user_score_avg = user.get('score_avg')
                if user_score_avg is not None:
                    rows.append([user_name, f"{user_score_avg:.2f}%"])
                else:
                    rows.append([user_name, "No exam data"])
        print_table(headers, rows, title="Student Grades")
