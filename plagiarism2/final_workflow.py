import json
import os
import boto3
from dotenv import load_dotenv
from embeddings import generate_embeddings_from_s3

# ----------------- Load environment -----------------
env_path = os.path.join(os.path.dirname(__file__), ".env")
if os.path.exists(env_path):
    load_dotenv(dotenv_path=env_path)
    print("Loaded environment variables from .env")

# ----------------- Config -----------------
S3_BUCKET = os.getenv("S3_BUCKET", "autograder-dummy")
ENDPOINT_NAME = os.getenv("SAGEMAKER_ENDPOINT_NAME")

if not ENDPOINT_NAME:
    raise ValueError("Missing SAGEMAKER_ENDPOINT_NAME in .env")

# ----------------- Step 1: Input code file URLs -----------------
test_s3_urls = [
    f"s3://{S3_BUCKET}/submissions/code1.py",
    f"s3://{S3_BUCKET}/submissions/code2.py",
    f"s3://{S3_BUCKET}/submissions/code3.py"
]

# ----------------- Step 2: Generate embeddings locally & upload -----------------
print("Generating embeddings and uploading to S3...")
embedding_urls = generate_embeddings_from_s3(test_s3_urls)
print("Embeddings uploaded successfully!")
print("Returned embedding URLs:\n", json.dumps(embedding_urls, indent=2))

# ----------------- Step 3: Prepare payload -----------------
input_payload = {
    "s3_embedding_urls": embedding_urls,
    "filenames": ["code1.py", "code2.py", "code3.py"],
    "bucket": S3_BUCKET,
    "threshold": 0.85
}

payload_json = json.dumps(input_payload)

# ----------------- Step 4: Invoke SageMaker endpoint -----------------
print(f"\n🚀 Invoking SageMaker endpoint: {ENDPOINT_NAME}")

runtime = boto3.client("sagemaker-runtime")

try:
    response = runtime.invoke_endpoint(
        EndpointName=ENDPOINT_NAME,
        ContentType="application/json",
        Body=payload_json
    )

    result = json.loads(response["Body"].read().decode("utf-8"))
    print("\n===== FINAL OUTPUT FROM ENDPOINT =====")
    print(json.dumps(result, indent=2))

except runtime.exceptions.ModelError as e:
    print("ModelError:", e)
except Exception as e:
    print("Unexpected error:", str(e))
