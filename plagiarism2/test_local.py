import json
from embeddings import generate_embeddings_from_s3
from inference import model_fn, predict_fn
import os
from dotenv import load_dotenv

env_path = os.path.join(os.path.dirname(__file__), ".env")
load_dotenv(dotenv_path=env_path)

# -----------------------------------------------------
# ✅ Step 1: Input code file URLs
# -----------------------------------------------------
test_s3_urls = [
        "s3://autograder-dummy/submissions/code1.py",
        "s3://autograder-dummy/submissions/code2.py",
        "s3://autograder-dummy/submissions/code3.py"
    ]

# -----------------------------------------------------
# ✅ Step 2: Generate embeddings locally and upload to S3
# -----------------------------------------------------
print("🔄 Generating embeddings and uploading to S3...")
embedding_urls = generate_embeddings_from_s3(test_s3_urls)
print("✅ Embeddings uploaded successfully!")
print("Returned embedding URLs:\n", json.dumps(embedding_urls, indent=2))

S3_BUCKET = os.getenv("S3_BUCKET")

# -----------------------------------------------------
# ✅ Step 3: Prepare input for inference
# -----------------------------------------------------
input_payload = {
    "s3_embedding_urls": embedding_urls,
    "filenames": ["code1.py", "code2.py", "code3.py"],
    "bucket": S3_BUCKET,     # params now passed dynamically
    "threshold": 0.85
}

# -----------------------------------------------------
# ✅ Step 4: Run inference locally
# -----------------------------------------------------
print("\n🚀 Running local inference using inference.py...")
model = model_fn(None)
output = predict_fn(input_payload, model)

# -----------------------------------------------------
# ✅ Step 5: Print results
# -----------------------------------------------------
print("\n===== FINAL OUTPUT =====")
print(json.dumps(output, indent=2))
