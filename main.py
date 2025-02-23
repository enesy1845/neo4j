# main.py

import uvicorn
from fastapi import FastAPI
from starlette.middleware.sessions import SessionMiddleware
from fastapi.staticfiles import StaticFiles
from fastapi.templating import Jinja2Templates

# Veritabanı ve kullanıcı işlemleri
from tools.database import init_db, get_db
from tools.user import create_admin_user
# Soru–cevap migrasyonu için migrate_questions
from migrate_questions import main as migrate_main

# Routerlar
from routers import auth, users, exams, questions, stats, results
from routers.ui import ui_router

app = FastAPI(title="NexusAI Quiz App")

# Session Middleware
app.add_middleware(SessionMiddleware, secret_key="SESSION_SECRET_KEY", max_age=3600)

# Statik dosyalar ve template ayarları
app.mount("/static", StaticFiles(directory="static"), name="static")
templates = Jinja2Templates(directory="templates")


@app.on_event("startup")
def on_startup():
    """
    Uygulama başlarken:
    1) Neo4j Constraint'leri oluştur
    2) Admin kullanıcı + DefaultSchool oluştur
    3) JSON'dan soruları migrate et
    """
    init_db()  # Constraint oluşturma
    
    # Admin ve DefaultSchool oluşturma
    session = get_db()
    try:
        create_admin_user(session)
    finally:
        session.close()

    # JSON'dan sorular ve cevapları Neo4j'ye migrate et
    try:
        migrate_main()
    except Exception as e:
        print(f"Migrate error: {e}")


# API Router'ları
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
