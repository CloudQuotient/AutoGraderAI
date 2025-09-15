from fastapi import FastAPI
from app.routes import assignments, submissions, presign, webhooks
import logging
import watchtower
from app.core.config import settings

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)
logger.addHandler(watchtower.CloudWatchLogHandler(log_group='AutoGraderAI', region_name=settings.AWS_REGION))

app = FastAPI()

app.include_router(assignments.router, prefix="/api/v1/assignments")
app.include_router(submissions.router, prefix="/api/v1/submissions")
app.include_router(presign.router, prefix="/api/v1/presign")
app.include_router(webhooks.router, prefix="/api/v1/grader-callback")
