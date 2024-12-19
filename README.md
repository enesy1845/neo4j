````md
# Exam Management System

This project is a simple exam management system that allows students to take exams, teachers to add questions and view statistics, and administrators to manage users and view global school statistics. It also includes the functionality to migrate questions and answers from JSON files into a PostgreSQL database on the first run.

## Features

- **Student Panel:** Take exams (up to 2 attempts) and view results.
- **Teacher Panel:** View statistics and add new questions.
- **Admin Panel:** Manage users (add, update, delete, list) and view administrative statistics.
- **Automatic Database Migration:** Automatically imports questions and answers from JSON files into PostgreSQL on the first run.

## Prerequisites

- Docker & Docker Compose installed.
- Optional: `psql` client if you want to directly inspect the database.

## Installation & Setup

1. **Environment Variables (.env)**  
   Ensure you have a `.env` file in the project root with the following (adapt as needed):

   ```env
   DB_HOST=db
   DB_NAME=mydatabase
   DB_USER=myuser
   DB_PASSWORD=mypassword
   DB_PORT=5432

   ADMIN_USERNAME=ADMIN
   ADMIN_PASSWORD=ADMIN
   ADMIN_NAME=ADMIN
   ADMIN_SURNAME=ADMIN
   ```
````

2. **Build and Run with Docker**  
   Build the images and start the containers:

   ```bash
   docker-compose build
   docker-compose up
   ```

   - The `db` service (PostgreSQL) will start.
   - The `app` service will run `migrate_questions.py` once and then start `main.py`.
   - If questions have already been migrated, it will skip the migration on subsequent runs.

3. **Interacting with the System**  
   When `main.py` is running, it prompts for user input (registration, login, etc.) directly in the console. However, if you are running this in an environment where `input()` might cause issues, consider running the test scenario instead of the main program.

## Running the Test Scenario

If you want to run the test scenario (non-interactive), edit the `docker-compose.yml` file and change the `app` command:

```yaml
command: sh -c "python migrate_questions.py && python tests/test_scenario.py"
```

Then rebuild and run again:

```bash
docker-compose down
docker-compose build
docker-compose up
```

The test scenario will run automatically without any user input required.

## Updating the Code

If you make changes to the source code, simply rebuild and run again:

```bash
docker-compose down
docker-compose build
docker-compose up
```

## Database Inspection

You can connect to the PostgreSQL database running in the `db` container:

```bash
docker-compose exec db psql -U myuser -d mydatabase
```

Once inside the `psql` terminal, you can list tables and inspect data:

```sql
\dt
SELECT * FROM users;
```

## Common Issues & Solutions

- **`input()` Error in Docker:**  
  If `input()` causes issues inside the Docker environment (e.g., when running `main.py`), switch the command to run the test scenario or run the code outside Docker in a suitable environment.

- **Environment Variables in PowerShell:**  
  On Windows PowerShell, use `$Env:VAR_NAME` instead of `$VAR_NAME` to reference environment variables.

- **Package Installation (e.g., `rich`):**  
  If `rich` or other packages fail to install, ensure your network connection is stable, your `requirements.txt` is correct, and that you have updated `pip`:
  ```bash
  pip install --upgrade pip
  pip install rich
  ```

## License

This project is licensed under the MIT License. See the [LICENSE](LICENSE) file for details.

## Contributing

Contributions are welcome. Please see the [CONTRIBUTING.md](CONTRIBUTING.md) file for guidelines.

---

If you have any further questions or issues, feel free to reach out!

```

```
