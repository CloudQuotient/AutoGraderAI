import boto3
from app.core.config import settings
from typing import List, Dict

s3 = boto3.client('s3', region_name=settings.AWS_REGION)


def save_submission_file(student_id: str, assignment_id: str, file_path: str) -> str:
    s3_key = f"submissions/{student_id}/{assignment_id}/{file_path.split('/')[-1]}"
    s3.upload_file(file_path, settings.S3_BUCKET_NAME, s3_key)
    return s3_key


def fetch_history(student_id: str) -> List[Dict]:
    prefix = f"submissions/{student_id}/"
    resp = s3.list_object_versions(Bucket=settings.S3_BUCKET_NAME, Prefix=prefix)
    history = []
    for obj in resp.get('Versions', []):
        history.append({
            'key': obj['Key'],
            'version_id': obj['VersionId'],
            'last_modified': obj['LastModified'].isoformat(),
            'is_latest': obj['IsLatest']
        })
    return history
