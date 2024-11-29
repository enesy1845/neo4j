# src/class_module.py

import os
import uuid
from quiznexusai.utils import read_json, write_json, CLASSES_FILE, SCHOOLS_FILE, USERS_FILE, clear_screen

class ClassManager:
    def manage_classes(self):
        """Admin menu for managing classes."""
        while True:
            clear_screen()
            print("=== Manage Classes ===")
            print("1. List Classes")
            print("2. Add Class")
            print("3. Update Class")
            print("4. Delete Class")
            print("5. Go Back")
            choice = input("Your choice: ").strip()
            if choice == '1':
                self.list_classes()
                input("Press Enter to continue...")
            elif choice == '2':
                self.add_class()
                input("Press Enter to continue...")
            elif choice == '3':
                self.update_class()
                input("Press Enter to continue...")
            elif choice == '4':
                self.delete_class()
                input("Press Enter to continue...")
            elif choice == '5':
                break
            else:
                print("Invalid choice.")
                input("Press Enter to continue...")

    def list_classes(self):
        classes = []
        if os.path.exists(CLASSES_FILE):
            classes = read_json(CLASSES_FILE)
        print("\n=== Classes ===")
        if not classes:
            print("No classes found.")
        else:
            schools = read_json(SCHOOLS_FILE) if os.path.exists(SCHOOLS_FILE) else []
            for idx, cls in enumerate(classes, 1):
                school_name = next((sch['school_name'] for sch in schools if sch['school_id'] == cls['school_id']), 'Unknown School')
                print(f"{idx}. ID: {cls['class_id']}, Name: {cls['class_name']}, School: {school_name}")
        print()

    def add_class(self):
        classes = []
        if os.path.exists(CLASSES_FILE):
            classes = read_json(CLASSES_FILE)

        schools = []
        if os.path.exists(SCHOOLS_FILE):
            schools = read_json(SCHOOLS_FILE)
        else:
            print("No schools found. Please add a school first.")
            return

        print("\nSelect the school for the new class:")
        for idx, school in enumerate(schools, 1):
            print(f"{idx}. {school['school_name']}")
        choice = input("Enter the number of the school: ").strip()
        if not choice.isdigit() or not 1 <= int(choice) <= len(schools):
            print("Invalid choice.")
            return
        school_idx = int(choice) - 1
        school_id = schools[school_idx]['school_id']

        class_name = input("Enter class name: ").strip()
        if not class_name:
            print("Class name cannot be empty.")
            return
        class_id = str(uuid.uuid4())
        classes.append({'class_id': class_id, 'class_name': class_name, 'school_id': school_id})
        write_json(classes, CLASSES_FILE)
        print("Class added successfully.")

    def update_class(self):
        classes = []
        if os.path.exists(CLASSES_FILE):
            classes = read_json(CLASSES_FILE)
        else:
            print("No classes found.")
            return

        self.list_classes()
        choice = input("Enter the number of the class you want to update: ").strip()
        if not choice.isdigit() or not 1 <= int(choice) <= len(classes):
            print("Invalid choice.")
            return
        idx = int(choice) - 1
        cls = classes[idx]
        print(f"Current name: {cls['class_name']}")
        new_name = input("Enter new class name (leave blank to keep current): ").strip()
        if new_name:
            cls['class_name'] = new_name

        # Optionally update the school
        schools = read_json(SCHOOLS_FILE) if os.path.exists(SCHOOLS_FILE) else []
        if schools:
            print("Do you want to change the school for this class?")
            change_school = input("Enter 'yes' to change, or press Enter to skip: ").strip().lower()
            if change_school == 'yes':
                print("\nSelect the new school:")
                for idx_s, school in enumerate(schools, 1):
                    print(f"{idx_s}. {school['school_name']}")
                school_choice = input("Enter the number of the school: ").strip()
                if not school_choice.isdigit() or not 1 <= int(school_choice) <= len(schools):
                    print("Invalid choice.")
                    return
                school_idx = int(school_choice) - 1
                cls['school_id'] = schools[school_idx]['school_id']

        write_json(classes, CLASSES_FILE)
        print("Class updated successfully.")

    def delete_class(self):
        classes = []
        if os.path.exists(CLASSES_FILE):
            classes = read_json(CLASSES_FILE)
        else:
            print("No classes found.")
            return

        self.list_classes()
        choice = input("Enter the number of the class you want to delete: ").strip()
        if not choice.isdigit() or not 1 <= int(choice) <= len(classes):
            print("Invalid choice.")
            return
        idx = int(choice) - 1
        cls = classes[idx]

        # Check if there are users associated with this class
        users = []
        if os.path.exists(USERS_FILE):
            users = read_json(USERS_FILE)
            associated_users = [user for user in users if user.get('class_id') == cls['class_id']]
            if associated_users:
                print("Cannot delete class with existing users. Please delete or reassign users first.")
                return

        # Proceed to delete the class
        confirm = input(f"Are you sure you want to delete '{cls['class_name']}'? (yes/no): ").strip().lower()
        if confirm == 'yes':
            classes.pop(idx)
            write_json(classes, CLASSES_FILE)
            print("Class deleted successfully.")
        else:
            print("Deletion cancelled.")

    def get_classes_by_school(self, school_id):
        """Returns a list of classes associated with a given school_id."""
        classes = []
        if os.path.exists(CLASSES_FILE):
            classes = read_json(CLASSES_FILE)
            return [cls for cls in classes if cls['school_id'] == school_id]
        return []

