from fastapi import APIRouter, Depends, HTTPException
from app.core.auth import get_current_user
from app.models import Assignment
from app.db import get_db
from sqlalchemy.orm import Session
from typing import List

router = APIRouter()

@router.get("/", response_model=List[Assignment])
def list_assignments(db: Session = Depends(get_db), user=Depends(get_current_user)):
    # TODO: Query assignments from DB
    return []

@router.post("/", response_model=Assignment)
def create_assignment(assignment: Assignment, db: Session = Depends(get_db), user=Depends(get_current_user)):
    # TODO: Insert assignment into DB
    return assignment
