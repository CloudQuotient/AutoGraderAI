import os
import tarfile
import shutil
from dotenv import load_dotenv
import boto3
import sagemaker
from sagemaker.sklearn.model import SKLearnModel  # ✅ Use SKLearnModel (not generic Model)

# ----------------- Load environment -----------------
env_path = os.path.join(os.path.dirname(__file__), ".env")
load_dotenv(dotenv_path=env_path)

AWS_REGION = os.getenv("AWS_DEFAULT_REGION", "ap-south-1")
S3_BUCKET = os.getenv("S3_BUCKET", "autograder-dummy")
SAGEMAKER_ROLE = os.getenv("SAGEMAKER_ROLE_ARN")  # must exist

# ----------------- Create SageMaker session -----------------
session = sagemaker.Session(boto3.Session(region_name=AWS_REGION))

# ----------------- Model packaging -----------------
MODEL_NAME = "plagiarism-detector"
MODEL_DIR = "model"
MODEL_ARTIFACT = f"s3://{S3_BUCKET}/models/{MODEL_NAME}.tar.gz"

# Create model directory
os.makedirs(MODEL_DIR, exist_ok=True)

# Copy inference.py and requirements.txt into model directory
shutil.copy("inference.py", os.path.join(MODEL_DIR, "inference.py"))
shutil.copy("requirements.txt", os.path.join(MODEL_DIR, "requirements.txt"))

# Create tar.gz for SageMaker model
with tarfile.open("model.tar.gz", mode="w:gz") as tar:
    tar.add(MODEL_DIR, arcname=".")

# Upload model artifact to S3
boto3.client("s3", region_name=AWS_REGION).upload_file(
    "model.tar.gz", S3_BUCKET, f"models/{MODEL_NAME}.tar.gz"
)
print(f"✅ Model artifact uploaded to {MODEL_ARTIFACT}")

# ----------------- Create SageMaker Model -----------------
# ✅ Use SKLearnModel (it auto-handles serving + entry point)
model = SKLearnModel(
    model_data=MODEL_ARTIFACT,
    role=SAGEMAKER_ROLE,
    entry_point="inference.py",   # ✅ explicitly specify your inference script
    framework_version="1.2-1",    # must match image version
    sagemaker_session=session,
    env={
        "S3_BUCKET": S3_BUCKET,
        "THRESHOLD": "0.85"
    }
)

# ----------------- Deploy Endpoint (Regular Instance) -----------------
endpoint_name = "plagiarism-detector"
print("🚀 Deploying endpoint using ml.m5.large instance...")

predictor = model.deploy(
    initial_instance_count=1,
    instance_type="ml.m5.large",  # stable for medium/large models
    endpoint_name=endpoint_name
)

print(f"✅ Deployment complete! Endpoint name: {endpoint_name}")
