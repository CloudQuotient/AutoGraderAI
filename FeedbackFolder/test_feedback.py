import os
import boto3
from dotenv import load_dotenv
from feedback import get_code_feedback_from_bedrock

load_dotenv()

feedback = get_code_feedback_from_bedrock("s3://autograder-dummy/submissions/code1.py")

if feedback:
    print("\n✅ Claude Feedback Received:\n")
    print(feedback)
else:
    print("\n❌ No feedback received.")
