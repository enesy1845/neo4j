# main.py
import uvicorn
from fastapi import FastAPI
from tools.database import init_db
from routers import auth, users, exams, questions, stats, results

app = FastAPI(title="Examination System API (Pydantic Updated)")

@app.on_event("startup")
def on_startup():
    init_db()

# Include Routers
app.include_router(auth.router, prefix="/auth", tags=["Auth"])
app.include_router(users.router, prefix="/users", tags=["Users"])
app.include_router(exams.router, prefix="/exams", tags=["Exams"])
app.include_router(questions.router, prefix="/questions", tags=["Questions"])
app.include_router(stats.router, prefix="/stats", tags=["Statistics"])
app.include_router(results.router, prefix="/students", tags=["Results"])

if __name__ == "__main__":
    uvicorn.run("main:app", host="0.0.0.0", port=8000, reload=True)
