from flask import Flask, render_template, request, redirect, url_for, jsonify
from flask_cors import CORS  # Import CORS
from dotenv import load_dotenv
import os
from werkzeug.utils import secure_filename

load_dotenv()

UPLOAD_FOLDER = "temp_uploads"
os.makedirs(UPLOAD_FOLDER, exist_ok=True)

# Initialize the Flask application
app = Flask(__name__)

# Enable CORS for all routes (you can customize it if needed)
CORS(app)  # This will allow all domains to access your API, you can limit it later if needed

# Configure the app (e.g., database URI)
app.config['SQLALCHEMY_DATABASE_URI'] = os.getenv('DATABASE_URL')
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False  # Disable modification tracking

# Initialize the database
# Import the `db` instance and models from models.py
from models import db, Student, Instructor, Class, Question, Submission

# Register the app with the SQLAlchemy instance
db.init_app(app)

# ----------------------------- Placeholder ------------------------------

# Change this Function with the Extraction of Role and User ID from the JWT Token
def getRoleID():
    switch = 0

    if switch:
        role = "instructor"
        user_id = 1
    
    else:
        role = "student"
        user_id = 1

    return role, user_id

# ------------------------------ Routes ----------------------------------

@app.route('/', methods = ["GET", "POST"])
def index():
    if request.method == "GET":
        return render_template("upload.html"), 200

    elif request.method == "POST":
        return render_template("error.html"), 404
    
    else:
        return jsonify({"msg": "???"}), 404
    
# This function is for Displaying all the Current Classes enrolled by the Student 
@app.route('/api/student/classes', methods = ["GET"])
def StudentClasses():
    role, user_id = getRoleID()
    
    if role == 'student':
        if request.method == "GET":
            # Step 1: Find the student by their StudentID
            student = db.session.query(Student).filter_by(StudentID=user_id).first()
            print(student.StudentID)
            if not student:
                return jsonify({"message": "Student not found"}), 404

            # Step 2: Find the instructor associated with the student
            instructor = db.session.query(Instructor).filter_by(InstructorID=student.InstructorID).first()

            print(instructor.InstructorID, instructor.Name)

            if not instructor:
                return jsonify({"message": "Instructor not found for this student"}), 404

            # Step 3: Find all classes taught by this instructor
            classes = db.session.query(Class).filter_by(InstructorID=instructor.InstructorID).all()

            # Step 4: Prepare the class data
            class_details = [
                {
                    'ClassID': cls.ClassID,
                    'InstructorID': cls.InstructorID,
                    'InstructorName': instructor.Name
                }
                for cls in classes
            ]
            
            return jsonify({"classes": class_details})

        else:
            return jsonify({"msg": "Only GET Requests are Allowed"}), 400
    
    else:
        return jsonify({"msg": "Only Student Role Allowed"}), 400

# This function is when the Student clicks on a Particular Class, All the questions (Just the QuestionID and Status) assigned in that Class is displayed
@app.route('/api/student/class/<int:class_id>', methods = ["GET"])
def StudentQuestions(class_id):
    role, user_id = getRoleID()

    if role == 'student':
        if request.method == "GET":
            # Step 1: Get the class by class_id
            cls = db.session.query(Class).filter_by(ClassID=class_id).first()
            if not cls:
                return jsonify({"message": "Class not found"}), 404

            # Step 2: Get the instructor_id from the class
            instructor_id = cls.InstructorID
            if not instructor_id:
                return jsonify({"message": "Instructor not found for this class"}), 404

            # Step 3: Get all questions for this instructor
            questions = db.session.query(Question).filter(Question.InstructorID == instructor_id).all()

            # Step 4: Serialize the questions into a list of dicts
            question_list = [
                {
                    "QuestionID": q.QuestionID,
                    "Status": q.Status
                }
                for q in questions
            ]

            return jsonify({"questions": question_list})
        
        else:
            return jsonify({"msg": "Only GET Requests are Allowed"}), 400
        
    else:
        return jsonify({"msg": "Only Student Role Allowed"}), 400
    
