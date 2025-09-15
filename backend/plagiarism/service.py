import boto3
import numpy as np
import faiss
import requests
from typing import List, Dict

SAGEMAKER_ENDPOINT = 'codebert-endpoint'  # Replace with your endpoint name
SIMILARITY_THRESHOLD = 0.85

# In-memory FAISS index for demo (replace with persistent storage in prod)
faiss_index = faiss.IndexFlatL2(768)  # 768 for CodeBERT
submission_embeddings = {}  # submission_id -> embedding
submission_ids = []

def get_code_embedding(code: str) -> np.ndarray:
    client = boto3.client('sagemaker-runtime')
    response = client.invoke_endpoint(
        EndpointName=SAGEMAKER_ENDPOINT,
        ContentType='application/json',
        Body=f'{{"code": "{code}"}}'
    )
    embedding = np.array(requests.utils.json.loads(response['Body'].read()))
    return embedding.astype('float32')

def check_plagiarism(submission_id: str, code: str) -> Dict:
    embedding = get_code_embedding(code)
    # Add to index
    faiss_index.add(np.expand_dims(embedding, axis=0))
    submission_embeddings[submission_id] = embedding
    submission_ids.append(submission_id)
    # Search for similar submissions
    if faiss_index.ntotal > 1:
        D, I = faiss_index.search(np.expand_dims(embedding, axis=0), k=10)
        similar_submissions = []
        for dist, idx in zip(D[0], I[0]):
            if idx == len(submission_ids) - 1:
                continue  # Skip self
            similarity = 1 - dist / 2  # Cosine similarity approximation
            if similarity > SIMILARITY_THRESHOLD:
                similar_submissions.append({
                    'id': submission_ids[idx],
                    'similarity': round(float(similarity), 2)
                })
    else:
        similar_submissions = []
    return {
        'submission_id': submission_id,
        'similar_submissions': similar_submissions
    }
