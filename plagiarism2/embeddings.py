import os
import re
import json
import torch
import boto3
import numpy as np
from urllib.parse import urlparse
from transformers import AutoTokenizer, AutoModel
from dotenv import load_dotenv

def generate_embeddings_from_s3(s3_urls, s3_bucket=None, s3_emb_folder="embeddings/"):
    """
    Given a list of S3 URLs pointing to code files, computes GraphCodeBERT embeddings
    locally and uploads the embeddings to S3.

    Returns a list of S3 URLs pointing to the embeddings.
    """
    # ----------------- Load environment variables from local .env -----------------
    env_path = os.path.join(os.path.dirname(__file__), ".env")
    load_dotenv(dotenv_path=env_path)

    AWS_ACCESS_KEY_ID = os.getenv("AWS_ACCESS_KEY_ID")
    AWS_SECRET_ACCESS_KEY = os.getenv("AWS_SECRET_ACCESS_KEY")
    AWS_DEFAULT_REGION = os.getenv("AWS_DEFAULT_REGION", "ap-south-1")
    S3_BUCKET = s3_bucket or os.getenv("S3_BUCKET")
    if not S3_BUCKET:
        raise ValueError("S3 bucket not specified. Pass it as argument or set S3_BUCKET in .env")

    # ----------------- Initialize S3 client -----------------
    s3 = boto3.client(
        "s3",
        aws_access_key_id=AWS_ACCESS_KEY_ID,
        aws_secret_access_key=AWS_SECRET_ACCESS_KEY,
        region_name=AWS_DEFAULT_REGION
    )

    # ----------------- Load GraphCodeBERT -----------------
    MODEL_NAME = "microsoft/graphcodebert-base"
    DEVICE = torch.device("cuda" if torch.cuda.is_available() else "cpu")
    tokenizer = AutoTokenizer.from_pretrained(MODEL_NAME)
    model = AutoModel.from_pretrained(MODEL_NAME).to(DEVICE)
    model.eval()

    # ----------------- Helper functions -----------------
    def normalize_code(code: str) -> str:
        code = re.sub(r'//.*|#.*', '', code)
        code = re.sub(r'/\*[\s\S]*?\*/', '', code)
        code = re.sub(r'""".*?"""', '', code, flags=re.DOTALL)
        code = re.sub(r"'''.*?'''", '', code, flags=re.DOTALL)
        code = re.sub(r'^\s*(import|from)\s+[\w\.\*]+\s*', '', code, flags=re.MULTILINE)
        code = re.sub(r'^\s*#include\s+[<\w\.\s>]+\s*', '', code, flags=re.MULTILINE)
        code = re.sub(r'\s+', ' ', code)
        return code.strip()

    def infer_language(filename):
        if filename.endswith('.py'):
            return "python"
        elif filename.endswith('.java'):
            return "java"
        elif filename.endswith(('.cpp', '.c')):
            return "c_cpp"
        elif filename.endswith('.js'):
            return "javascript"
        return "code"

    def get_embedding(code: str, lang_tag: str):
        normalized = normalize_code(code)
        text = f"<{lang_tag}> {normalized}"
        inputs = tokenizer(text, return_tensors="pt", truncation=True, max_length=512, padding=True).to(DEVICE)
        with torch.no_grad():
            outputs = model(**inputs)
        return outputs.last_hidden_state[:, 0, :].squeeze().cpu().numpy()

    def fetch_s3_file_content(url):
        parsed = urlparse(url)
        bucket, key = parsed.netloc, parsed.path.lstrip("/")
        filename = os.path.basename(key)
        obj = s3.get_object(Bucket=bucket, Key=key)
        content = obj["Body"].read().decode("utf-8", errors="ignore")
        return content, filename

    def upload_embedding(emb, filename):
        key = os.path.join(s3_emb_folder, filename + ".npy")
        np_bytes = emb.tobytes()
        s3.put_object(Bucket=S3_BUCKET, Key=key, Body=np_bytes)
        return f"s3://{S3_BUCKET}/{key}"

    # ----------------- Main processing -----------------
    emb_urls = []
    for url in s3_urls:
        code, fn = fetch_s3_file_content(url)
        lang = infer_language(fn)
        emb = get_embedding(code, lang)
        emb_url = upload_embedding(emb, fn)
        emb_urls.append(emb_url)
        print(f"✅ Saved embedding for {fn} -> {emb_url}")

    return emb_urls

# ----------------- Example usage -----------------
# if __name__ == "__main__":
#     test_s3_urls = [
#         "s3://autograder-dummy/submissions/code1.py",
#         "s3://autograder-dummy/submissions/code2.py",
#         "s3://autograder-dummy/submissions/code3.py"
#     ]
#     embeddings = generate_embeddings_from_s3(test_s3_urls)
#     print("Embeddings saved:", embeddings)
