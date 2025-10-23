from flask_sqlalchemy import SQLAlchemy
from datetime import datetime

db = SQLAlchemy()

class Instructor(db.Model):
    __tablename__ = 'instructors'
    InstructorID = db.Column(db.Integer, primary_key=True)
    Name = db.Column(db.String(100))
    Email = db.Column(db.String(100), unique=True)
    Password = db.Column(db.String(256))

    students = db.relationship('Student', backref='instructor', lazy=True)
    classes = db.relationship('Class', backref='instructor', lazy=True)
    questions = db.relationship('Question', backref='instructor', lazy=True)


class Student(db.Model):
    __tablename__ = 'students'
    StudentID = db.Column(db.Integer, primary_key=True)
    Name = db.Column(db.String(100))
    Email = db.Column(db.String(100), unique=True)
    Password = db.Column(db.String(256))
    InstructorID = db.Column(db.Integer, db.ForeignKey('instructors.InstructorID'))

    submissions = db.relationship('Submission', backref='student', lazy=True)


class Class(db.Model):
    __tablename__ = 'classes'
    ClassID = db.Column(db.Integer, primary_key=True)
    InstructorID = db.Column(db.Integer, db.ForeignKey('instructors.InstructorID'))
    S3FolderPath = db.Column(db.Text)


class Question(db.Model):
    __tablename__ = 'questions'
    QuestionID = db.Column(db.Integer, primary_key=True)
    InstructorID = db.Column(db.Integer, db.ForeignKey('instructors.InstructorID'))
    QuestionText = db.Column(db.Text)
    TestCases = db.Column(db.JSON)
    Status = db.Column(db.String(20), default='open') # or 'closed'
    Results = db.Column(db.JSON, nullable=True)

    submissions = db.relationship('Submission', backref='question', lazy=True)


class Submission(db.Model):
    __tablename__ = 'submissions'
    SubmissionID = db.Column(db.Integer, primary_key=True)
    StudentID = db.Column(db.Integer, db.ForeignKey('students.StudentID'))
    QuestionID = db.Column(db.Integer, db.ForeignKey('questions.QuestionID'))
    S3FilePath = db.Column(db.Text)
    Score = db.Column(db.Float)
    Feedback = db.Column(db.Text)