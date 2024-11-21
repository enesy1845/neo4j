# MultiPartQuizApp

**MultiPartQuizApp** is a secure, multi-section exam management system that allows users to take exams and enables admins to manage exam content. Featuring encrypted data processing, the system supports various question types and maintains detailed results for each user.

## Table of Contents

- [Project Overview](#project-overview)
- [Directory Structure](#directory-structure)
- [Main Features](#main-features)
- [Installation and Setup](#installation-and-setup)
  - [1. Requirements](#1-requirements)
  - [2. Cloning the Project](#2-cloning-the-project)
  - [3. Setting Up the Conda Environment](#3-setting-up-the-conda-environment)
  - [4. Installing Required Packages](#4-installing-required-packages)
  - [5. Creating the First Admin Account](#5-creating-the-first-admin-account)
  - [6. Running the Application](#6-running-the-application)
- [Tests](#tests)
- [Best Practices and Tips](#best-practices-and-tips)
- [License](#license)
- [Troubleshooting](#troubleshooting)
- [About the Project](#about-the-project)
- [Support and Contributions](#support-and-contributions)

## Project Overview

The application comprises the following main features:

- **User Management**: User registration, tracking exam attempts, and access management.
- **Admin Management**: Admins can add, update, delete questions, and manage users.
- **Question Management**: Handling different types of questions (True/False, Single Choice, Multiple Choice).
- **Exam Management**: Timed exam administration and result recording.
- **Encryption**: Encryption methods to ensure the security of all user and exam data.

## Directory Structure

```
MultiPartQuizApp/
├── data/                     # JSON data storage
│   ├── answers/              # Correct answers
│   │   └── answers.json      # JSON file containing correct answers for questions
│   ├── questions/            # Question files
│   │   ├── multiple_choice_questions.json  # Multiple-choice questions
│   │   ├── single_choice_questions.json    # Single-choice questions
│   │   └── true_false_questions.json       # True/False questions
│   └── users/                # User data
│       └── users.json        # JSON file storing user and admin information
├── docs/                     # Documentation
│   └── README.md
├── src/                      # Source code files
│   ├── admin.py              # Admin management
│   ├── exam.py               # Exam management
│   ├── main.py               # Entry point of the application
│   ├── question.py           # Question management
│   ├── setup_admin.py        # Initial admin setup
│   ├── user.py               # User management
│   └── utils.py              # Utility functions
├── test/                     # Unit tests
│   ├── test_exam.py          # Tests for exam functionalities
│   ├── test_integration.py   # Integration tests
│   ├── test_question.py      # Tests for question management
│   ├── test_user.py          # Tests for user management
├── .gitignore
├── LICENSE
├── requirements.txt          # Required Python packages
├── environment.yml           # Conda environment configuration
└── README.md                 # Project documentation
```

## Main Features

### 1. User Management (`user.py`)

- **Registration & Login**: Users can register, log in, and track their exam attempts.
- **CRUD Operations**: Listing, updating, and deleting user information.

### 2. Admin Management (`admin.py`)

- **Question and User Management**: Admins can add, update, delete questions, and manage users.
- **Admin Authentication**: Admin access requires master password verification.

### 3. Question Management (`question.py`)

- **Support for Multiple Question Types**: True/False, Single Choice, and Multiple Choice questions.
- **CRUD Operations**: Creating, listing, updating, and deleting questions.

### 4. Exam Management (`exam.py`)

- **Timed Exams**: Users can participate in exams with specified time limits.
- **Result Calculation**: Points are calculated and recorded for each section.

### 5. Result Management (`utils.py` and `user.py`)

- **Result Tracking**: User results are recorded and tracked for each section.
- **Pass/Fail Assessment**: Determines whether the user meets the passing criteria.

## Installation and Setup

This section provides step-by-step instructions on how to set up and run the project from scratch on your computer.

### **1. Requirements**

Ensure the following software is installed on your computer for the project to run:

- **Miniconda** or **Anaconda**
- **Python 3.9 or higher**
- **Git**

**Check Installation:**

```bash
conda --version
python --version
git --version
```

If these commands return version information, the software is installed. Otherwise, download and install them from the official websites:

- Miniconda: [https://docs.conda.io/en/latest/miniconda.html](https://docs.conda.io/en/latest/miniconda.html)
- Python: [https://www.python.org/downloads/](https://www.python.org/downloads/)
- Git: [https://git-scm.com/downloads](https://git-scm.com/downloads)

### **2. Cloning the Project**

Open your terminal or command prompt and follow these steps:

1. **Navigate to the Directory Where You Want to Clone the Project:**

   ```bash
   cd Desktop  # Or any other desired directory
   ```

2. **Clone the Project:**

   ```bash
   git clone https://github.com/username/MultiPartQuizApp.git
   ```

   **Note:** Replace `username` with the actual GitHub username of the project repository.

3. **Enter the Project Directory:**

   ```bash
   cd MultiPartQuizApp
   ```

### **3. Setting Up the Conda Environment**

Virtual environments are used to isolate project dependencies.

1. **Create the Conda Environment Using `environment.yml`:**

   ```bash
   conda env create -f environment.yml
   ```

   - **Explanation:**
     - This command creates a new Conda environment based on the specifications in the `environment.yml` file, including Python version and required packages.

2. **Activate the Environment:**

   ```bash
   conda activate quiz_app_env
   ```

   - **Note:** If the environment name is different in your `environment.yml`, use the corresponding name.

### **4. Installing Required Packages**

Pip packages are managed separately to handle dependencies not available through Conda.

1. **Upgrade pip:**

   ```bash
   pip install --upgrade pip
   ```

2. **Install Required Packages:**

   ```bash
   pip install -r requirements.txt
   ```

   **Content of `requirements.txt`:**

   ```
   bcrypt==4.0.1
   inputimeout==1.0.4
   ```

   **Note:** Remember to add any additional dependencies to this file as needed for the project.

### **5. Creating the First Admin Account**

When running the program for the first time, if there is no admin user in the system, the first admin user will be created automatically.

1. **Run the Application:**

   ```bash
   python ./src/main.py
   ```

2. **Enter Admin Information:**

   The program will prompt you to create the first admin user by requesting the necessary information:

   - Username
   - Password
   - Your Name
   - Your Surname
   - Your Phone Number

   **Note:** This step is only performed during the first run. Subsequent runs will skip this step.

### **6. Running the Application**

1. **Start the Main Program:**

   ```bash
   python src/main.py
   ```

2. **Log In or Register:**

   Upon running, the application will present you with options:

   - `1`: Register
   - `2`: Login
   - `3`: Exit

   **Admin Operations:**

   - Log in as an admin to add, update, or delete questions.
   - Manage users by listing and deleting them.
   - Create new admins (a master password may be required).

   **User Operations:**

   - Register and log in as a user.
   - Participate in exams and view your results.

---

## Tests

Run all tests using the following command:

```bash
python -m unittest discover -s test
```

### Test Coverage

- **test_user.py**: Tests for user registration, login, and attempt tracking.
- **test_exam.py**: Tests for starting exams, time management, and question processing.
- **test_question.py**: Tests for question management.
- **test_integration.py**: Tests interactions between modules to ensure complete workflow validation.

## Best Practices and Tips

### 1. Using Conda Environments

- Use Conda environments to isolate project dependencies.
- To activate the environment:

  ```bash
  conda activate quiz_app_env
  ```

- To deactivate the environment:

  ```bash
  conda deactivate
  ```

### 2. Managing Dependencies

- After installing new packages, update the `requirements.txt` file:

  ```bash
  pip freeze > requirements.txt
  ```

### 3. Security and Privacy

- **Passwords and Sensitive Information**: User passwords are securely hashed using `bcrypt`.
- **Master Password**: Change the master password used for creating admins to a strong password and store it securely.

### 4. Debugging

- **Logging**: Use `print` statements or logging as needed to identify and debug issues.
- **User Inputs**: Validate user inputs to prevent potential errors.

## License

This project is licensed under the MIT License. See the [LICENSE](LICENSE) file for more information.

---

## Troubleshooting

### **1. Conda Commands Not Recognized**

- **Ensure Conda is Added to PATH:**
  - During installation, check the option to 'Add Anaconda to my PATH environment variable'.
- **Initialize Conda for Your Shell:**
  ```bash
  conda init
  ```
- **Restart Your Terminal or PowerShell.**

### **2. Module Not Found Errors**

- **Ensure All Required Packages are Installed:**
  ```bash
  pip install -r requirements.txt
  ```

### **3. Virtual Environment Activation Issues**

- **Run `conda init` Before Activating the Environment and Restart Your Terminal:**
  ```bash
  conda init
  ```
- **Set Execution Policy in PowerShell:**
  ```powershell
  Set-ExecutionPolicy -ExecutionPolicy RemoteSigned -Scope CurrentUser
  ```
  - **Explanation:**
    - This allows PowerShell to execute scripts necessary for Conda.

### **4. PowerShell Profile File Not Found**

If you encounter issues related to the Conda initialization in PowerShell, follow these steps:

1. **Check if the Profile Exists:**

   ```powershell
   Test-Path $PROFILE
   ```

   - **Output:**
     - `True`: Profile exists.
     - `False`: Profile does not exist.

2. **Create the Profile if It Does Not Exist:**

   ```powershell
   New-Item -Type File -Path $PROFILE -Force
   ```

3. **Initialize Conda for PowerShell:**

   ```powershell
   conda init powershell
   ```

4. **Set Execution Policy:**

   ```powershell
   Set-ExecutionPolicy -ExecutionPolicy RemoteSigned -Scope CurrentUser
   ```

   - **Note:** Confirm the change by typing `Y` when prompted.

5. **Restart PowerShell or Your Terminal.**

### **5. Prefix Already Exists Error**

If you encounter the following error:

```
CondaValueError: prefix already exists: C:\Users\yilma\Miniconda3\envs\quiz_app_env
```

- **Solution: Remove the Existing Environment and Recreate It:**
  ```powershell
  conda remove --name quiz_app_env --all
  conda env create -f environment.yml
  ```

### **6. Conda Initialization Issues**

If `conda activate` still doesn't work after following the above steps:

- **Ensure Your `environment.yml` is Correct:**

  - Remove the `prefix` line if present.
  - Use a supported Python version (e.g., `python=3.10`).

- **Sample `environment.yml`:**

  ```yaml
  name: quiz_app_env
  channels:
    - defaults
    - conda-forge
  dependencies:
    - python=3.10
    - pip
    - pip:
        - -r requirements.txt
  ```

- **Recreate the Environment:**
  ```powershell
  conda env create -f environment.yml
  ```

### **7. General Tips**

- **Ensure You Are in the Correct Directory When Running Commands.**
- **Verify the `environment.yml` File is Properly Formatted.**
- **Check for Typos in Commands and File Paths.**

---

## About the Project

This project is a console-based application developed using Python. The user interface is interactive via the command line. The application provides a simple and secure solution for organizing and managing educational exams.

---

## Support and Contributions

For feedback or contributions related to the project, please reach out via GitHub.

---

**Thank You and Happy Coding!**

---

**Important Note:**

- **`.env` File No Longer Used:**

  - The previously used `.env` file and related code have been removed.
  - Encryption processes and other sensitive information are managed securely within the code or through other secure methods.

- **Summary of Installation Steps:**
  1. Clone the project.
  2. Create and activate the Conda environment using `environment.yml`.
  3. Install required packages.
  4. Run the application and create the first admin account.

---

**Note:** This README file contains all the necessary information to set up and run the project smoothly. If you encounter any issues, refer to the [Troubleshooting](#troubleshooting) section or contact us for support.

---

## Updated `environment.yml` Example

Ensure your `environment.yml` file in the project root directory (`MultiPartQuizApp/`) looks like the following:

```yaml
name: quiz_app_env
channels:
  - defaults
  - conda-forge
dependencies:
  - python=3.10
  - pip
  - pip:
      - -r requirements.txt
```

**Notes:**

- **Python Version:** Set to `python=3.10` for stability. Adjust as needed based on project requirements.
- **Pip Packages:** Listed under `pip` to ensure packages in `requirements.txt` are installed correctly.
- **Channels:** Includes `defaults` and `conda-forge` for a broader range of packages.

## Using `environment.yml` to Create the Conda Environment

After cloning the project and navigating to the project directory, run the following commands to set up your Conda environment:

```bash
conda env create -f environment.yml
conda activate quiz_app_env
```

These steps will create the Conda environment as specified in the `environment.yml` file and activate it for use.

---

If you follow all these steps and still encounter issues, please provide detailed error messages and context so that further assistance can be provided.

---

**Happy Coding!**
