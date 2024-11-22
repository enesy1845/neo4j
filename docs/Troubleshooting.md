### 3.4 **Troubleshooting.md**

**Path:** `docs/Troubleshooting.md`

**Content:**

```markdown
# Troubleshooting

This document provides solutions to common issues you may encounter while setting up or using the MultiPartQuizApp.

## 1. Conda Commands Not Recognized

### **Issue:**
Conda commands such as `conda activate` are not recognized in the terminal.

### **Solutions:**

- **Ensure Conda is Added to PATH:**
  - During installation, ensure the option to 'Add Anaconda to my PATH environment variable' is selected.

- **Initialize Conda for Your Shell:**
  ```bash
  conda init
````

- **Restart Your Terminal or Command Prompt:**
  - After initializing, restart the terminal to apply changes.

## 2. Module Not Found Errors

### **Issue:**

Errors indicating that certain Python modules are not found.

### **Solutions:**

- **Ensure All Required Packages are Installed:**

  ```bash
  pip install -r requirements.txt
  ```

- **Activate the Correct Conda Environment:**

  ```bash
  conda activate quiz_app_env
  ```

- **Check for Typos in Import Statements:**
  - Ensure that module names are correctly spelled in your Python files.

## 3. Virtual Environment Activation Issues

### **Issue:**

Unable to activate the Conda environment using `conda activate quiz_app_env`.

### **Solutions:**

- **Run `conda init` and Restart Terminal:**

  ```bash
  conda init
  ```

  - Restart the terminal after running the command.

- **Set Execution Policy in PowerShell (Windows Only):**
  ```powershell
  Set-ExecutionPolicy -ExecutionPolicy RemoteSigned -Scope CurrentUser
  ```
  - **Explanation:** This allows PowerShell to execute scripts necessary for Conda.

## 4. PowerShell Profile File Not Found

### **Issue:**

Errors related to the Conda initialization in PowerShell due to a missing profile file.

### **Solutions:**

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

5. **Restart PowerShell or Your Terminal:**

## 5. Prefix Already Exists Error

### **Issue:**

Error message:

```
CondaValueError: prefix already exists: C:\Users\username\Miniconda3\envs\quiz_app_env
```

### **Solutions:**

- **Remove the Existing Environment and Recreate It:**
  ```bash
  conda remove --name quiz_app_env --all
  conda env create -f environment.yml
  ```

## 6. Conda Initialization Issues

### **Issue:**

`conda activate` still doesn't work after following the above steps.

### **Solutions:**

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
  ```bash
  conda env create -f environment.yml
  ```

## 7. General Tips

- **Ensure You Are in the Correct Directory When Running Commands.**
- **Verify the `environment.yml` File is Properly Formatted.**
- **Check for Typos in Commands and File Paths.**
- **Consult the [Contributing Guidelines](./Contributing.md) for Additional Help.**

````
