import os
from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import RedirectResponse
from fastapi.staticfiles import StaticFiles

from database import init_db
from routers.templates import load_templates
from routers import auth, templates, process, history
from config import OUTPUT_DIR

app = FastAPI(
    title="Simple File Helper",
    description="Upload bank statements → Gemini AI extracts transactions → Download Excel",
    version="2.0.0"
)

# CORS — allow same-origin browser access
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Register API routers
app.include_router(auth.router)
app.include_router(templates.router)
app.include_router(process.router)
app.include_router(history.router)


@app.on_event("startup")
async def startup():
    # Ensure output directory exists
    os.makedirs(OUTPUT_DIR, exist_ok=True)

    # Initialize database tables
    init_db()

    # Load all template JSON files into memory
    load_templates()


@app.get("/app/index.html")
def legacy_login_page():
    return RedirectResponse(url="/", status_code=307)


@app.get("/app/app.html")
def legacy_app_page():
    return RedirectResponse(url="/app.html", status_code=307)


# Serve frontend static files
backend_dir = os.path.dirname(os.path.abspath(__file__))
frontend_dir = os.path.abspath(os.path.join(backend_dir, "..", "frontend"))

if os.path.exists(frontend_dir):
    app.mount("/", StaticFiles(directory=frontend_dir, html=True), name="frontend")
