from fastapi import APIRouter, Depends, HTTPException
from app.core.auth import get_current_user
from app.db import get_db
from sqlalchemy.orm import Session

router = APIRouter()

@router.post("/")
def grader_callback(payload: dict, db: Session = Depends(get_db), user=Depends(get_current_user)):
    # TODO: Update submission grades/results in DB
    return {"status": "received"}
