# tools/database.py

import os
import time
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker, declarative_base
from dotenv import load_dotenv

load_dotenv()

DB_HOST = os.getenv("DB_HOST")
DB_NAME = os.getenv("DB_NAME")
DB_USER = os.getenv("DB_USER")
DB_PASSWORD = os.getenv("DB_PASSWORD")
DB_PORT = os.getenv("DB_PORT", "5432")

DATABASE_URL = f"postgresql://{DB_USER}:{DB_PASSWORD}@{DB_HOST}:{DB_PORT}/{DB_NAME}"

Base = declarative_base()

retries = 5
while retries > 0:
    try:
        engine = create_engine(DATABASE_URL, future=True)
        break
    except Exception as e:
        print(f"Database connection failed: {e}")
        retries -= 1
        time.sleep(5)

SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)

def get_db():
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()

def init_db():
    from tools.models import User, Question, Answer, Exam, ExamAnswer, Statistics, School
    from tools.migrate_questions import questions_already_migrated, main as migrate_questions_main

    # Tablolar oluştur
    School.__table__.create(bind=engine, checkfirst=True)
    User.__table__.create(bind=engine, checkfirst=True)
    Question.__table__.create(bind=engine, checkfirst=True)
    Answer.__table__.create(bind=engine, checkfirst=True)
    Exam.__table__.create(bind=engine, checkfirst=True)
    ExamAnswer.__table__.create(bind=engine, checkfirst=True)
    Statistics.__table__.create(bind=engine, checkfirst=True)

    seed_initial_data()

    with next(get_db()) as db:
        if not questions_already_migrated(db):
            migrate_questions_main()
        else:
            print("Sorular ve cevaplar zaten migrate edilmiş.")

def seed_initial_data():
    from tools.models import School
    with next(get_db()) as db:
        default_school = db.query(School).filter(School.name == "DefaultSchool").first()
        if not default_school:
            new_school = School(name="DefaultSchool")
            db.add(new_school)
            db.commit()
            db.refresh(new_school)
            print("DefaultSchool eklendi.")
        else:
            print("DefaultSchool zaten mevcut.")
