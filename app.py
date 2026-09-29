from pathlib import Path
from fastapi import FastAPI, Request
from fastapi.responses import HTMLResponse
from fastapi.staticfiles import StaticFiles
from fastapi.templating import Jinja2Templates
from fastapi.middleware.cors import CORSMiddleware
from database import Base, engine
from routes.auth_routes import router as auth_router
from routes.planner_routes import router as planner_router
from routes.session_routes import router as session_router
from routes.history_routes import router as history_router

Base.metadata.create_all(bind=engine)

app = FastAPI(title="PocketSmart AI", version="1.0.0")
app.add_middleware(CORSMiddleware, allow_origins=["http://127.0.0.1:8000", "http://localhost:8000"], allow_credentials=True, allow_methods=["*"], allow_headers=["*"])
app.mount("/static", StaticFiles(directory="static"), name="static")
app.state.templates = Jinja2Templates(directory="templates")

app.include_router(auth_router)
app.include_router(planner_router)
app.include_router(session_router)
app.include_router(history_router)

@app.get("/", response_class=HTMLResponse)
def home(request: Request):
    return app.state.templates.TemplateResponse("index.html", {"request": request})

@app.get("/dashboard", response_class=HTMLResponse)
def dashboard(request: Request):
    from auth import get_current_user
    from database import SessionLocal
    db = SessionLocal()
    try:
        user = get_current_user(request, db)
        return app.state.templates.TemplateResponse("dashboard.html", {"request": request, "user": user})
    finally:
        db.close()

@app.get("/health")
def health():
    return {"status": "ok", "service": "PocketSmart AI"}

@app.on_event("startup")
def startup():
    Path("static/uploads").mkdir(parents=True, exist_ok=True)

if __name__ == "__main__":
    import uvicorn
    uvicorn.run("app:app", host="127.0.0.1", port=8000, reload=True)
