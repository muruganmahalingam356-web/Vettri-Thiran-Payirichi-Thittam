from fastapi import APIRouter, Depends, Form, Request
from fastapi.responses import HTMLResponse, RedirectResponse
from sqlalchemy.orm import Session
from sqlalchemy.exc import IntegrityError
from database import get_db
from models.db_models import User
from models.schemas import RegisterRequest, LoginRequest
from auth import hash_password, verify_password, create_access_token

router = APIRouter()

def redirect_with_cookie(url: str, token: str):
    response = RedirectResponse(url=url, status_code=303)
    response.set_cookie("access_token", token, httponly=True, samesite="lax", max_age=86400)
    return response

@router.get("/register", response_class=HTMLResponse)
def register_page(request: Request):
    return request.app.state.templates.TemplateResponse("register.html", {"request": request, "error": None})

@router.post("/register")
def register(request: Request, name: str = Form(...), email: str = Form(...), password: str = Form(...), db: Session = Depends(get_db)):
    email = email.strip().lower()
    if len(password) < 6:
        return request.app.state.templates.TemplateResponse("register.html", {"request": request, "error": "Password must be at least 6 characters."})
    if db.query(User).filter(User.email == email).first():
        return request.app.state.templates.TemplateResponse("register.html", {"request": request, "error": "Email is already registered."})
    user = User(name=name.strip(), email=email, password_hash=hash_password(password))
    db.add(user)
    try:
        db.commit()
        db.refresh(user)
    except IntegrityError:
        db.rollback()
        return request.app.state.templates.TemplateResponse("register.html", {"request": request, "error": "Could not create account."})
    return redirect_with_cookie("/dashboard", create_access_token(user.id))

@router.get("/login", response_class=HTMLResponse)
def login_page(request: Request):
    return request.app.state.templates.TemplateResponse("login.html", {"request": request, "error": None})

@router.post("/login")
def login(request: Request, email: str = Form(...), password: str = Form(...), db: Session = Depends(get_db)):
    user = db.query(User).filter(User.email == email.strip().lower()).first()
    if not user or not verify_password(password, user.password_hash):
        return request.app.state.templates.TemplateResponse("login.html", {"request": request, "error": "Invalid email or password."})
    return redirect_with_cookie("/dashboard", create_access_token(user.id))

@router.get("/logout")
def logout():
    response = RedirectResponse("/", status_code=303)
    response.delete_cookie("access_token")
    return response

@router.post("/token")
def token(data: LoginRequest, db: Session = Depends(get_db)):
    user = db.query(User).filter(User.email == data.email.lower()).first()
    if not user or not verify_password(data.password, user.password_hash):
        return {"access_token": None, "token_type": "bearer", "detail": "Invalid credentials"}
    return {"access_token": create_access_token(user.id), "token_type": "bearer"}
