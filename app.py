from flask import Flask, render_template, request, redirect, url_for, jsonify
from flask_cors import CORS
from flask_jwt_extended import (
    JWTManager,
    create_access_token,
    jwt_required,
    get_jwt,
    get_jwt_identity,
)
from dotenv import load_dotenv
import os
from werkzeug.utils import secure_filename
import requests
import time
from jose import jwk, jwt as jose_jwt
from jose.exceptions import JOSEError
import json
import uuid

# --- Function Imports ---
from S3Handler import CodeUploadS3
from beforeECS.app_ECS import EvaluateECS
from FeedbackFolder.feedback import get_code_feedback_from_bedrock
from plagiarism2.embeddings import generate_embeddings_from_s3

API_URL = "https://something_something/prod/run"    # URL of API Gateway that Connects the Lambda Function

load_dotenv()

# Temporary Folder for Storing Code Locally before Storing in S3
UPLOAD_FOLDER = "uploads"
os.makedirs(UPLOAD_FOLDER, exist_ok=True)

app = Flask(__name__)

CORS(app, resources={r"/api/*": {"origins": "*"}}, supports_credentials=True)

app.config['SQLALCHEMY_DATABASE_URI'] = os.getenv('DATABASE_URL')
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False
app.config['JWT_SECRET_KEY'] = os.getenv('JWT_SECRET_KEY', 'change-this-in-prod')

# Load Cognito config from environment
COGNITO_USER_POOL_ID = os.getenv('COGNITO_USER_POOL_ID')
COGNITO_APP_CLIENT_ID = os.getenv('COGNITO_APP_CLIENT_ID')
COGNITO_REGION = os.getenv('COGNITO_REGION')
COGNITO_ISSUER = f"https://cognito-idp.{COGNITO_REGION}.amazonaws.com/{COGNITO_USER_POOL_ID}"
JWKS_URL = f"{COGNITO_ISSUER}/.well-known/jwks.json"

# Fetch and cache the JWKS (JSON Web Key Set)
try:
    jwks = requests.get(JWKS_URL).json()["keys"]
except requests.exceptions.RequestException as e:
    print(f"Error fetching JWKS: {e}")
    jwks = []

# Import DB Instances and Models from models.py
from models import db, Student, Instructor, Class, Question, Submission

db.init_app(app)

jwt_manager = JWTManager(app)

# ----------------------------- Auth Helpers ------------------------------

def verify_cognito_token(token):
    """
    Verifies a Cognito ID Token.
    Returns the decoded claims if valid, otherwise returns None.
    """
    if not jwks:
        print("JWKS not loaded. Cannot verify token.")
        return None

    try:
        header = jose_jwt.get_unverified_header(token)
        kid = header["kid"]
        key = next((k for k in jwks if k["kid"] == kid), None)
        if not key:
            print("Public key not found in JWKS.")
            return None

        claims = jose_jwt.decode(
            token,
            key,
            algorithms=["RS256"],
            issuer=COGNITO_ISSUER,
            audience=COGNITO_APP_CLIENT_ID 
        )

        if claims.get("token_use") != "id":
            print("Token is not an ID token.")
            return None
        
        if time.time() > claims["exp"]:
            print("Token is expired.")
            return None

        return claims

    except JOSEError as e:
        print(f"Token verification failed: {e}")
        return None
    except Exception as e:
        print(f"An unexpected error occurred: {e}")
        return None

def getRoleID():
    """Extract role and user_id from the JWT claims.

    This function assumes the route is protected with @jwt_required().
    """
    try:
        claims = get_jwt()
        print(f"JWT Claims: {claims}")
        role = claims.get('role')
        user_id = claims.get('user_id')
        print(f"Extracted role: {role}, user_id: {user_id}")
        return role, user_id
    except Exception as e:
        print(f"Error in getRoleID: {e}")
        return None, None

