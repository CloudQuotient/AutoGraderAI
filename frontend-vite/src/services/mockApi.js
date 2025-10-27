// Mock API data for frontend-only testing
// To use this, import mockApi instead of API in your components

export const mockStudentClasses = {
  classes: [
    { ClassID: 1, InstructorID: 1, InstructorName: "Dr. Smith" },
    { ClassID: 2, InstructorID: 1, InstructorName: "Dr. Smith" }
  ]
};

export const mockStudentQuestions = {
  questions: [
    { QuestionID: 1, Status: "open" },
    { QuestionID: 2, Status: "closed" },
    { QuestionID: 3, Status: "open" }
  ]
};

export const mockQuestionDetails = {
  QuestionID: 1,
  QuestionText: "Write a function to sort an array using bubble sort algorithm. The function should take a list of integers and return the sorted list.",
  TestCases: [
    { input: "[10, 5, 2, 6]", output: "[2, 5, 6, 10]" },
    { input: "[3, 8, 4, 1, 9]", output: "[1, 3, 4, 8, 9]" }
  ],
  Status: "open"
};

export const mockInstructorClasses = {
  instructor: {
    InstructorID: 1,
    Name: "Dr. Smith",
    Email: "smith@university.edu"
  },
  classes: [
    { ClassID: 1 },
    { ClassID: 2 }
  ]
};

export const mockInstructorQuestions = {
  questions: [
    { QuestionID: 1, Status: "open" },
    { QuestionID: 2, Status: "closed" },
    { QuestionID: 3, Status: "open" }
  ]
};

export const mockQuestionResults = {
  status: "open",
  msg: "Click on Evaluate Button For Results"
};

export const mockQuestionResultsClosed = {
  status: "closed",
  results: {
    plagiarism_report: "No significant plagiarism detected",
    student_performances: [
      { student_id: 1, score: 85, similarity: 0.1 },
      { student_id: 2, score: 90, similarity: 0.05 }
    ]
  }
};
