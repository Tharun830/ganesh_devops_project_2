import os
import platform
import socket
import time
from datetime import datetime, timezone
from typing import List, Optional
from fastapi import FastAPI, HTTPException, Request, status
from fastapi.responses import HTMLResponse, JSONResponse
from fastapi.staticfiles import StaticFiles
from fastapi.templating import Jinja2Templates
from pydantic import BaseModel, Field

START_TIME = time.time()

# ---------------------------------------------------------
# Pydantic Schemas
# ---------------------------------------------------------
class ProjectItemBase(BaseModel):
    title: str = Field(..., min_length=2, max_length=100, description="Task or Service Title")
    category: str = Field(default="Development", max_length=50, description="Task Category")
    priority: str = Field(default="Medium", description="Low, Medium, High, or Critical")
    status: str = Field(default="Pending", description="Pending, In Progress, or Completed")
    description: Optional[str] = Field(default="", max_length=250, description="Optional Details")

class ProjectItemCreate(ProjectItemBase):
    pass

class ProjectItemUpdate(BaseModel):
    title: Optional[str] = Field(None, min_length=2, max_length=100)
    category: Optional[str] = Field(None, max_length=50)
    priority: Optional[str] = None
    status: Optional[str] = None
    description: Optional[str] = None

class ProjectItem(ProjectItemBase):
    id: int
    created_at: str

# ---------------------------------------------------------
# In-Memory Database Storage
# ---------------------------------------------------------
INITIAL_ITEMS = [
    {
        "id": 1,
        "title": "Set up FastAPI Async Backend",
        "category": "Backend",
        "priority": "High",
        "status": "Completed",
        "description": "High performance REST API with automatic OpenAPI specs.",
        "created_at": "2026-11-03 12:00:00"
    },
    {
        "id": 2,
        "title": "Build Responsive Control Dashboard",
        "category": "Frontend",
        "priority": "High",
        "status": "Completed",
        "description": "Full-stack UI with live metrics and interactive CRUD interface.",
        "created_at": "2026-11-03 12:30:00"
    },
    {
        "id": 3,
        "title": "Containerize with Multi-Stage Dockerfile",
        "category": "DevOps",
        "priority": "Critical",
        "status": "Completed",
        "description": "Production container with non-root security compliance.",
        "created_at": "2026-11-03 13:00:00"
    },
    {
        "id": 4,
        "title": "Automate Jenkins & GitHub Actions Pipelines",
        "category": "CI/CD",
        "priority": "Critical",
        "status": "In Progress",
        "description": "Continuous integration with automated testing and smoke checks.",
        "created_at": "2026-11-03 13:15:00"
    }
]

items_db: List[dict] = list(INITIAL_ITEMS)

# ---------------------------------------------------------
# FastAPI App Initialization
# ---------------------------------------------------------
app = FastAPI(
    title="Ganesh DevOps Project 2",
    description="Full-Stack Web Application featuring FastAPI REST API, Responsive UI, Docker & Jenkins CI/CD.",
    version="1.0.0",
    docs_url="/docs",
    redoc_url="/redoc"
)

# Static and Templates Directory Configuration
BASE_DIR = os.path.dirname(os.path.abspath(__file__))
static_dir = os.path.join(BASE_DIR, "static")
templates_dir = os.path.join(BASE_DIR, "templates")

if os.path.isdir(static_dir):
    app.mount("/static", StaticFiles(directory=static_dir), name="static")

templates = Jinja2Templates(directory=templates_dir)

def get_system_stats():
    uptime_seconds = int(time.time() - START_TIME)
    hours, rem = divmod(uptime_seconds, 3600)
    minutes, seconds = divmod(rem, 60)
    uptime_str = f"{hours:02d}h {minutes:02d}m {seconds:02d}s"

    return {
        "hostname": socket.gethostname(),
        "os": f"{platform.system()} {platform.release()}",
        "architecture": platform.machine(),
        "python_version": platform.python_version(),
        "uptime_seconds": uptime_seconds,
        "uptime_human": uptime_str,
        "is_containerized": os.path.exists("/.dockerenv") or os.getenv("RUNNING_IN_DOCKER") == "true",
        "server_time_utc": datetime.now(timezone.utc).strftime("%Y-%m-%d %H:%M:%S UTC")
    }

# ---------------------------------------------------------
# Frontend Routes
# ---------------------------------------------------------
@app.get("/", response_class=HTMLResponse)
async def home(request: Request):
    stats = get_system_stats()
    return templates.TemplateResponse(
        request=request,
        name="index.html",
        context={
            "app_name": "Ganesh DevOps Full-Stack Hub",
            "app_version": "1.0.0",
            "stats": stats,
            "items": items_db
        }
    )

# ---------------------------------------------------------
# Health & Metrics API
# ---------------------------------------------------------
@app.get("/health", tags=["Health & Monitoring"])
async def health_check():
    return {
        "status": "UP",
        "service": "ganesh_devops_project_2",
        "version": "1.0.0",
        "framework": "FastAPI",
        "timestamp": datetime.now(timezone.utc).isoformat(),
        "checks": {
            "web_server": "healthy",
            "database": "operational"
        }
    }

@app.get("/api/metrics", tags=["Health & Monitoring"])
async def get_metrics():
    stats = get_system_stats()
    return {
        "service": "ganesh_devops_project_2",
        "status": "healthy",
        "total_items": len(items_db),
        "system_metrics": stats
    }

# ---------------------------------------------------------
# CRUD REST API for Items
# ---------------------------------------------------------
@app.get("/api/items", response_model=List[ProjectItem], tags=["DevOps Items"])
async def list_items(category: Optional[str] = None, status: Optional[str] = None):
    results = items_db
    if category:
        results = [item for item in results if item["category"].lower() == category.lower()]
    if status:
        results = [item for item in results if item["status"].lower() == status.lower()]
    return results

@app.get("/api/items/{item_id}", response_model=ProjectItem, tags=["DevOps Items"])
async def get_item(item_id: int):
    for item in items_db:
        if item["id"] == item_id:
            return item
    raise HTTPException(status_code=404, detail=f"Item with ID {item_id} not found")

@app.post("/api/items", response_model=ProjectItem, status_code=status.HTTP_201_CREATED, tags=["DevOps Items"])
async def create_item(payload: ProjectItemCreate):
    new_id = max([item["id"] for item in items_db], default=0) + 1
    new_item = {
        "id": new_id,
        "title": payload.title,
        "category": payload.category,
        "priority": payload.priority,
        "status": payload.status,
        "description": payload.description or "",
        "created_at": datetime.now(timezone.utc).strftime("%Y-%m-%d %H:%M:%S")
    }
    items_db.append(new_item)
    return new_item

@app.put("/api/items/{item_id}", response_model=ProjectItem, tags=["DevOps Items"])
async def update_item(item_id: int, payload: ProjectItemUpdate):
    for item in items_db:
        if item["id"] == item_id:
            update_data = payload.model_dump(exclude_unset=True)
            item.update(update_data)
            return item
    raise HTTPException(status_code=404, detail=f"Item with ID {item_id} not found")

@app.delete("/api/items/{item_id}", status_code=status.HTTP_204_NO_CONTENT, tags=["DevOps Items"])
async def delete_item(item_id: int):
    global items_db
    for i, item in enumerate(items_db):
        if item["id"] == item_id:
            items_db.pop(i)
            return None
    raise HTTPException(status_code=404, detail=f"Item with ID {item_id} not found")

if __name__ == "__main__":
    import uvicorn
    port = int(os.getenv("PORT", 8000))
    uvicorn.run("app.main:app", host="0.0.0.0", port=port, reload=True)