@app.route('/api/login', methods=['POST'])
def login():
    data = request.get_json() or {}
    cognito_id_token = data.get('token')

    if not cognito_id_token:
        return jsonify({"message": "Cognito ID token is required"}), 400

    claims = verify_cognito_token(cognito_id_token)
    
    if not claims:
        return jsonify({"message": "Invalid or expired Cognito token"}), 401

    email = claims.get('email')
    groups = claims.get('cognito:groups', [])
    
    role = None
    if 'Instructor' in groups:
        role = 'instructor'
    elif 'Student' in groups:
        role = 'student'

    if not role or not email:
        return jsonify({"message": "User email or role not found in token"}), 400

    user = None
    if role == 'instructor':
        user = db.session.query(Instructor).filter_by(Email=email).first()
    elif role == 'student':
        user = db.session.query(Student).filter_by(Email=email).first()

    if not user:
        return jsonify({"message": f"User {email} not found in local database."}), 404
        
    user_id = user.InstructorID if role == 'instructor' else user.StudentID

    additional_claims = {
        'role': role,
        'user_id': user_id,
    }
    access_token = create_access_token(identity=str(user_id), additional_claims=additional_claims)
    
    return jsonify({
        'access_token': access_token,  
        'role': role,
        'user_id': user_id,
    }), 200

# ------------------------------ Routes ----------------------------------

# To Check if its working (No other use for actual application --- debugging)
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
@jwt_required()
def StudentClasses():
    role, user_id = getRoleID()
    
    if role == 'student':
        if request.method == "GET":
            student = db.session.query(Student).filter_by(StudentID=user_id).first()
            print(student.StudentID)
            if not student:
                return jsonify({"message": "Student not found"}), 404

            instructor = db.session.query(Instructor).filter_by(InstructorID=student.InstructorID).first()

            print(instructor.InstructorID, instructor.Name)

            if not instructor:
                return jsonify({"message": "Instructor not found for this student"}), 404

            classes = db.session.query(Class).filter_by(InstructorID=instructor.InstructorID).all()

            class_details = [
                {
                    'ClassID': cls.ClassID,
                    'InstructorID': cls.InstructorID,
                    'InstructorName': instructor.Name
                }
                for cls in classes
            ]
            print("Class details:", class_details)
            return jsonify({"classes": class_details})

        else:
            return jsonify({"msg": "Only GET Requests are Allowed"}), 400
    
    else:
        return jsonify({"msg": "Only Student Role Allowed"}), 400

# This function is when the Student clicks on a Particular Class, All the questions (Just the QuestionID and Status) assigned in that Class is displayed
@app.route('/api/student/class/<int:class_id>', methods = ["GET"])
@jwt_required()
def StudentQuestions(class_id):
    role, user_id = getRoleID()

    if role == 'student':
        if request.method == "GET":
            cls = db.session.query(Class).filter_by(ClassID=class_id).first()
            if not cls:
                return jsonify({"message": "Class not found"}), 404

            instructor_id = cls.InstructorID
            if not instructor_id:
                return jsonify({"message": "Instructor not found for this class"}), 404

            questions = db.session.query(Question).filter(Question.InstructorID == instructor_id).all()

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
@jwt_required()
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
@jwt_required()
def StudentQuestionSubmission(question_id):
    role, user_id = getRoleID()

    if role == 'student':
        if request.method == "POST":
            if 'file' not in request.files:
                return jsonify({"message": "No file part in the request"}), 400

            file = request.files['file']

            if file.filename == '':
                return jsonify({"message": "No file selected"}), 400

            filename = secure_filename(file.filename)
            temp_path = os.path.join(UPLOAD_FOLDER, filename)
            file.save(temp_path)

            old_filename = request.form.get('old_filename')
            if old_filename:
                old_path = os.path.join(UPLOAD_FOLDER, old_filename)
                if os.path.exists(old_path):
                    os.remove(old_path)

            try:
                student = db.session.query(Student).filter_by(StudentID=user_id).first()
                if not student:
                    return jsonify({"message": "Invalid student ID"}), 404

                instructor_id = student.InstructorID
                class_obj = db.session.query(Class).filter_by(InstructorID=instructor_id).first()
                if not class_obj:
                    return jsonify({"message": "No class found for this instructor"}), 404

                class_id = class_obj.ClassID

                # autograder-dummy is the bucket that is used to store the submissions
                s3_folder_path = f"s3://autograder-dummy/submissions/class_{class_id}/"
                extension = os.path.splitext(filename)[1] or ".py"
                s3_file_name = f"student_{user_id}_question_{question_id}{extension}"

                s3_path = CodeUploadS3(s3_folder_path, s3_file_name, temp_path)

                existing_submission = db.session.query(Submission).filter_by(
                    StudentID=user_id, QuestionID=question_id
                ).first()

                if existing_submission:
                    return jsonify({"message": "You have already submitted for this question"}), 400
                
                question = db.session.query(Question).filter_by(QuestionID=question_id).first()
                if not question:
                    return jsonify({"message": "Invalid question ID"}), 404

                jsonblob = question.TestCases

                result = EvaluateECS(s3_path, jsonblob)
                print(result)
                score = result or None

                feedback = get_code_feedback_from_bedrock(s3_path)

                new_submission = Submission(
                    StudentID=user_id,
                    QuestionID=question_id,
                    S3FilePath=s3_path,
                    Score=score,
                    Feedback=feedback
                )

                db.session.add(new_submission)
                db.session.commit()

                return jsonify({
                    "message": "Submission uploaded successfully",
                    "S3FilePath": s3_path
                }), 200

            except Exception as e:
                db.session.rollback()
                print("Error during submission upload:", str(e))
                return jsonify({"error": "Failed to upload submission"}), 500
            

        else:
            return jsonify({"msg": "Only POST Requests are Allowed"}), 400
    
    else:
        return jsonify({"msg": "Only Student Role Allowed"}), 400
    
