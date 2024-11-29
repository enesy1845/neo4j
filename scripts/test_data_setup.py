import os
import uuid
import bcrypt
import json
import sys
from quiznexusai.utils import read_json, USERS_FILE, write_json, SCHOOLS_FILE, CLASSES_FILE, get_next_user_id

def create_test_schools(existing_schools=None):
    if os.path.exists(SCHOOLS_FILE):
        print(f"{SCHOOLS_FILE} already exists. Schools will not be created.")
        schools = read_json(SCHOOLS_FILE)
        if existing_schools:
            schools = existing_schools
        return schools

    # Fixed school_ids to ensure consistency
    schools = [
        {'school_id': '5c2fec33-10ed-4177-88ed-10090de96114', 'school_name': 'Green Valley High School'},
        {'school_id': '31442513-3546-484f-92df-630435180158', 'school_name': 'Riverdale Elementary School'},
        {'school_id': 'e6ebd8a2-ded4-4e67-8596-8d99e78d74df', 'school_name': 'Mountainview Middle School'},
        {'school_id': '0f76b5bc-f800-4c80-9349-6d681f993128', 'school_name': 'Lakeside Academy'},
        {'school_id': '3d57315a-90cc-41b1-a55e-0a6fd3ff8575', 'school_name': 'Sunrise Elementary School'},
    ]
    write_json(schools, SCHOOLS_FILE)
    print(f"{SCHOOLS_FILE} created and schools added.")
    return schools

def create_test_classes(schools, existing_classes=None):
    if os.path.exists(CLASSES_FILE):
        print(f"{CLASSES_FILE} already exists. Classes will not be created.")
        classes = read_json(CLASSES_FILE)
        if existing_classes:
            classes = existing_classes
        return classes

    classes = []
    for school in schools:
        for i in range(1, 5):  # Create 4 classes per school
            if "Elementary" in school["school_name"]:
                grade = "7"
            elif "High" in school["school_name"]:
                grade = "10"
            elif "Middle" in school["school_name"]:
                grade = "8"
            elif "Academy" in school["school_name"]:
                grade = "9"
            else:
                grade = "Unknown"

            # Assign class names based on grade and section
            class_name = f'{grade}-{chr(64+i)}' if grade != "Unknown" else f'Class {i}'
            cls = {
                'class_id': str(uuid.uuid4()),
                'class_name': class_name,
                'school_id': school['school_id'],
                'sections': {
                    "1": {"correct_questions": 0, "wrong_questions": 0},
                    "2": {"correct_questions": 0, "wrong_questions": 0},
                    "3": {"correct_questions": 0, "wrong_questions": 0},
                    "4": {"correct_questions": 0, "wrong_questions": 0}
                }
            }
            classes.append(cls)
    write_json(classes, CLASSES_FILE)
    print(f"{CLASSES_FILE} created and classes added.")
    return classes

def create_test_students(classes):
    users = []
    if os.path.exists(USERS_FILE):
        users = read_json(USERS_FILE)
    else:
        print(f"{USERS_FILE} does not exist. Creating...")

    for i in range(1, 21):  # Create 20 students
        if not classes:
            print(f"Error: Class list is empty. Student {i} cannot be created.")
            continue
        cls = classes[i % len(classes)]
        if not cls['class_id'] or not cls['school_id']:
            print(f"Error: Class {cls.get('class_name', 'Unknown')} is missing class_id or school_id.")
            continue
        student = {
            'user_id': str(uuid.uuid4()),
            'username': f'student{i}',
            'password': bcrypt.hashpw(f'password{i}'.encode('utf-8'), bcrypt.gensalt()).decode('utf-8'),
            'name': f'Student{i}',
            'surname': f'Lastname{i}',
            'phone_number': f'555-000-{i:04d}',
            'role': 'user',
            'attempts': 0,
            'last_attempt_date': '',
            'score1': None,
            'score2': None,
            'score_avg': None,
            'class_id': cls['class_id'],
            'school_id': cls['school_id'],
            'teacher_sections': []
        }
        users.append(student)
    write_json(users, USERS_FILE)
    print(f"20 students created and added to {USERS_FILE}.")
    
    # Print assigned class and school for each student
    print("\n=== Assigned Classes and Schools for Students ===")
    schools = read_json(SCHOOLS_FILE)
    classes_dict = {cls['class_id']: cls for cls in classes}
    schools_dict = {school['school_id']: school for school in schools}

    for user in users[-20:]:  # Last 20 students
        class_info = classes_dict.get(user['class_id'], {})
        school_info = schools_dict.get(user['school_id'], {})
        print(f"Username: {user['username']}, Class: {class_info.get('class_name', 'Unknown')}, School: {school_info.get('school_name', 'Unknown')}")

