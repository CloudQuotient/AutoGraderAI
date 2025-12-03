CREATE TABLE instructors (
    "InstructorID" SERIAL PRIMARY KEY,
    "Name" VARCHAR(100),
    "Email" VARCHAR(100) UNIQUE,
    "Password" VARCHAR(256)
);

CREATE TABLE students (
    "StudentID" SERIAL PRIMARY KEY,
    "Name" VARCHAR(100),
    "Email" VARCHAR(100) UNIQUE,
    "Password" VARCHAR(256),
    "InstructorID" INTEGER REFERENCES instructors("InstructorID")
);

CREATE TABLE classes (
    "ClassID" SERIAL PRIMARY KEY,
    "InstructorID" INTEGER REFERENCES instructors("InstructorID"),
    "S3FolderPath" TEXT
);

CREATE TABLE questions (
    "QuestionID" SERIAL PRIMARY KEY,
    "InstructorID" INTEGER REFERENCES instructors("InstructorID"),
    "QuestionText" TEXT,
    "TestCases" JSON,
    "Status" VARCHAR(20) DEFAULT 'open',
    "Results" JSON
);

CREATE TABLE submissions (
    "SubmissionID" SERIAL PRIMARY KEY,
    "StudentID" INTEGER REFERENCES students("StudentID"),
    "QuestionID" INTEGER REFERENCES questions("QuestionID"),
    "S3FilePath" TEXT,
    "Score" JSON,
    "Feedback" TEXT
);