# This function is when the Student clicks on a Particular Question of a Class
# If the question is 'closed', then the evaluated results are returned and displayed
# If the question is 'open' and the student hasn't attempted it, The Question details and upload button is displayed
# If the question is 'open' and the student has attempted it, The student will receive a message to wait for the results (no upload button should be shown)
@app.route('/api/student/class/<int:class_id>/<int:question_id>', methods = ["GET"])
def StudentQuestionAttempt(class_id, question_id):
    role, user_id = getRoleID()

    if role == 'student':
        if request.method == "GET":
            question = db.session.query(Question).filter_by(QuestionID = question_id).first()

            question_info = {
                "QuestionID": question_id,
                "QuestionText": question.QuestionText,
                "TestCases": question.TestCases,
                "Status": question.Status
            }

            submission = db.session.query(Submission).filter_by(
                QuestionID=question_id,
                StudentID=user_id
            ).first()

            if question.Status == 'closed':
                if submission:
                    question_info["Submission"] = {
                        "Score": submission.Score,
                        "Feedback": submission.Feedback
                    }
                else:
                    question_info["Submission"] = {
                        "Score": None,
                        "Feedback": "No submission found"
                    }

            elif question.Status == 'open':
                if submission:
                    question_info["message"] = "Already submitted. Please wait for results."

            return jsonify(question_info), 200

        else:
            return jsonify({"msg": "Only GET Requests are Allowed"}), 400
    
    else:
        return jsonify({"msg": "Only Student Role Allowed"}), 400

# This route is called when the Student clicks on the 'Submit' button after uploading his code
# When route is called, it should consist of the code file along with it in the request body
# The Question closes and the student cannot attempt it again (Prolly route to the Previous Page to allow changes to take place after a response is generated from this route call)  
@app.route('/api/student/submission/<int:question_id>', methods=["POST"])
def StudentQuestionSubmission(question_id):
    role, user_id = getRoleID()

    if role == 'student':
        if request.method == "POST":
            # Step 1: Check if a file is part of the request
            if 'file' not in request.files:
                return jsonify({"message": "No file part in the request"}), 400

            file = request.files['file']

            # Step 2: Validate the file
            if file.filename == '':
                return jsonify({"message": "No file selected"}), 400

            # Step 3: Save the file temporarily
            filename = secure_filename(file.filename)
            temp_path = os.path.join(UPLOAD_FOLDER, filename)
            file.save(temp_path)

            try:
                # Step 4: Upload to S3 using your helper function
                # s3_path = CodeUploadS3(temp_path)
                s3_path = "s3://autograder-dummy/code.py" # Hard-coded path, to be changed later on

                # Step 5: Check if the student already has a submission for this question
                existing_submission = db.session.query(Submission).filter_by(
                    StudentID=user_id, QuestionID=question_id
                ).first()

                if existing_submission:
                    return jsonify({"message": "You have already submitted for this question"}), 400

                # Step 6: Create a new Submission entry
                new_submission = Submission(
                    StudentID=user_id,
                    QuestionID=question_id,
                    S3FilePath=s3_path,
                    Score=None,
                    Feedback=None
                )

                db.session.add(new_submission)
                db.session.commit()

                return jsonify({
                    "message": "Submission uploaded successfully",
                    "S3FilePath": s3_path
                }), 200

                #add the route to call the ECS to evaluate the code and bedrock to give feedback and update the submission in the database

            except Exception as e:
                db.session.rollback()
                print("Error during submission upload:", str(e))
                return jsonify({"error": "Failed to upload submission"}), 500

            finally:
                # Step 7: Always clean up local temp file, even if something failed
                if os.path.exists(temp_path):
                    try:
                        os.remove(temp_path)
                    except Exception as cleanup_error:
                        print("Warning: Failed to delete temp file:", cleanup_error)
            

        else:
            return jsonify({"msg": "Only POST Requests are Allowed"}), 400
    
    else:
        return jsonify({"msg": "Only Student Role Allowed"}), 400
    
