# src/school.py

import os
import uuid
from quiznexusai.utils import read_json, write_json, SCHOOLS_FILE, clear_screen

class SchoolManager:
    def manage_schools(self):
        """Admin menu for managing schools."""
        while True:
            clear_screen()
            print("=== Manage Schools ===")
            print("1. List Schools")
            print("2. Add School")
            print("3. Update School")
            print("4. Delete School")
            print("5. Go Back")
            choice = input("Your choice: ").strip()
            if choice == '1':
                self.list_schools()
                input("Press Enter to continue...")
            elif choice == '2':
                self.add_school()
                input("Press Enter to continue...")
            elif choice == '3':
                self.update_school()
                input("Press Enter to continue...")
            elif choice == '4':
                self.delete_school()
                input("Press Enter to continue...")
            elif choice == '5':
                break
            else:
                print("Invalid choice.")
                input("Press Enter to continue...")

    def list_schools(self):
        schools = []
        if os.path.exists(SCHOOLS_FILE):
            schools = read_json(SCHOOLS_FILE)
        print("\n=== Schools ===")
        if not schools:
            print("No schools found.")
        else:
            for idx, school in enumerate(schools, 1):
                print(f"{idx}. ID: {school['school_id']}, Name: {school['school_name']}")
        print()

    def add_school(self):
        schools = []
        if os.path.exists(SCHOOLS_FILE):
            schools = read_json(SCHOOLS_FILE)
        school_name = input("Enter school name: ").strip()
        if not school_name:
            print("School name cannot be empty.")
            return
        school_id = str(uuid.uuid4())
        schools.append({'school_id': school_id, 'school_name': school_name})
        write_json(schools, SCHOOLS_FILE)
        print("School added successfully.")

    def update_school(self):
        schools = []
        if os.path.exists(SCHOOLS_FILE):
            schools = read_json(SCHOOLS_FILE)
        else:
            print("No schools found.")
            return

        self.list_schools()
        choice = input("Enter the number of the school you want to update: ").strip()
        if not choice.isdigit() or not 1 <= int(choice) <= len(schools):
            print("Invalid choice.")
            return
        idx = int(choice) - 1
        school = schools[idx]
        print(f"Current name: {school['school_name']}")
        new_name = input("Enter new school name (leave blank to keep current): ").strip()
        if new_name:
            school['school_name'] = new_name
            write_json(schools, SCHOOLS_FILE)
            print("School updated successfully.")
        else:
            print("No changes made.")

    def delete_school(self):
        schools = []
        if os.path.exists(SCHOOLS_FILE):
            schools = read_json(SCHOOLS_FILE)
        else:
            print("No schools found.")
            return

        self.list_schools()
        choice = input("Enter the number of the school you want to delete: ").strip()
        if not choice.isdigit() or not 1 <= int(choice) <= len(schools):
            print("Invalid choice.")
            return
        idx = int(choice) - 1
        school = schools[idx]

        # Check if there are classes associated with this school
        from class_module import ClassManager
        class_manager = ClassManager()
        classes = class_manager.get_classes_by_school(school['school_id'])
        if classes:
            print("Cannot delete school with existing classes. Please delete or reassign classes first.")
            return

        # Proceed to delete the school
        confirm = input(f"Are you sure you want to delete '{school['school_name']}'? (yes/no): ").strip().lower()
        if confirm == 'yes':
            schools.pop(idx)
            write_json(schools, SCHOOLS_FILE)
            print("School deleted successfully.")
        else:
            print("Deletion cancelled.")

