### 3.1 **Installation.md**

**Path:** `docs/Installation.md`

**Content:**

````markdown
# Installation and Setup

This document provides step-by-step instructions on how to set up and run the project from scratch on your computer.

## 1. Requirements

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
````

If these commands return version information, the software is installed. Otherwise, download and install them from the official websites:

- Miniconda: [https://docs.conda.io/en/latest/miniconda.html](https://docs.conda.io/en/latest/miniconda.html)
- Python: [https://www.python.org/downloads/](https://www.python.org/downloads/)
- Git: [https://git-scm.com/downloads](https://git-scm.com/downloads)

## 2. Cloning the Project

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

## 3. Setting Up the Conda Environment

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

## 4. Installing Required Packages

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

## 5. Creating the First Admin Account

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

## 6. Running the Application

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

````