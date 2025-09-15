from fastapi import APIRouter, Depends, Query
from app.core.auth import get_current_user
from app.core.config import settings
import boto3
import uuid

router = APIRouter()

@router.get("/")
def get_presigned_url(
    assignmentId: str = Query(...),
    filename: str = Query(...),
    user=Depends(get_current_user)
):
    s3_key = f"assignments/{assignmentId}/{uuid.uuid4()}_{filename}"
    s3 = boto3.client("s3", region_name=settings.AWS_REGION)
    url = s3.generate_presigned_url(
        "put_object",
        Params={"Bucket": settings.S3_BUCKET_NAME, "Key": s3_key},
        ExpiresIn=900
    )
    return {"url": url, "s3_key": s3_key}
