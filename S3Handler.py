import boto3
import os
from urllib.parse import urlparse
from dotenv import load_dotenv

# Load environment variables from .env
load_dotenv()

def CodeUpload(S3FolderPath: str, S3FileName: str, CodeFilePath: str):
    """
    Uploads a local code file to the given S3 folder path.

    Args:
        S3FolderPath (str): Full S3 folder path (e.g., 'S3FolderPath="s3://autograder-ai/submissions/class_1/').
        S3FileName (str): File name to be saved as in S3 (e.g., 'student_1_question_1.py').
        CodeFilePath (str): Local path to the temporary code file.

    Returns:
        str: Full S3 URL of the uploaded file.

    Example Usage:
    CodeUpload(
        S3FolderPath="s3://autograder-ai/submissions/class_1/",
        S3FileName="student_1_question_1.py",
        CodeFilePath="/tmp/student_1_question_1.py"
    )
    """
    try:
        # Parse bucket name and prefix from S3FolderPath
        parsed = urlparse(S3FolderPath)
        bucket_name = parsed.netloc
        prefix = parsed.path.lstrip('/')
        if prefix and not prefix.endswith('/'):
            prefix += '/'
        
        s3_key = f"{prefix}{S3FileName}"

        # Initialize S3 client using credentials from .env
        s3 = boto3.client(
            's3',
            aws_access_key_id=os.getenv('AWS_ACCESS_KEY_ID'),
            aws_secret_access_key=os.getenv('AWS_SECRET_ACCESS_KEY'),
            region_name=os.getenv('AWS_REGION')
        )

        # Upload file
        s3.upload_file(CodeFilePath, bucket_name, s3_key)

        file_url = f"https://{bucket_name}.s3.{os.getenv('AWS_REGION')}.amazonaws.com/{s3_key}"
        print(f"✅ Uploaded successfully to: {file_url}")
        return file_url

    except Exception as e:
        print(f"❌ Error uploading file: {e}")
        return None