def create_test_teachers(classes):
    teachers = []
    for i in range(1, 6):  # Create 5 teachers
        if not classes:
            print(f"Error: Class list is empty. Teacher {i} cannot be created.")
            continue
        cls = classes[i % len(classes)]
        if not cls['class_id'] or not cls['school_id']:
            print(f"Error: Class {cls.get('class_name', 'Unknown')} is missing class_id or school_id.")
            continue
        teacher = {
            'user_id': str(uuid.uuid4()),
            'username': f'teacher{i}',
            'password': bcrypt.hashpw(f'password{i}'.encode('utf-8'), bcrypt.gensalt()).decode('utf-8'),
            'name': f'Teacher{i}',
            'surname': f'Surname{i}',
            'phone_number': f'555-100-{i:04d}',
            'role': 'teacher',
            'attempts': 0,
            'last_attempt_date': '',
            'score1': None,
            'score2': None,
            'score_avg': None,
            'class_id': cls['class_id'],
            'school_id': cls['school_id'],
            'teacher_sections': ["1", "2", "3"]  # Assigned 3 sections
        }
        teachers.append(teacher)
    
    # Read existing users
    if os.path.exists(USERS_FILE):
        users = read_json(USERS_FILE)
    else:
        users = []
    
    # Add teachers to users
    users.extend(teachers)
    write_json(users, USERS_FILE)
    print(f"5 teachers created and added to {USERS_FILE}.")
    
    # Print assigned class and school for each teacher
    print("\n=== Assigned Classes and Schools for Teachers ===")
    schools = read_json(SCHOOLS_FILE)
    classes_dict = {cls['class_id']: cls for cls in classes}
    schools_dict = {school['school_id']: school for school in schools}

    for teacher in teachers:
        class_info = classes_dict.get(teacher['class_id'], {})
        school_info = schools_dict.get(teacher['school_id'], {})
        print(f"Username: {teacher['username']}, Class: {class_info.get('class_name', 'Unknown')}, School: {school_info.get('school_name', 'Unknown')}")
    
    return teachers

def validate_data(schools, classes, users, teachers):
    school_ids = set(school['school_id'] for school in schools)
    class_ids = set(cls['class_id'] for cls in classes)
    
    errors = False
    
    for cls in classes:
        if cls['school_id'] not in school_ids:
            print(f"Error: Class {cls['class_id']} has invalid school_id {cls['school_id']}.")
            errors = True
    
    for user in users:
        if user['class_id'] not in class_ids:
            print(f"Error: User {user['user_id']} has invalid class_id {user['class_id']}.")
            errors = True
        if user['school_id'] not in school_ids:
            print(f"Error: User {user['user_id']} has invalid school_id {user['school_id']}.")
            errors = True
    
    if not errors:
        print("\nData validation successful. All IDs are consistent.")
    else:
        print("\nData validation encountered errors. Please review the above messages.")

def display_users():
    users = read_json(USERS_FILE)
    classes = read_json(CLASSES_FILE)
    schools = read_json(SCHOOLS_FILE)
    
    classes_dict = {cls['class_id']: cls['class_name'] for cls in classes}
    schools_dict = {school['school_id']: school['school_name'] for school in schools}
    
    print("\n=== User List ===")
    for user in users:
        class_name = classes_dict.get(user['class_id'], '-')
        school_name = schools_dict.get(user['school_id'], '-')
        score1 = f"{user['score1']}%" if user['score1'] is not None else "-"
        score2 = f"{user['score2']}%" if user['score2'] is not None else "-"
        score_avg = f"{user['score_avg']}%" if user['score_avg'] is not None else "-"
        print(f"ID: {user['user_id']}, Name: {user['name']} {user['surname']}, Phone: {user['phone_number']}, Class: {class_name}, School: {school_name}, Login Attempts: {user['attempts']}, Score 1: {score1}, Score 2: {score2}, Average: {score_avg}")

if __name__ == "__main__":
    try:
        # Create or load schools and classes
        if os.path.exists(SCHOOLS_FILE) and os.path.exists(CLASSES_FILE):
            print("Using existing schools and classes.")
            schools = read_json(SCHOOLS_FILE)
            classes = read_json(CLASSES_FILE)
        else:
            print("Schools or classes file does not exist. Creating...")
            schools = create_test_schools()
            classes = create_test_classes(schools)
        
        # Ensure all classes have 'sections'
        sections_added = False
        for cls in classes:
            if 'sections' not in cls:
                print(f"Warning: Class {cls['class_id']} is missing 'sections'. Adding sections.")
                cls['sections'] = {
                    "1": {"correct_questions": 0, "wrong_questions": 0},
                    "2": {"correct_questions": 0, "wrong_questions": 0},
                    "3": {"correct_questions": 0, "wrong_questions": 0},
                    "4": {"correct_questions": 0, "wrong_questions": 0}
                }
                sections_added = True
        if sections_added:
            write_json(classes, CLASSES_FILE)
            print(f"{CLASSES_FILE} has been updated with missing sections.")
        
        # Create students and teachers
        create_test_students(classes)
        teachers = create_test_teachers(classes)
        
        # Load users
        if os.path.exists(USERS_FILE):
            users = read_json(USERS_FILE)
        else:
            users = []
        
        # Validate data
        validate_data(schools, classes, users, teachers)
        
        # Display users
        display_users()
        
        print("\nTest data setup complete.")
        if teachers is not None:
            print(f"Number of Teachers Created: {len(teachers)}")
            for teacher in teachers:
                print(f"  Teacher ID: {teacher['user_id']}, Username: {teacher['username']}, Sections: {teacher['teacher_sections']}")
        else:
            print("Error: 'teachers' list is None. create_test_teachers function did not work properly.")
    
    except Exception as e:
        print("\nAn error occurred during test data setup:")
        print(str(e))
        sys.exit(1)
