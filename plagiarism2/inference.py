import json
import os
import numpy as np
import boto3
from urllib.parse import urlparse
from sklearn.metrics.pairwise import cosine_similarity

# ----------------- Optional: load dotenv only when running locally -----------------
try:
    from dotenv import load_dotenv
    env_path = os.path.join(os.path.dirname(__file__), ".env")
    if os.path.exists(env_path):
        load_dotenv(dotenv_path=env_path)
        print("✅ Loaded environment variables from .env (local mode)")
except ModuleNotFoundError:
    # dotenv not installed in container — ignore silently
    pass

# ----------------- Initialize S3 client -----------------
AWS_ACCESS_KEY = os.getenv("AWS_ACCESS_KEY_ID")
AWS_SECRET_KEY = os.getenv("AWS_SECRET_ACCESS_KEY")
AWS_REGION = os.getenv("AWS_DEFAULT_REGION", "ap-south-1")

if AWS_ACCESS_KEY and AWS_SECRET_KEY:
    # Local mode (explicit credentials)
    s3 = boto3.client(
        "s3",
        aws_access_key_id=AWS_ACCESS_KEY,
        aws_secret_access_key=AWS_SECRET_KEY,
        region_name=AWS_REGION,
    )
    print("✅ Initialized S3 with explicit credentials (local mode)")
else:
    # SageMaker mode (IAM role)
    s3 = boto3.client("s3")
    print("✅ Initialized S3 with IAM role (SageMaker mode)")

# ----------------- Helpers -----------------
def fetch_embedding(url: str) -> np.ndarray:
    """Fetch a precomputed embedding from S3 and return as a numpy array."""
    parsed = urlparse(url)
    bucket, key = parsed.netloc, parsed.path.lstrip("/")
    obj = s3.get_object(Bucket=bucket, Key=key)
    arr = np.frombuffer(obj["Body"].read(), dtype=np.float32)
    return arr


def plagiarism_report(sim_matrix, filenames, threshold):
    """Build structured plagiarism report."""
    results = []
    n = len(filenames)
    for i in range(n):
        for j in range(i + 1, n):
            sim = float(round(sim_matrix[i, j], 3))
            results.append({
                "file1": filenames[i],
                "file2": filenames[j],
                "similarity": sim,
                "plagiarism_flag": int(sim >= threshold)
            })
    return {"results": results}

# ----------------- SageMaker Required Functions -----------------
def model_fn(model_dir):
    """Dummy function — no model file required since we fetch embeddings from S3."""
    return None


def input_fn(request_body, content_type):
    """Parse incoming request JSON."""
    if content_type == "application/json":
        return json.loads(request_body)
    raise ValueError(f"Unsupported content type: {content_type}")


def predict_fn(input_data, _):
    """
    Expected input_data format:
    {
        "s3_embedding_urls": [
            "s3://autograder-dummy/embeddings/code1.py.npy",
            "s3://autograder-dummy/embeddings/code2.py.npy"
        ],
        "filenames": ["code1.py", "code2.py"],     # optional
        "threshold": 0.85,                         # optional, default = 0.85
        "bucket": "autograder-dummy"               # optional (for validation / override)
    }
    """
    # Extract parameters
    emb_urls = input_data.get("s3_embedding_urls", [])
    filenames = input_data.get("filenames", [f"file_{i}" for i in range(len(emb_urls))])
    threshold = float(input_data.get("threshold", 0.85))
    bucket = input_data.get("bucket", None)

    if not emb_urls:
        raise ValueError("No 's3_embedding_urls' provided in input.")

    # Optional: validate all URLs belong to the given bucket (if provided)
    if bucket:
        for url in emb_urls:
            if bucket not in url:
                raise ValueError(f"Embedding URL {url} not found in specified bucket {bucket}")

    # Fetch embeddings from S3
    embeddings = [fetch_embedding(url) for url in emb_urls]
    embeddings = np.stack(embeddings)

    # Normalize embeddings
    norms = np.linalg.norm(embeddings, axis=1, keepdims=True)
    embeddings = embeddings / np.clip(norms, 1e-8, None)

    # Compute cosine similarity
    sim_matrix = cosine_similarity(embeddings)
    np.fill_diagonal(sim_matrix, 1.0)
    sim_matrix = np.clip(sim_matrix, 0, 1)

    # Generate report
    report = plagiarism_report(sim_matrix, filenames, threshold)
    report["threshold"] = threshold
    report["bucket"] = bucket or "auto-detected"

    return report


def output_fn(prediction, accept):
    """Return prediction as JSON."""
    return json.dumps(prediction), "application/json"
