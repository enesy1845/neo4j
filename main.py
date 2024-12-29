# main.py

import uvicorn
from fastapi import FastAPI
from tools.database import init_db
from routers import auth, users, exams, questions, stats

app = FastAPI(title="Examination System API (Pydantic Updated)")

# Proje ilk ayağa kalkarken DB tablolarını oluşturup seed edelim
init_db()

# Router'ları ekle
app.include_router(auth.router, prefix="/auth", tags=["Auth"])
app.include_router(users.router, prefix="/users", tags=["Users"])
app.include_router(exams.router, prefix="/exams", tags=["Exams"])
app.include_router(questions.router, prefix="/questions", tags=["Questions"])
app.include_router(stats.router, prefix="/stats", tags=["Statistics"])

if __name__ == "__main__":
    uvicorn.run("main:app", host="0.0.0.0", port=8000, reload=True)