# This route is called when the student clicks on the 'Test Run' button for just running the code
# When route is called, it should consist of the code file along with it in the request body
# This is not considered as the final Submission, and response consists of results of the public test-cases
@app.route('/api/student/run/<int:question_id>', methods = ["POST"])
@jwt_required()
def StudentQuestionRun(question_id):
    role, user_id = getRoleID()

    if role == 'student':
        if request.method == "POST":
            if 'file' not in request.files:
                return jsonify({"message": "No file part in the request"}), 400

            file = request.files['file']

            if file.filename == '':
                return jsonify({"message": "No file selected"}), 400

            filename = secure_filename(file.filename)
            temp_path = os.path.join(UPLOAD_FOLDER, filename)
            file.save(temp_path)
            print(temp_path)

            old_filename = request.form.get('old_filename')
            if old_filename:
                old_path = os.path.join(UPLOAD_FOLDER, old_filename)
                if os.path.exists(old_path):
                    os.remove(old_path)

            try:
                file_ext = os.path.splitext(filename)[1] or ""
                random_name = f"{uuid.uuid4().hex}{file_ext}"

                # Store the 'Run' codes in a temporary directory and later delete (not needed)
                s3_folder_path = f"s3://autograder-dummy/temporary/"
                s3_path = CodeUploadS3(s3_folder_path, random_name, temp_path)

                question = db.session.query(Question).filter_by(QuestionID=question_id).first()
                if not question:
                    return jsonify({"message": "Invalid question ID"}), 404

                jsonblob = question.TestCases

                results = EvaluateECS(s3_path, jsonblob)

                return jsonify({
                    "message": "Code executed successfully (test run)",
                    "Results": results
                }), 200

            except Exception as e:
                print("Error during test run:", str(e))
                return jsonify({"error": "Failed to run code"}), 500
            

        else:
            return jsonify({"msg": "Only POST Requests are Allowed"}), 400
        
    else:
        return jsonify({"msg": "Only Student Role Allowed"}), 400

