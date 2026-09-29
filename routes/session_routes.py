from fastapi import APIRouter, Depends, Request
from auth import get_current_user
from models.db_models import User

router = APIRouter()

@router.get("/session-info")
def session_info(user: User = Depends(get_current_user)):
    return {"logged_in": True, "user_id": user.id, "name": user.name, "email": user.email}

@router.get("/session-data")
def session_data(user: User = Depends(get_current_user)):
    return {"user": {"id": user.id, "name": user.name, "email": user.email}, "message": "Session is active"}
