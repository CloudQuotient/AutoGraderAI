import os
from dotenv import load_dotenv

load_dotenv()

class Settings:
    S3_BUCKET_NAME = os.getenv("S3_BUCKET_NAME", "demo-bucket")
    AWS_REGION = os.getenv("AWS_REGION", "us-east-1")
    DATABASE_URL = os.getenv("DATABASE_URL", "postgresql://user:pass@localhost:5432/autograder")
    COGNITO_POOL_ID = os.getenv("COGNITO_POOL_ID", "pool-id")
    COGNITO_CLIENT_ID = os.getenv("COGNITO_CLIENT_ID", "client-id")
    COGNITO_JWKS_URL = os.getenv("COGNITO_JWKS_URL", "https://cognito-idp.us-east-1.amazonaws.com/pool-id/.well-known/jwks.json")

settings = Settings()