# This route is called when the student clicks on the 'Test Run' button for just running the code
# When route is called, it should consist of the code file along with it in the request body
# This is not considered as the final Submission, and response consists of results of the public test-cases
@app.route('/api/student/run/<int:question_id>', methods = ["POST"])
def StudentQuestionRun(question_id):
    role, user_id = getRoleID

    if role == 'student':
        if request.method == "POST":
            # Step 1: Ensure file exists in request
            if 'file' not in request.files:
                return jsonify({"message": "No file part in the request"}), 400

            file = request.files['file']

            # Step 2: Validate the file
            if file.filename == '':
                return jsonify({"message": "No file selected"}), 400

            # Step 3: Save file temporarily
            filename = secure_filename(file.filename)
            temp_path = os.path.join(UPLOAD_FOLDER, filename)
            file.save(temp_path)

            try:
                # Step 4: Upload to S3 (temporary)
                # s3_path = CodeUploadS3(temp_path)
                s3_path = "s3://autograder-dummy/code.py" # Hard-coded, change later

                # Step 5: Call EvaluateECS to run code (not final submission)
                # results = EvaluateECS(s3_path)
                results = {} # Hard-coded, change later

                # Step 6: Return the run results to student
                return jsonify({
                    "message": "Code executed successfully (test run)",
                    "Results": results
                }), 200

            except Exception as e:
                print("Error during test run:", str(e))
                return jsonify({"error": "Failed to run code"}), 500

            finally:
                # Step 7: Always delete local file after use
                if os.path.exists(temp_path):
                    try:
                        os.remove(temp_path)
                    except Exception as cleanup_error:
                        print("Warning: Failed to delete temp run file:", cleanup_error)
            
        else:
            return jsonify({"msg": "Only POST Requests are Allowed"}), 400
        
    else:
        return jsonify({"msg": "Only Student Role Allowed"}), 400

# This function Returns all the Classes and their details taken by that particular Instructor
@app.route('/api/instructor/classes', methods = ["GET"])
def InstructorClasses():
    role, user_id = getRoleID()

    if role == 'instructor':
        if request.method == "GET":
            # Step 1: Query the instructor table
            instructor = db.session.query(Instructor).filter_by(InstructorID=user_id).first()
            if not instructor:
                return jsonify({"message": "Instructor not found"}), 404

            # Step 2: Query the class table for classes taught by this instructor
            classes = db.session.query(Class).filter_by(InstructorID=user_id).all()

            # Step 3: Prepare response
            instructor_info = {
                "InstructorID": instructor.InstructorID,
                "Name": instructor.Name,
                "Email": instructor.Email
            }

            class_list = [
                {
                    "ClassID": cls.ClassID
                }
                for cls in classes
            ]

            return jsonify({
                "instructor": instructor_info,
                "classes": class_list
            })

        else:
            return jsonify({"msg": "Only GET Requests are Allowed"}), 400
    
    else:
        return jsonify({"msg": "Only Instructor Role Allowed"}), 400
    
# This function returns all the questions (QuestionID, Status) assigned by the instructor for a particular Class
@app.route('/api/instructor/class/<int:class_id>', methods = ["GET"])
def InstructorQuestions(class_id):
    role, user_id = getRoleID()

    if role == 'instructor':
        if request.method == "GET":
            questions = db.session.query(Question).filter_by(InstructorID = user_id).all()
            if not questions:
                return jsonify({"msg": "No Questions Found"}), 404
            
            question_list = [
                {
                    "QuestionID": q.QuestionID,
                    "Status": q.Status
                }
                for q in questions
            ]
            
            return jsonify({"questions": question_list}), 200

        else:
            return jsonify({"msg": "Only GET Requests are Allowed"}), 400
    
    else:
        return jsonify({"msg": "Only Instructor Role Allowed"}), 400

# This function returns the results of a particular Question
# If the question is 'open', then the Instructor will be shown an 'Evaluate' button to evaluate all submissions
# If the question is 'closed', then display the plagiarism results
@app.route('/api/instructor/class/<int:class_id>/<int:question_id>', methods = ["GET"])
def InstructorQuestionSubmission(class_id, question_id):
    role, user_id = getRoleID()

    if role == 'instructor':
        if request.method == "GET":
            # Fetch the question where QuestionID matches
            question = db.session.query(Question).filter_by(QuestionID=question_id, InstructorID=user_id).first()

            if not question:
                return jsonify({"message": "Question not found or unauthorized access"}), 404

            # Check the status
            if question.Status == 'open':
                return jsonify({
                    "status": "open",
                    "msg": "Click on Evaluate Button For Results"
                })

            # If status is closed, return the Results field
            return jsonify({
                "status": "closed",
                "results": question.Results
            })

        else:
            return jsonify({"msg": "Only GET Requests are Allowed"}), 400
    
    else:
        return jsonify({"msg": "Only Instructor Role Allowed"}), 400

