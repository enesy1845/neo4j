# MultiPartQuizApp

## **Project Description**

MultiPartQuizApp is a comprehensive quiz and exam management system designed to facilitate timed, multi-section exams. Users can attempt quizzes divided into various sections, each with its own time limit. The system supports multiple user roles, including students, teachers, and administrators, each with distinct permissions and functionalities. Secure data handling through AES encryption ensures the protection of sensitive information, while detailed statistical analyses provide insights into performance metrics at class and school levels.

## **Features**

- **Multi-Section Exams:** Each exam comprises multiple sections with individual time constraints.
- **Diverse Question Types:** Supports True/False, Single Choice, Multiple Choice, and Ordering questions.
- **User Roles:** Distinct interfaces and permissions for Students, Teachers, and Administrators.
- **Secure Data Management:** Utilizes AES encryption to securely store and handle data.
- **Statistical Analysis:** Provides detailed statistics and performance evaluations at class and school levels.
- **Integration Testing:** Comprehensive test scenarios to ensure system integrity and reliability.

## **Project Structure**

```
MultiPartQuizApp/
├── data/
│   ├── answers/
│   │   └── answers.json
│   ├── classes/
│   │   └── classes.json
│   ├── questions/
│   │   ├── section1_questions.json
│   │   ├── section2_questions.json
│   │   ├── section3_questions.json
│   │   └── section4_questions.json
│   ├── schools/
│   │   └── schools.json
│   ├── statistics/
│   │   └── statistics.json
│   ├── user_answers/
│   │   └── user_answers.json
│   └── users/
│       └── users.json
├── scripts/
│   ├── decrypt_files.py
│   ├── encrypt_files.py
│   ├── simulate_student_actions.py
│   └── test_data_setup.py
src/
├── quiznexusai/
│   ├── __init__.py
│   ├── admin.py
│   ├── class_module.py
│   ├── encryption.py
│   ├── exam.py
│   ├── main.py
│   ├── question.py
│   ├── result.py
│   ├── school.py
│   ├── statistics_module.py
│   ├── teacher.py
│   ├── user.py
│   └── utils.py
├── tests/
│   └── test_integration.py
├── .gitignore
├── environment.yml
├── LICENSE
├── README.md
└── setup.py
```

