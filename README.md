İşte daha temiz, düzenli ve profesyonel bir formatta hazırlanmış yeni `README.md` dosyası:

````markdown
# MultiPartQuizApp

**MultiPartQuizApp** is a secure, multi-section exam management system designed for both exam takers and administrators. It supports encrypted data processing, multiple question types, and detailed result tracking.

---

## Table of Contents

- [Overview](#overview)
- [Key Features](#key-features)
- [Directory Structure](#directory-structure)
- [Quick Start](#quick-start)
- [Documentation](#documentation)
- [License](#license)
- [Contributing](#contributing)
- [Contact](#contact)

---

## Overview

MultiPartQuizApp provides a secure platform for conducting exams with the following main capabilities:

- **User Management**: Register, log in, and track exam attempts.
- **Admin Management**: Add, update, delete questions, and manage users.
- **Exam Execution**: Timed exams with support for True/False, Single Choice, and Multiple Choice questions.
- **Result Management**: Detailed tracking of results for each user.

This project is implemented in Python with a command-line interface for simplicity and security.

---

## Key Features

1. **User Management**

   - Registration and login functionality.
   - Tracks attempts and results for individual users.

2. **Admin Management**

   - Secure access for admins with a master password.
   - CRUD (Create, Read, Update, Delete) operations for users and questions.

3. **Exam Management**

   - Timed exams with multiple sections.
   - Different question types: True/False, Single Choice, Multiple Choice.

4. **Result Tracking**

   - Section-wise results and pass/fail assessment.
   - Securely stores user data and exam history.

5. **Encryption**
   - Passwords and sensitive data are encrypted using industry-standard techniques.

---

## Directory Structure

The project is organized as follows:

```plaintext
MultiPartQuizApp/
├── data/                     # JSON data storage
│   ├── answers/              # Correct answers
│   ├── questions/            # Question files
│   └── users/                # User data
├── docs/                     # Documentation files
│   ├── Installation.md       # Installation guide
│   ├── Usage.md              # Usage instructions
│   ├── Tests.md              # Testing details
│   ├── Troubleshooting.md    # Troubleshooting guide
│   ├── Best_Practices.md     # Best practices and tips
│   ├── Contributing.md       # Contribution guidelines
│   └── License.md            # License details
├── src/                      # Source code files
├── test/                     # Unit tests
├── .gitignore                # Git ignore rules
├── LICENSE                   # Project license
├── requirements.txt          # Python dependencies
├── environment.yml           # Conda environment configuration
└── README.md                 # Main project documentation
```
````

---

## Quick Start

### Prerequisites

Ensure the following software is installed:

- **Miniconda** or **Anaconda**
- **Python 3.9 or higher**
- **Git**

### Setup Instructions

1. Clone the repository:

   ```bash
   git clone https://github.com/username/MultiPartQuizApp.git
   cd MultiPartQuizApp
   ```

2. Create and activate the Conda environment:

   ```bash
   conda env create -f environment.yml
   conda activate quiz_app_env
   ```

3. Install Python dependencies:

   ```bash
   pip install -r requirements.txt
   ```

4. Run the application:

   ```bash
   python src/main.py
   ```

For detailed installation instructions, refer to the [Installation Guide](./docs/Installation.md).

---

## Documentation

Detailed guides are available in the `docs/` directory:

- [Installation Guide](./docs/Installation.md)
- [Usage Instructions](./docs/Usage.md)
- [Running Tests](./docs/Tests.md)
- [Troubleshooting](./docs/Troubleshooting.md)

**Thank you for using MultiPartQuizApp! Happy coding!**

```

```
