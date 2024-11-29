# tests/test_integration.py

import pytest
import os
import sys
import pytest

project_root = os.path.abspath(os.path.join(os.path.dirname(__file__), '..'))
sys.path.insert(0, project_root)

from scripts.test_data_setup import (
    create_test_schools,
    create_test_classes,
    create_test_students,
    create_test_teachers,
)
from scripts.simulate_student_actions import simulate_all_students
from quiznexusai.utils import read_json, STATISTICS_FILE,USERS_FILE

@pytest.fixture(scope='module')
def setup_test_data():
    print("===== Setting Up Test Data =====")
    
    # Prepare test data
    schools = create_test_schools()
    classes = create_test_classes(schools)
    create_test_students(classes)
    teachers = create_test_teachers(classes)  # Create teachers
    
    # Read users from USERS_FILE to get students
    users = read_json(USERS_FILE)
    students = [user for user in users if user.get('role') == 'user']
    
    print("\n--- Test Data Created ---")
    print(f"Number of Schools: {len(schools)}")
    for school in schools:
        print(f"  School ID: {school['school_id']}, Name: {school['school_name']}")
    
    print(f"\nNumber of Classes: {len(classes)}")
    for cls in classes:
        print(f"  Class ID: {cls['class_id']}, Name: {cls['class_name']}, School ID: {cls['school_id']}")
    
    print(f"\nNumber of Students: {len(students)}")
    for student in students:
        print(f"  Student ID: {student['user_id']}, Username: {student['username']}, Class ID: {student['class_id']}")
    
    print(f"\nNumber of Teachers: {len(teachers)}")
    for teacher in teachers:
        print(f"  Teacher ID: {teacher['user_id']}, Username: {teacher['username']}, Sections: {teacher['teacher_sections']}")
    
    print("===== Test Data Setup Complete =====\n")
    
    return schools, classes, students, teachers

def test_student_exams(setup_test_data):
    schools, classes, students, teachers = setup_test_data
    print("===== Starting Exam Simulation =====")
    
    # Simulate students taking exams
    simulate_all_students()
    print("===== Exam Simulation Complete =====\n")
    
    # Verify statistics
    print("===== Verifying Statistics =====")
    statistics = read_json(STATISTICS_FILE)
    
    # Schools Statistics
    print("\n--- Schools Statistics ---")
    for school_id, stats in statistics.get('schools', {}).items():
        print(f"School ID: {school_id}")
        print(f"  Average Score: {stats.get('average_score', 0):.2f}%")
        print(f"  Student Count: {stats.get('student_count', 0)}")
    
    # Classes Statistics
    print("\n--- Classes Statistics ---")
    for class_id, stats in statistics.get('classes', {}).items():
        print(f"Class ID: {class_id}")
        print(f"  Average Score: {stats.get('average_score', 0):.2f}%")
        print(f"  Student Count: {stats.get('student_count', 0)}")
    
    # Overall Summary (Assuming these keys exist)
    total_students = statistics.get('total_students', len(students))
    total_exams = statistics.get('total_exams', 0)
    successful_exams = statistics.get('successful_exams', 0)
    failed_exams = statistics.get('failed_exams', 0)
    
    print("\n--- Overall Summary ---")
    print(f"Total Students: {total_students}")
    print(f"Total Exams Attempted: {total_exams}")
    print(f"Successful Exams: {successful_exams}")
    print(f"Failed Exams: {failed_exams}")
    
    print("\n===== Statistics Verification Complete =====\n")
    
    # Assertions
    assert 'classes' in statistics, "Classes statistics missing."
    assert 'schools' in statistics, "Schools statistics missing."
    # Add more assertions based on your requirements