- **data/**: Directory containing all data files used by the application.

  - **answers/**: Stores the correct answers for questions.
  - **classes/**: Information about different classes.
  - **questions/**: Separate JSON files for questions in each section.
  - **schools/**: Information about different schools.
  - **statistics/**: Statistical data related to exams and performance.
  - **user_answers/**: Stores users' exam attempts and answers.
  - **users/**: User information including students, teachers, and admins.

- **scripts/**: Helper scripts for various tasks.

  - **decrypt_files.py**: Script to decrypt encrypted data files.
  - **encrypt_files.py**: Script to encrypt data files.
  - **simulate_student_actions.py**: Simulates student exam attempts.
  - **test_data_setup.py**: Sets up test data by creating students and teachers.

- **src/quiznexusai/**: Main application code.

  - **admin.py**: Administrator functionalities.
  - **class_module.py**: Management of classes.
  - **encryption.py**: Handles encryption and decryption processes.
  - **exam.py**: Exam management and execution.
  - **main.py**: Entry point of the application.
  - **question.py**: Question management.
  - **result.py**: Result calculation and reporting.
  - **school.py**: School management.
  - **statistics_module.py**: Statistics management.
  - **teacher.py**: Teacher functionalities.
  - **user.py**: User management including registration and login.
  - **utils.py**: Utility functions and helpers.

- **tests/**: Testing scripts.

  - **test_integration.py**: Integration tests to verify system functionality.

- **setup.py**: Configuration script for project setup.
- **environment.yml**: Conda environment configuration file.
- **README.md**: Project documentation.
- **LICENSE**: Licensing information.
- **.gitignore**: Specifies files and directories to be ignored by Git.

## **Installation**

### **Prerequisites**

- **Conda:** Ensure that [Conda](https://docs.conda.io/en/latest/) is installed on your system for package and environment management.
- **Python 3.9:** The project is compatible with Python version 3.9.

### **Steps**

1. **Clone the Repository**

   ```bash
   git clone https://github.com/your_username/MultiPartQuizApp.git
   cd MultiPartQuizApp
   ```

2. **Set Up the Conda Environment**

   ```bash
   conda env create -f environment.yml
   conda activate quiz_app_env
   ```

3. **Run the Setup Script**

   The `setup.py` script will automatically create the `.env` file required for encryption.

   ```bash
   python setup.py
   ```

4. **Generate AES Keys**

   Generate the AES encryption key and IV by running the following script:

   ```bash
   python scripts/generate_keys.py
   ```

   Add the generated `AES_KEY` and `AES_IV` values to the `.env` file.

5. **Set Up Test Data**

   Before simulating student exams, set up the necessary test data by creating students and teachers:

   ```bash
   python scripts/test_data_setup.py
   ```

6. **Encrypt Data Files (If Needed)**

   To encrypt specific data files, use the encryption script:

   ```bash
   python scripts/encrypt_files.py
   ```

   Similarly, to decrypt encrypted files:

   ```bash
   python scripts/decrypt_files.py
   ```

### **Troubleshooting**

- **Conda Commands Not Working:**

  - Ensure that Conda is correctly installed. Follow the [official Conda installation guide](https://docs.conda.io/projects/conda/en/latest/user-guide/install/index.html) if issues persist.

- **AES Keys Not Generating:**

  - Verify that the `.env` file is properly created and that you have the necessary permissions to write to it.

- **Dependency Installation Errors:**

  - Ensure that the `environment.yml` file specifies compatible package versions. Update Conda if necessary:

    ```bash
    conda update conda
    ```

## **Usage**

### **Running the Application**

Start the main application by executing:

```bash
python src/quiznexusai/main.py
```

### **User Roles**

- **Administrator:**

  - Create and manage users, teachers, schools, classes, and questions.
  - Access detailed statistics and performance reports.

- **Teacher:**

  - Add, update, or delete questions within assigned sections.
  - View statistics related to their classes and schools.

- **Student:**
  - Register and log in to attempt exams.
  - View personal exam results and performance compared to class and school averages.

### **Student Exam Simulation**

To simulate student exam attempts, follow these steps:

1. **Set Up Test Data (If Not Already Done)**

   Ensure that students and teachers are created by running the test data setup script:

   ```bash
   python scripts/test_data_setup.py
   ```

2. **Simulate Student Exams**

   Run the simulation script to perform automated exam attempts by students:

   ```bash
   python scripts/simulate_student_actions.py
   ```

   This script will automatically create exam attempts for the created students and update the statistical data accordingly.

## **Tests**

### **Running Integration Tests**

To verify the integrity and functionality of the system, execute the integration tests as follows:

1. **Activate the Conda Environment**

   ```bash
   conda activate quiz_app_env
   ```

2. **Run the Tests**

   ```bash
   pytest tests/test_integration.py
   ```

   This command will execute all test scenarios defined in the `test_integration.py` file, ensuring that data setup, exam simulations, and statistical updates are functioning correctly.

### **Purpose of Tests**

- **Data Setup Verification:** Ensures that test data for schools, classes, students, and teachers are correctly created.
- **Exam Simulation Validation:** Confirms that simulated exam attempts behave as expected.
- **Statistics Accuracy:** Checks that statistical data is accurately updated based on exam results.

## **Post-Installation**

- **Create Admin Account:**

  - If an admin account was not created during setup, run the setup script or use the registration feature to create the first admin user.

- **Secure Your Environment:**
  - Protect the `.env` file and AES keys by setting appropriate file permissions to prevent unauthorized access.

## **Contributing**

Contributions are welcome! To contribute to the project, follow these steps:

1. **Fork the Repository**

   Fork the project repository to your GitHub account.

2. **Create a New Branch**

   Create a new branch for your feature or bug fix:

   ```bash
   git checkout -b feature/your-feature-name
   ```

3. **Make Changes**

   Implement your changes and commit them with descriptive messages.

4. **Push to Your Fork**

   Push your changes to your forked repository:

   ```bash
   git push origin feature/your-feature-name
   ```

5. **Create a Pull Request**

   Open a pull request from your forked repository to the main repository, detailing your changes and their purpose.

## **License**

This project is licensed under the [MIT License](LICENSE).

## **Contact**

For questions, feedback, or support, please reach out to [email@example.com](mailto:email@example.com).

---

**Note:** All data files within the project are encrypted for security. Ensure that the AES keys in the `.env` file are kept confidential to maintain data integrity and protection.
