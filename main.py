# main.py

import uvicorn
from fastapi import FastAPI
from starlette.middleware.sessions import SessionMiddleware
from fastapi.staticfiles import StaticFiles
from fastapi.templating import Jinja2Templates
# Database and user operations
from tools.database import init_db, get_db
from tools.user import create_admin_user
# Migrate questions from JSON
from migrate_questions import main as migrate_main
# Routers
from routers import auth, users, exams, questions, stats, results
from routers.ui import ui_router

app = FastAPI(title="NexusAI Quiz App")

# Session Middleware
app.add_middleware(SessionMiddleware, secret_key="SESSION_SECRET_KEY", max_age=3600)
# Static files and template configuration
app.mount("/static", StaticFiles(directory="static"), name="static")
templates = Jinja2Templates(directory="templates")

@app.on_event("startup")
def on_startup():
    """
    On application startup:
    1) Create Neo4j constraints
    2) Create Admin user and DefaultSchool
    3) Migrate questions from JSON
    """
    init_db()  # Create constraints
    # Create Admin and DefaultSchool
    session = get_db()
    try:
        create_admin_user(session)
    finally:
        session.close()
    # Migrate questions and answers from JSON to Neo4j
    try:
        migrate_main()
    except Exception as e:
        print(f"Migrate error: {e}")

# API Routers
app.include_router(auth.router, prefix="/auth", tags=["Auth"])
app.include_router(users.router, prefix="/users", tags=["Users"])
app.include_router(exams.router, prefix="/exams", tags=["Exams"])
app.include_router(questions.router, prefix="/questions", tags=["Questions"])
app.include_router(stats.router, prefix="/stats", tags=["Statistics"])
app.include_router(results.router, prefix="/students", tags=["Results"])
# UI Router (Jinja2)
app.include_router(ui_router, tags=["UI Pages"])

if __name__ == "__main__":
    uvicorn.run("main:app", host="0.0.0.0", port=8000, reload=True)
