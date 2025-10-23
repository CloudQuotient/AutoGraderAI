from flask import Flask, render_template, request, redirect, url_for, flash
from flask_sqlalchemy import SQLAlchemy
from models import db
import os
from dotenv import load_dotenv
from S3Handler import CodeUpload  # import your upload function

load_dotenv()

app = Flask(__name__)
app.secret_key = "supersecretkey"  # needed for flash messages

# Database connection
app.config['SQLALCHEMY_DATABASE_URI'] = os.getenv('DATABASE_URL')
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False

# File upload config
UPLOAD_FOLDER = "uploads"
os.makedirs(UPLOAD_FOLDER, exist_ok=True)
app.config["UPLOAD_FOLDER"] = UPLOAD_FOLDER

db.init_app(app)

@app.route('/')
def home():
    return "AutoGrader.AI Backend is running!"

@app.route('/upload', methods=['GET', 'POST'])
def upload_file():
    if request.method == 'POST':
        if 'file' not in request.files:
            flash('No file part')
            return redirect(request.url)

        file = request.files['file']
        if file.filename == '':
            flash('No selected file')
            return redirect(request.url)

        if file:
            # Save temporarily
            local_path = os.path.join(app.config['UPLOAD_FOLDER'], file.filename)
            file.save(local_path)

            # Call CodeUpload
            # Change the file name according to the format student_<student_id>_question_<question_id>.<code_extension>
            # Also change the folder path to consist of /class_<class_id>
            s3_folder_path = "s3://autograder-ai/submissions/class_<class_id>/student_<student_id>_question_<question_id>.<code_extension>/"
            s3_file_name = file.filename
            s3_url = CodeUpload(s3_folder_path, s3_file_name, local_path)

            if s3_url:
                flash(f"File uploaded successfully! S3 URL: {s3_url}")
            else:
                flash("Failed to upload file to S3.")
            return redirect(url_for('upload_file'))
        
    elif request.method == 'GET':
        return render_template('upload.html')
    
    else:
        return render_template('error.html')

if __name__ == '__main__':
    with app.app_context():
        db.create_all()
    app.run(debug=True)
