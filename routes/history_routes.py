import json
from fastapi import APIRouter, Depends, Request
from fastapi.responses import HTMLResponse
from sqlalchemy.orm import Session
from database import get_db
from auth import get_current_user
from models.db_models import RecommendationHistory, User

router = APIRouter()

@router.get("/history", response_class=HTMLResponse)
def history_page(request: Request, db: Session = Depends(get_db), user: User = Depends(get_current_user)):
    rows = db.query(RecommendationHistory).filter(RecommendationHistory.user_id == user.id).order_by(RecommendationHistory.created_at.desc()).all()
    return request.app.state.templates.TemplateResponse("history.html", {"request": request, "user": user, "history": rows})

@router.get("/recommendations-details/{history_id}")
def recommendation_details(history_id: int, db: Session = Depends(get_db), user: User = Depends(get_current_user)):
    row = db.query(RecommendationHistory).filter(RecommendationHistory.id == history_id, RecommendationHistory.user_id == user.id).first()
    if not row:
        return {"detail": "Recommendation not found"}
    return {"id": row.id, "planner": row.planner, "request": json.loads(row.request_json), "result": json.loads(row.response_json), "created_at": row.created_at}
