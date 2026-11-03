import pytest
from fastapi.testclient import TestClient
from app.main import app

client = TestClient(app)

def test_read_root():
    """Verify that root endpoint serves the HTML control dashboard."""
    response = client.get("/")
    assert response.status_code == 200
    assert "FastAPI" in response.text
    assert "Ganesh DevOps" in response.text

def test_health_check():
    """Verify health endpoint used by Docker and Jenkins smoke testing."""
    response = client.get("/health")
    assert response.status_code == 200
    data = response.json()
    assert data["status"] == "UP"
    assert data["service"] == "ganesh_devops_project_2"
    assert data["framework"] == "FastAPI"
    assert "timestamp" in data
    assert data["checks"]["web_server"] == "healthy"

def test_metrics_endpoint():
    """Verify metrics endpoint returns system metadata."""
    response = client.get("/api/metrics")
    assert response.status_code == 200
    data = response.json()
    assert data["status"] == "healthy"
    assert "total_items" in data
    assert "system_metrics" in data
    assert "hostname" in data["system_metrics"]

def test_list_items():
    """Verify listing all DevOps items."""
    response = client.get("/api/items")
    assert response.status_code == 200
    items = response.json()
    assert isinstance(items, list)
    assert len(items) >= 4

def test_get_item_by_id():
    """Verify retrieving a single item by id."""
    response = client.get("/api/items/1")
    assert response.status_code == 200
    data = response.json()
    assert data["id"] == 1
    assert "title" in data

def test_get_item_not_found():
    """Verify 404 response when querying non-existent item."""
    response = client.get("/api/items/99999")
    assert response.status_code == 404
    assert "not found" in response.json()["detail"].lower()

def test_create_item_success():
    """Verify creating a new DevOps item via POST."""
    new_task = {
        "title": "Configure Prometheus Metrics Exporter",
        "category": "Monitoring",
        "priority": "High",
        "status": "In Progress",
        "description": "Export ASGI metrics to Prometheus server."
    }
    response = client.post("/api/items", json=new_task)
    assert response.status_code == 201
    data = response.json()
    assert data["title"] == new_task["title"]
    assert data["category"] == new_task["category"]
    assert "id" in data
    assert "created_at" in data

def test_create_item_validation_error():
    """Verify FastAPI/Pydantic automatic validation on bad payload."""
    bad_payload = {
        "title": "x",  # Min length is 2
        "category": "DevOps"
    }
    response = client.post("/api/items", json=bad_payload)
    assert response.status_code == 422  # Unprocessable Entity

def test_delete_item():
    """Verify deleting an existing item."""
    # Create an item first to delete
    create_res = client.post("/api/items", json={
        "title": "Temporary Task for Deletion",
        "category": "Testing",
        "priority": "Low",
        "status": "Pending"
    })
    assert create_res.status_code == 201
    item_id = create_res.json()["id"]

    # Delete it
    del_res = client.delete(f"/api/items/{item_id}")
    assert del_res.status_code == 204

    # Verify it is gone
    get_res = client.get(f"/api/items/{item_id}")
    assert get_res.status_code == 404
