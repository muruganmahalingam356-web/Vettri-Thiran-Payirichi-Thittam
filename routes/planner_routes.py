import json
import os
import uuid
from pathlib import Path
from fastapi import APIRouter, Depends, File, Form, HTTPException, Request, UploadFile
from fastapi.responses import HTMLResponse
from sqlalchemy.orm import Session
from database import get_db
from auth import get_current_user
from models.db_models import RecommendationHistory, User
from services.gemini_utils import generate_recommendations
from config import settings

router = APIRouter()
UPLOAD_DIR = Path("static/uploads")
UPLOAD_DIR.mkdir(parents=True, exist_ok=True)

@router.get("/home-planner", response_class=HTMLResponse)
def home_page(request: Request, user: User = Depends(get_current_user)):
    return request.app.state.templates.TemplateResponse("home_planner.html", {"request": request, "user": user})

@router.get("/party-planner", response_class=HTMLResponse)
def party_page(request: Request, user: User = Depends(get_current_user)):
    return request.app.state.templates.TemplateResponse("party_planner.html", {"request": request, "user": user})

@router.get("/jewelry-planner", response_class=HTMLResponse)
def jewelry_page(request: Request, user: User = Depends(get_current_user)):
    return request.app.state.templates.TemplateResponse("jewelry_planner.html", {"request": request, "user": user})

def save_history(db, user, planner, data, result):
    row = RecommendationHistory(user_id=user.id, planner=planner, budget=str(data.get("budget", "")), request_json=json.dumps(data), response_json=json.dumps(result))
    db.add(row); db.commit()

def result_page(request, user, result):
    return request.app.state.templates.TemplateResponse("recommendations.html", {"request": request, "user": user, "result": result})

@router.post("/generate-home", response_class=HTMLResponse)
def generate_home(request: Request, budget: float = Form(...), rooms: str = Form(...), style: str = Form("Modern"), notes: str = Form(""), db: Session = Depends(get_db), user: User = Depends(get_current_user)):
    if budget <= 0: raise HTTPException(400, "Budget must be greater than zero")
    room_list = [x.strip() for x in rooms.split(",") if x.strip()]
    data = {"budget": budget, "rooms": room_list, "style": style, "notes": notes}
    result = generate_recommendations("home", data)
    save_history(db, user, "home", data, result)
    return result_page(request, user, result)

@router.post("/generate-party", response_class=HTMLResponse)
def generate_party(request: Request, budget: float = Form(...), guests: int = Form(...), event_type: str = Form(...), venue: str = Form(...), notes: str = Form(""), db: Session = Depends(get_db), user: User = Depends(get_current_user)):
    if budget <= 0 or guests <= 0: raise HTTPException(400, "Budget and guest count must be greater than zero")
    data = {"budget": budget, "guests": guests, "event_type": event_type, "venue": venue, "notes": notes}
    result = generate_recommendations("party", data)
    save_history(db, user, "party", data, result)
    return result_page(request, user, result)

@router.post("/generate-jewelry", response_class=HTMLResponse)
async def generate_jewelry(request: Request, budget: float = Form(...), occasion: str = Form(...), style: str = Form(...), notes: str = Form(""), outfit_image: UploadFile | None = File(None), db: Session = Depends(get_db), user: User = Depends(get_current_user)):
    if budget <= 0: raise HTTPException(400, "Budget must be greater than zero")
    data = {"budget": budget, "occasion": occasion, "style": style, "notes": notes}
    image_path = None
    if outfit_image and outfit_image.filename:
        if outfit_image.content_type not in {"image/jpeg", "image/png", "image/webp"}:
            raise HTTPException(400, "Please upload JPG, PNG or WEBP image")
        content = await outfit_image.read() if hasattr(outfit_image, "read") else b""
        if len(content) > settings.MAX_UPLOAD_MB * 1024 * 1024:
            raise HTTPException(400, f"Image must be under {settings.MAX_UPLOAD_MB} MB")
        ext = Path(outfit_image.filename).suffix.lower() or ".jpg"
        image_path = str(UPLOAD_DIR / f"{uuid.uuid4().hex}{ext}")
        Path(image_path).write_bytes(content)
        data["outfit_image"] = True
    result = generate_recommendations("jewelry", data, image_path, outfit_image.content_type if outfit_image and outfit_image.filename else None)
    save_history(db, user, "jewelry", data, result)
    return result_page(request, user, result)
