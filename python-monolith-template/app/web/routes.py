from fastapi import APIRouter, Request
from fastapi.responses import HTMLResponse
from fastapi.templating import Jinja2Templates
from app.config import settings

admin_router = APIRouter()
templates = Jinja2Templates(directory="app/web/templates")

@admin_router.get("/", response_class=HTMLResponse)
async def admin_dashboard(request: Request):
    return templates.TemplateResponse("dashboard.html", {
        "request": request,
        "project_name": settings.PROJECT_NAME,
        "use_db": settings.USE_DB
    })