# This function Returns all the Classes and their details taken by that particular Instructor
@app.route('/api/instructor/classes', methods = ["GET"])
@jwt_required()
def InstructorClasses():
    print("InstructorClasses called")
    role, user_id = getRoleID()
    print(f"Role: {role}, User ID: {user_id}")

    if role == 'instructor':
        if request.method == "GET":
            instructor = db.session.query(Instructor).filter_by(InstructorID=user_id).first()
            if not instructor:
                return jsonify({"message": "Instructor not found"}), 404

            classes = db.session.query(Class).filter_by(InstructorID=user_id).all()

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
@jwt_required()
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
@jwt_required()
def InstructorQuestionSubmission(class_id, question_id):
    role, user_id = getRoleID()

    if role == 'instructor':
        if request.method == "GET":
            question = db.session.query(Question).filter_by(QuestionID=question_id, InstructorID=user_id).first()

            if not question:
                return jsonify({"message": "Question not found or unauthorized access"}), 404

            if question.Status == 'open':
                return jsonify({
                    "status": "open",
                    "msg": "Click on Evaluate Button For Results"
                })

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
@jwt_required()
def InstructorEvaluateQuestion(question_id):
    role, user_id = getRoleID()

    if role != 'instructor':
        return jsonify({"msg": "Only Instructor Role Allowed"}), 400

    try:
        question = db.session.query(Question).filter_by(QuestionID=question_id, InstructorID=user_id).first()
        if not question:
            return jsonify({"message": "Question not found or unauthorized"}), 404

        question.Status = 'closed'
        db.session.commit()

        submissions = db.session.query(Submission).filter_by(QuestionID=question_id).all()
        if not submissions:
            return jsonify({"message": "No submissions found for this question"}), 404

        s3_urls = [sub.S3FilePath for sub in submissions]

        embedding_urls = generate_embeddings_from_s3(s3_urls, "autograder-dummy", "embeddings/")

        filenames = [os.path.basename(sub.S3FilePath) for sub in submissions]

        payload = {
            "s3_embedding_urls": embedding_urls,
            "filenames": filenames,
            "bucket": "autograder-dummy",   # Change bucket name if needed
            "threshold": 0.85
        }

        print("🚀 Sending request to plagiarism detector...")
        response = requests.post(API_URL, json=payload, timeout=120)

        if response.status_code != 200:
            print(f"Lambda call failed: {response.status_code} {response.text}")
            return jsonify({
                "message": "Lambda plagiarism check failed",
                "error": response.text
            }), 500

        try:
            plagiarism_result = response.json()
        except json.JSONDecodeError:
            plagiarism_result = {"raw_response": response.text}

        question.Results = plagiarism_result
        db.session.commit()

        print(f"Results stored for Question {question_id}")

        return jsonify({
            "message": "Question closed and plagiarism evaluation completed",
            "plagiarism_result": plagiarism_result
        }), 200

    except Exception as e:
        db.session.rollback()
        print(f"Error during instructor evaluation: {str(e)}")
        return jsonify({"error": str(e)}), 500

# This function is to be called when the instructor navigates inside a particular Class and clicks on the 'Add New Question' Button
# The New Question has fields to be filled by the Instructor and sent through the request body to this endpoint and assigned
# View Multi-lined comments inside the function to see Example Request and Example Response
@app.route('/api/instructor/class/<int:class_id>/question', methods=["POST"])
@jwt_required()
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
            instructor = db.session.query(Instructor).filter_by(InstructorID=user_id).first()
            if not instructor:
                return jsonify({"message": "Instructor not found"}), 404

            cls = db.session.query(Class).filter_by(ClassID=class_id, InstructorID=user_id).first()
            if not cls:
                return jsonify({"message": "Class not found or unauthorized access"}), 404

            data = request.get_json()
            if not data or not data.get('QuestionText') or not data.get('TestCases'):
                return jsonify({"message": "Missing required fields (QuestionText, TestCases)"}), 400

            new_question = Question(
                InstructorID=user_id,  # Instructing instructor
                QuestionText=data['QuestionText'],  # The question text provided
                TestCases=data['TestCases'],  # Test cases for the question
                Status='open'  # Default status is open
            )

            db.session.add(new_question)
            db.session.commit()

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
    with app.app_context():
        db.create_all()
    app.run(host="0.0.0.0", port=5000, debug=True, use_reloader = False)
