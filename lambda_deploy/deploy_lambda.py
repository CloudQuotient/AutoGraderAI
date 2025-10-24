import boto3
import json
import os
import time
import zipfile
from dotenv import load_dotenv

# -----------------------------
# Load environment variables
# -----------------------------
env_path = os.path.join(os.path.dirname(__file__), ".env")
load_dotenv(dotenv_path=env_path)

# -----------------------------
# CONFIG (change these values)
# -----------------------------
LAMBDA_NAME = "plagiarism-lambda"
ROLE_NAME = "lambda-sagemaker-role"
POLICY_NAME = "lambda-sagemaker-policy"
ZIP_FILE = "function.zip"
HANDLER = "lambda_function.lambda_handler"
RUNTIME = "python3.9"

REGION = os.getenv("AWS_DEFAULT_REGION")
SAGEMAKER_ENDPOINT = os.getenv("SAGEMAKER_ENDPOINT_NAME")
S3_BUCKET = os.getenv("S3_BUCKET")

# Retrieve AWS credentials and region from environment
aws_access_key_id = os.getenv("AWS_ACCESS_KEY_ID")
aws_secret_access_key = os.getenv("AWS_SECRET_ACCESS_KEY")
region_name = os.getenv("AWS_DEFAULT_REGION")

# Check all required vars exist
if not all([aws_access_key_id, aws_secret_access_key, region_name, SAGEMAKER_ENDPOINT, S3_BUCKET]):
    raise ValueError("❌ Missing one or more required environment variables. Check your .env file.")

# Create the session using environment variables
session = boto3.Session(
    aws_access_key_id=aws_access_key_id,
    aws_secret_access_key=aws_secret_access_key,
    region_name=region_name
)

# Initialize clients
iam = session.client("iam")
lambda_client = session.client("lambda")
sts_client = session.client("sts")

ACCOUNT_ID = sts_client.get_caller_identity()["Account"]

# -----------------------------------
# Helper: create zip for lambda code
# -----------------------------------
def create_zip():
    print("📦 Zipping lambda_function.py ...")
    with zipfile.ZipFile(ZIP_FILE, "w", zipfile.ZIP_DEFLATED) as zf:
        zf.write("lambda_function.py")
    print("✅ Created", ZIP_FILE)


# ------------------------------------------------
# Helper: create IAM role + inline policy for Lambda
# ------------------------------------------------
def create_iam_role():
    trust_policy = {
        "Version": "2012-10-17",
        "Statement": [
            {
                "Effect": "Allow",
                "Principal": {"Service": "lambda.amazonaws.com"},
                "Action": "sts:AssumeRole"
            }
        ]
    }

    try:
        print("🧩 Creating IAM role...")
        role = iam.create_role(
            RoleName=ROLE_NAME,
            AssumeRolePolicyDocument=json.dumps(trust_policy)
        )
        print("✅ Role created:", role["Role"]["Arn"])
    except iam.exceptions.EntityAlreadyExistsException:
        print("ℹ️ Role already exists.")
        role = iam.get_role(RoleName=ROLE_NAME)

    # Build permissions policy
    permissions = {
        "Version": "2012-10-17",
        "Statement": [
            {
                "Effect": "Allow",
                "Action": ["sagemaker:InvokeEndpoint"],
                "Resource": f"arn:aws:sagemaker:{REGION}:{ACCOUNT_ID}:endpoint/{SAGEMAKER_ENDPOINT}"
            },
            {
                "Effect": "Allow",
                "Action": ["s3:GetObject", "s3:ListBucket"],
                "Resource": [
                    f"arn:aws:s3:::{S3_BUCKET}",
                    f"arn:aws:s3:::{S3_BUCKET}/*"
                ]
            },
            {
                "Effect": "Allow",
                "Action": [
                    "logs:CreateLogGroup",
                    "logs:CreateLogStream",
                    "logs:PutLogEvents"
                ],
                "Resource": "*"
            }
        ]
    }

    iam.put_role_policy(
        RoleName=ROLE_NAME,
        PolicyName=POLICY_NAME,
        PolicyDocument=json.dumps(permissions)
    )
    print("✅ Attached inline policy.")

    print("⏳ Waiting for IAM role to be usable...")
    time.sleep(10)
    return role["Role"]["Arn"]


# -----------------------------------
# Helper: create or update Lambda
# -----------------------------------
def deploy_lambda(role_arn):
    with open(ZIP_FILE, "rb") as f:
        zip_bytes = f.read()

    try:
        print("🚀 Creating Lambda function...")
        resp = lambda_client.create_function(
            FunctionName=LAMBDA_NAME,
            Runtime=RUNTIME,
            Role=role_arn,
            Handler=HANDLER,
            Code={"ZipFile": zip_bytes},
            Timeout=60,
            Environment={
                "Variables": {"SAGEMAKER_ENDPOINT": SAGEMAKER_ENDPOINT}
            }
        )
        print("✅ Created Lambda:", resp["FunctionArn"])

    except lambda_client.exceptions.ResourceConflictException:
        print("ℹ️ Lambda already exists, updating code...")
        resp = lambda_client.update_function_code(
            FunctionName=LAMBDA_NAME,
            ZipFile=zip_bytes
        )
        print("✅ Updated Lambda code.")


# -----------------------------------
# Optional: Test Lambda invocation
# -----------------------------------
def test_lambda():
    print("🧪 Testing Lambda invocation...")

    # Correct payload for your Lambda
    test_event = {
        "s3_embedding_urls": [
            "s3://autograder-dummy/embeddings/code1.py.npy",
            "s3://autograder-dummy/embeddings/code2.py.npy",
            "s3://autograder-dummy/embeddings/code3.py.npy"
        ],
        "filenames": ["code1.py", "code2.py", "code3.py"],
        "bucket": "autograder-dummy",
        "threshold": 0.85
    }

    # Invoke Lambda
    response = lambda_client.invoke(
        FunctionName=LAMBDA_NAME,
        Payload=json.dumps(test_event)
    )

    # Read and decode response
    result = response["Payload"].read().decode("utf-8")
    response_dict = json.loads(result)  # result is what you got from Lambda
    body_dict = json.loads(response_dict["body"])

    print("Response: ", json.dumps(body_dict, indent=2))


# -----------------------------------
# MAIN
# -----------------------------------
if __name__ == "__main__":
    # Uncomment for deploying for the first time
    # create_zip()
    # role_arn = create_iam_role()
    # deploy_lambda(role_arn)
    test_lambda()

    print("\n✅ Deployment complete!")
    print(f"Lambda Function: {LAMBDA_NAME}")
    print(f"IAM Role: {ROLE_NAME}")
    print(f"SageMaker Endpoint: {SAGEMAKER_ENDPOINT}")
    print(f"S3 Bucket: {S3_BUCKET}")
