from sqlalchemy import Column, String, Integer, ForeignKey, DateTime, Text, Boolean, Float
from sqlalchemy.orm import declarative_base, relationship
import datetime

Base = declarative_base()

class User(Base):
    __tablename__ = "users"
    id = Column(String, primary_key=True)
    email = Column(String, unique=True)
    role = Column(String)
    assignments = relationship("Assignment", back_populates="instructor")
    submissions = relationship("Submission", back_populates="student")

class Assignment(Base):
    __tablename__ = "assignments"
    id = Column(String, primary_key=True)
    title = Column(String)
    description = Column(Text)
    due_date = Column(DateTime)
    instructor_id = Column(String, ForeignKey("users.id"))
    instructor = relationship("User", back_populates="assignments")
    submissions = relationship("Submission", back_populates="assignment")
    test_cases = relationship("TestCase", back_populates="assignment")

class Submission(Base):
    __tablename__ = "submissions"
    id = Column(String, primary_key=True)
    assignment_id = Column(String, ForeignKey("assignments.id"))
    student_id = Column(String, ForeignKey("users.id"))
    s3_key = Column(String)
    filename = Column(String)
    submitted_at = Column(DateTime, default=datetime.datetime.utcnow)
    assignment = relationship("Assignment", back_populates="submissions")
    student = relationship("User", back_populates="submissions")
    grades = relationship("Grade", back_populates="submission")
    plagiarism_flags = relationship("PlagiarismFlag", back_populates="submission")

class TestCase(Base):
    __tablename__ = "test_cases"
    id = Column(Integer, primary_key=True)
    assignment_id = Column(String, ForeignKey("assignments.id"))
    input_data = Column(Text)
    expected_output = Column(Text)
    assignment = relationship("Assignment", back_populates="test_cases")

class Grade(Base):
    __tablename__ = "grades"
    id = Column(Integer, primary_key=True)
    submission_id = Column(String, ForeignKey("submissions.id"))
    score = Column(Float)
    feedback = Column(Text)
    submission = relationship("Submission", back_populates="grades")

class PlagiarismFlag(Base):
    __tablename__ = "plagiarism_flags"
    id = Column(Integer, primary_key=True)
    submission_id = Column(String, ForeignKey("submissions.id"))
    flagged = Column(Boolean)
    reason = Column(Text)
    submission = relationship("Submission", back_populates="plagiarism_flags")
