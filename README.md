# AutoGraderAI

## Overview

AutoGraderAI is a full-stack, cloud-native platform for automated code grading, feedback, and plagiarism detection. It supports both **students** and **instructors** with a seamless experience, leveraging AWS, Flask, React, and advanced AI models for code evaluation and feedback.

**Note:** For simplicity, each student is assigned a unique instructor (one-to-one mapping). This design streamlines class and question management, but can be easily extended for more complex relationships.

---

## 🏗️ Architecture

- **Backend:** Flask REST API, JWT Auth, AWS S3, Amazon Bedrock, Plagiarism Detection via SageMaker & Lambda
- **Frontend:** React (Vite), Tailwind CSS, Monaco Editor
- **Database:** Amazon RDS - PostgreSQL (SQLAlchemy ORM)
- **Cloud:** AWS S3, Lambda, API Gateway, Bedrock, SageMaker

![Architecture Diagram](https://app.eraser.io/workspace/Ku0BayJcOVZEeOyf6OPx?origin=share)

---

## ✨ Features

### Student Portal
- Secure login via AWS Cognito
- Dashboard: View enrolled classes
- Attempt coding questions with Monaco Editor
- Test run code before final submission
- Submit code for auto-grading
- Receive instant feedback and scores
- View results for closed questions

### Instructor Portal
- Secure login via AWS Cognito
- Dashboard: Manage classes and questions
- Add new coding questions with test cases
- View all student submissions
- Evaluate and close questions
- Run plagiarism detection on submissions
- View detailed plagiarism reports

### AI & Cloud Integrations
- **Code Feedback:** Amazon Bedrock (Claude 3 Sonnet)
- **Plagiarism Detection:** SageMaker, Lambda, API Gateway
- **Code Storage:** AWS S3

#### Plagiarism Detection Flow
- **Embeddings Generation:** When a student submits code, the server generates code embeddings using GraphCodeBERT and stores them in the `embeddings/` directory in the S3 bucket. This step is performed server-side (not in SageMaker) to avoid free instance limitations. The embeddings module is fully modular and can be integrated into SageMaker if you use a paid instance.
- **Plagiarism Check:** When an instructor closes a question, the backend calls the API Gateway, which triggers a Lambda function. The Lambda then calls SageMaker to run the plagiarism checker using the pre-generated embeddings from S3.

---

## 🗂️ Project Structure

```
AutoGraderAI/
├── app.py                  # Main Flask backend
├── models.py               # SQLAlchemy models
├── requirements.txt        # Backend dependencies
├── S3Handler.py            # S3 upload utility
├── schema.md / schema.sql  # Database schema
├── API_Gateway/            # Lambda & API Gateway integration
│   ├── connect_api_gateway.py
│   └── test_api.py
├── beforeECS/              # ECS evaluation service
│   ├── app_ECS.py
│   ├── Dockerfile
│   └── requirements.txt
├── FeedbackFolder/         # Code feedback via Bedrock
│   ├── feedback.py
│   └── test_feedback.py
├── plagiarism2/            # Plagiarism detection & embeddings
│   ├── embeddings.py
│   └── requirements.txt
├── frontend-vite/          # React frontend
│   ├── src/
│   └── README.md
└── uploads/                # Temporary code uploads
```

---

## 🧑‍💻 Backend API Endpoints

### Student Endpoints
- `GET /api/student/classes` — List enrolled classes
- `GET /api/student/class/<class_id>` — List questions in a class
- `GET /api/student/class/<class_id>/<question_id>` — Get question details & status
- `POST /api/student/run/<question_id>` — Test run code
- `POST /api/student/submission/<question_id>` — Submit code for grading

### Instructor Endpoints
- `GET /api/instructor/classes` — List classes taught
- `GET /api/instructor/class/<class_id>` — List questions in a class
- `POST /api/instructor/class/<class_id>/question` — Add new question
- `GET /api/instructor/class/<class_id>/<question_id>` — Get question results
- `POST /api/instructor/evaluate/<question_id>` — Evaluate & close question (plagiarism check)

---

## 🗄️ Database Schema

See [`schema.md`](./schema.md) and [`schema.sql`](./schema.sql) for full details.

- **Instructor**: Manages classes & questions
- **Student**: Enrolls in classes, submits code
- **Class**: Linked to instructor
- **Question**: Linked to class & instructor, has test cases
- **Submission**: Linked to student & question, stores S3 path, score, feedback

---

## ⚡ Key Modules

- **app.py**: Main Flask app, JWT auth, routes for students/instructors
- **models.py**: SQLAlchemy ORM models
- **S3Handler.py**: Uploads code files to AWS S3
- **FeedbackFolder/feedback.py**: Gets code feedback from Amazon Bedrock
- **plagiarism2/embeddings.py**: Generates code embeddings for plagiarism detection
	- Embeddings are generated server-side and stored in S3 (`embeddings/`). This is modular and can be moved to SageMaker for paid instances.
- **beforeECS/app_ECS.py**: Calls remote code evaluation service

---

## 🖥️ Frontend

See [`frontend-vite/README.md`](./frontend-vite/README.md) for full details.

- **React 18** + **Vite** + **Tailwind CSS**
- Role-based dashboards for students & instructors
- Monaco Editor for code input
- Toast notifications, modern UI

---

## 🛠️ Setup & Installation

### Backend
```bash
# Clone repo
cd AutoGraderAI
python -m venv .venv
.\.venv\Scripts\activate
pip install -r requirements.txt

# Set up environment variables (.env)
# AWS credentials, DB URL, Cognito config, etc.

# Run Flask app
python app.py
```

### Frontend
```bash
cd frontend-vite
npm install
npm run dev
```

---

## ☁️ Cloud Deployment

- **AWS S3**: Stores code submissions & embeddings
- **Lambda & API Gateway**: Plagiarism detection
- **Amazon Bedrock**: Code feedback
- **SageMaker**: Embedding generation
	- *Note: Embeddings are currently generated server-side due to free instance limitations. For paid SageMaker instances, the embeddings module can be integrated directly into SageMaker.*
	- The API Gateway triggers Lambda, which calls SageMaker for plagiarism checking when an instructor closes a question.

---

## 🧩 Extensibility

- Add new question types, languages, or evaluation logic
- Integrate additional AI models for feedback
- Support for more cloud providers

---

## 📄 License

MIT License

---

## 💬 Feedback & Issues

Please open issues or pull requests on [GitHub](https://github.com/CloudQuotient/AutoGraderAI).
