# Database Schema Documentation

This document describes the database structure based on the SQLAlchemy models used in the project.

---

## **Instructors Table**
**Table:** `instructors`

| Column        | Type           | Constraints               |
|---------------|----------------|---------------------------|
| InstructorID  | Integer        | Primary Key (auto INC)    |
| Name          | String(100)    |                           |
| Email         | String(100)    | Unique                    |
| Password      | String(256)    |                           |

**Relationships:**
- **One instructor → many students**
- **One instructor → many classes**
- **One instructor → many questions**

---

## **Students Table**
**Table:** `students`

| Column        | Type           | Constraints                           |
|---------------|----------------|---------------------------------------|
| StudentID     | Integer        | Primary Key (auto INC)                |
| Name          | String(100)    |                                       |
| Email         | String(100)    | Unique                                |
| Password      | String(256)    |                                       |
| InstructorID  | Integer        | Foreign Key → instructors.InstructorID |

**Important Relationship Rule:**
- **Each student belongs to exactly one instructor**  
- **A student cannot have multiple instructors**

**Relationships:**
- One student → many submissions

---

## **Classes Table**
**Table:** `classes`

| Column        | Type        | Constraints                           |
|---------------|-------------|---------------------------------------|
| ClassID       | Integer     | Primary Key (auto INC)                |
| InstructorID  | Integer     | Foreign Key → instructors.InstructorID |
| S3FolderPath  | Text        |                                       |

**Relationship Rule:**  
- Each class is assigned to **one instructor**

---

## **Questions Table**
**Table:** `questions`

| Column        | Type        | Constraints                           |
|---------------|-------------|---------------------------------------|
| QuestionID    | Integer     | Primary Key (auto INC)                |
| InstructorID  | Integer     | Foreign Key → instructors.InstructorID |
| QuestionText  | Text        |                                       |
| TestCases     | JSON        |                                       |
| Status        | String(20)  | Default: `'open'`                     |
| Results       | JSON        | Nullable                              |

**Relationship Rule:**  
- Each question belongs to **one instructor**

**Relationships:**
- One question → many submissions

---

## **Submissions Table**
**Table:** `submissions`

| Column        | Type        | Constraints                           |
|---------------|-------------|---------------------------------------|
| SubmissionID  | Integer     | Primary Key (auto INC)                |
| StudentID     | Integer     | Foreign Key → students.StudentID      |
| QuestionID    | Integer     | Foreign Key → questions.QuestionID    |
| S3FilePath    | Text        |                                       |
| Score         | JSON        |                                       |
| Feedback      | Text        |                                       |

**Relationship Rules:**
- Each submission is made by **one student**
- Each submission corresponds to **one question**