# This route is to be called when the 'Evaluate' button is clicked by the Instructor to Run the Feedback Generator and Plagiarism Detector
# Until a response is returned, display 'Question is being Evaluated...'
@app.route('/api/instructor/evaluate/<int:question_id>', methods = ["POST"])
def InstructorEvaluateQuestion(question_id):
    role, user_id = getRoleID()

    if role == 'instructor':
        if request.method == "POST":
            # Step 1: Find the question by QuestionID
            question = db.session.query(Question).filter_by(QuestionID=question_id, InstructorID=user_id).first()
            if not question:
                return jsonify({"message": "Question not found or you are not the instructor of this question"}), 404

            # Step 2: Update the status of the question to 'closed'
            question.Status = 'closed'
            db.session.commit()

            # Step 3: Get all submissions related to this question
            submissions = db.session.query(Submission).filter_by(QuestionID=question_id).all()

            # Step 4: Call EvaluateECS and FeedbackBedrock for each submission
            for submission in submissions:
                # Call the function to evaluate the submission
                # EvaluateECS(submission)  # Evaluate and then save the results in DB

                # Call the function to give feedback for the submission
                # FeedbackBedrock(submission)  # Get Feedbacm and then save the results in DB

                pass

            return jsonify({"message": "Question closed and evaluations processed for all submissions"}), 200

        else:
            return jsonify({"msg": "Only POST Requests are Allowed"}), 400
        
    else:
        return jsonify({"msg": "Only Instructor Role Allowed"}), 400

# This function is to be called when the instructor navigates inside a particular Class and clicks on the 'Add New Question' Button
# The New Question has fields to be filled by the Instructor and sent through the request body to this endpoint and assigned
# View Multi-lined comments inside the function to see Example Request and Example Response
@app.route('/api/instructor/class/<int:class_id>/question', methods=["POST"])
def InstructorAddQuestion(class_id):
    role, user_id = getRoleID()

    '''Example Request (JSON body):
{
  "QuestionText": "Write the Code for QuickSort, OK?",
  "TestCases": [
    {"input": "10, 5, 2, 6", "output": "2, 5, 6, 10"},
    {"input": "3, 8, 4, 1, 9", "output": "1, 3, 4, 8, 9"}
  ]
}

Example Response:
{
  "message": "Question added successfully",
  "QuestionID": 101,
  "QuestionText": "Write the Code for QuickSort, OK?",
  "TestCases": [
    {"input": "10, 5, 2, 6", "output": "2, 5, 6, 10"},
    {"input": "3, 8, 4, 1, 9", "output": "1, 3, 4, 8, 9"}
  ],
  "Status": "open"
}'''

    if role == 'instructor':
        if request.method == "POST":
            # Step 1: Get the instructor associated with the user_id
            instructor = db.session.query(Instructor).filter_by(InstructorID=user_id).first()
            if not instructor:
                return jsonify({"message": "Instructor not found"}), 404

            # Step 2: Check if the class exists and is taught by the instructor
            cls = db.session.query(Class).filter_by(ClassID=class_id, InstructorID=user_id).first()
            if not cls:
                return jsonify({"message": "Class not found or unauthorized access"}), 404

            # Step 3: Get the data from the request body
            data = request.get_json()
            if not data or not data.get('QuestionText') or not data.get('TestCases'):
                return jsonify({"message": "Missing required fields (QuestionText, TestCases)"}), 400

            # Step 4: Create a new Question instance
            new_question = Question(
                InstructorID=user_id,  # Instructing instructor
                QuestionText=data['QuestionText'],  # The question text provided
                TestCases=data['TestCases'],  # Test cases for the question
                Status='open'  # Default status is open
            )

            # Step 5: Add the question to the database
            db.session.add(new_question)
            db.session.commit()

            # Step 6: Return a success message with the created question's ID
            return jsonify({
                "message": "Question added successfully",
                "QuestionID": new_question.QuestionID,
                "QuestionText": new_question.QuestionText,
                "TestCases": new_question.TestCases,
                "Status": new_question.Status
            }), 201

        else:
            return jsonify({"msg": "Only POST Requests are Allowed"}), 400
    
    else:
        return jsonify({"msg": "Only Instructor Role Allowed"}), 400

# Error handling route for 404
@app.errorhandler(404)
def page_not_found(e):
    return render_template('error.html'), 404

# Run the app
if __name__ == '__main__':
    # Create database tables if they don't exist (development convenience)
    with app.app_context():
        db.create_all()
    app.run(debug=True)
