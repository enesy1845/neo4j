# tools/models.py
import uuid
from sqlalchemy import Column, String, Integer, Float, Boolean, DateTime, ForeignKey, Text, Table
from sqlalchemy.dialects.postgresql import UUID as PGUUID
from sqlalchemy.orm import relationship
from tools.database import Base
from datetime import datetime
import json

# Association Table for Exam and Question
exam_question_association = Table(
    'exam_question_association',
    Base.metadata,
    Column('exam_id', PGUUID(as_uuid=True), ForeignKey('exams.exam_id'), primary_key=True),
    Column('question_id', PGUUID(as_uuid=True), ForeignKey('questions.id'), primary_key=True)
)

class School(Base):
    __tablename__ = "schools"
    school_id = Column(PGUUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    name = Column(String(255), unique=True, nullable=False)
    users = relationship("User", back_populates="school")
    exams = relationship("Exam", back_populates="school")
    statistics = relationship("Statistics", back_populates="school")

class User(Base):
    __tablename__ = "users"
    user_id = Column(PGUUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    username = Column(String(255), unique=True, nullable=False)
    password = Column(Text, nullable=False)
    name = Column(String(255), nullable=False)
    surname = Column(String(255), nullable=False)
    phone_number = Column(String(50), nullable=True)
    role = Column(String(50), nullable=False)
    attempts = Column(Integer, default=0)
    last_attempt_date = Column(DateTime, nullable=True)
    score1 = Column(Float, default=0)
    score2 = Column(Float, default=0)
    score_avg = Column(Float, default=0)
    class_name = Column(String(50), nullable=False)
    registered_section = Column(String(50), nullable=True)
    school_id = Column(PGUUID(as_uuid=True), ForeignKey("schools.school_id", ondelete='CASCADE'), nullable=False)
    school = relationship("School", back_populates="users")
    exams = relationship("Exam", back_populates="user", cascade="all, delete-orphan")


class Question(Base):
    __tablename__ = "questions"
    id = Column(PGUUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    external_id = Column(String, unique=True, nullable=False)
    section = Column(Integer, nullable=False)
    question = Column(Text, nullable=False)
    points = Column(Integer, nullable=False, default=1)
    type = Column(String(50), nullable=False)
    choices = Column(Text, nullable=True)

    # Answer ile 1-1
    answer = relationship("Answer", back_populates="question", uselist=False)

    # DÜZELTME:
    # 'exams' => 'relationship("Exam", secondary=exam_question_association, back_populates="selected_questions")'
    # demek istiyoruz
    exams = relationship(
        "Exam",
        secondary=exam_question_association,
        back_populates="selected_questions"  # <-- karşının ismi 'selected_questions'
    )


    def get_choices_list(self):
        """
        Kolonumuz Text biçiminde JSON sakladığı için bu fonksiyonla python list/dict'e çevirebiliriz.
        """
        if self.choices:
            try:
                return json.loads(self.choices)
            except:
                pass
        return []

class Answer(Base):
    __tablename__ = "answers"
    id = Column(PGUUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    question_id = Column(PGUUID(as_uuid=True), ForeignKey("questions.id"), nullable=False)
    correct_answer = Column(Text, nullable=False)
    question = relationship("Question", back_populates="answer")

class Exam(Base):
    __tablename__ = "exams"
    exam_id = Column(PGUUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    user_id = Column(PGUUID(as_uuid=True), ForeignKey("users.user_id", ondelete='CASCADE'), nullable=False)
    class_name = Column(String(50), nullable=False)
    start_time = Column(DateTime, default=datetime.utcnow)
    end_time = Column(DateTime, nullable=True)
    school_id = Column(PGUUID(as_uuid=True), ForeignKey("schools.school_id", ondelete='CASCADE'), nullable=False)

    school = relationship("School", back_populates="exams")
    user = relationship("User", back_populates="exams")
    exam_answers = relationship("ExamAnswer", back_populates="exam", cascade="all, delete-orphan")

    # DÜZELTME:
    selected_questions = relationship(
        "Question",
        secondary=exam_question_association,
        back_populates="exams"  # <-- Karşı taraftaki 'exams' ile eşleşiyor
    )
class ExamAnswer(Base):
    __tablename__ = "exam_answers"
    id = Column(PGUUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    exam_id = Column(PGUUID(as_uuid=True), ForeignKey("exams.exam_id", ondelete='CASCADE'), nullable=False)
    question_id = Column(PGUUID(as_uuid=True), ForeignKey("questions.id", ondelete='CASCADE'), nullable=False)
    user_answer = Column(Text, nullable=False)
    is_correct = Column(Boolean, default=False)
    points_earned = Column(Integer, default=0)
    exam = relationship("Exam", back_populates="exam_answers")

class Statistics(Base):
    __tablename__ = "statistics"
    id = Column(PGUUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    class_name = Column(String(50), nullable=False)
    section_number = Column(Integer, nullable=False)
    correct_questions = Column(Integer, default=0)
    wrong_questions = Column(Integer, default=0)
    average_score = Column(Float, default=0.0)
    section_percentage = Column(Float, default=0.0)
    school_id = Column(PGUUID(as_uuid=True), ForeignKey("schools.school_id"), nullable=False)
    school = relationship("School", back_populates="statistics")
