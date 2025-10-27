# Autograder Frontend

This is the frontend application for the Autograder system, built with React, Vite, and Tailwind CSS.

## Features

### Student Portal
- Login page with role-based authentication
- Dashboard displaying enrolled classes
- Class view showing all questions
- Question attempt page with Monaco Editor
- Test run functionality
- Final submission capability
- Results display for closed questions

### Instructor Portal
- Dashboard displaying all taught classes
- Class view with questions list
- Add new question with test cases
- View question results
- Evaluate submissions and close questions
- View plagiarism reports

## Tech Stack

- **React 18** - UI library
- **Vite** - Build tool and dev server
- **React Router** - Client-side routing
- **Tailwind CSS** - Utility-first CSS framework
- **Axios** - HTTP client
- **React Hot Toast** - Toast notifications
- **Monaco Editor** - Code editor component

## Installation

```bash
cd frontend-vite
npm install
```

## Running the Development Server

```bash
npm run dev
```

The app will be available at `http://localhost:3000`

**Note:** Make sure your Flask backend is running on `http://localhost:5000`

## Project Structure

```
frontend-vite/
├── src/
│   ├── pages/
│   │   ├── Login.jsx                   # Login page
│   │   ├── student/
│   │   │   ├── StudentDashboard.jsx    # Classes dashboard
│   │   │   ├── StudentClassView.jsx     # Questions list
│   │   │   └── StudentQuestionAttempt.jsx  # Code editor & submission
│   │   └── instructor/
│   │       ├── InstructorDashboard.jsx  # Classes dashboard
│   │       ├── InstructorClassView.jsx   # Questions list
│   │       └── InstructorQuestionView.jsx  # View results & evaluate
│   ├── components/
│   │   └── instructor/
│   │       └── AddNewQuestion.jsx       # Add question modal
│   ├── services/
│   │   └── api.js                       # Axios configuration
│   ├── App.jsx                          # Main app component
│   ├── routes.jsx                       # Route definitions
│   ├── main.jsx                         # Entry point
│   └── index.css                        # Global styles (Tailwind)
├── index.html
├── package.json
├── vite.config.js                       # Vite configuration
├── tailwind.config.js                   # Tailwind configuration
└── postcss.config.js                    # PostCSS configuration
```

## API Endpoints Used

### Student Endpoints

- `GET /api/student/classes` - Fetch all classes for student
- `GET /api/student/class/<class_id>` - Fetch questions for a class
- `GET /api/student/class/<class_id>/<question_id>` - Fetch question details
- `POST /api/student/run/<question_id>` - Test run code
- `POST /api/student/submission/<question_id>` - Final submission

### Instructor Endpoints

- `GET /api/instructor/classes` - Fetch all classes for instructor
- `GET /api/instructor/class/<class_id>` - Fetch questions for a class
- `POST /api/instructor/class/<class_id>/question` - Add new question
- `GET /api/instructor/class/<class_id>/<question_id>` - Get question details
- `POST /api/instructor/evaluate/<question_id>` - Evaluate and close question

## Building for Production

```bash
npm run build
```

The production build will be in the `dist/` directory.

## Preview Production Build

```bash
npm run preview
```
