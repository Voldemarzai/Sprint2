import pytest
from fastapi.testclient import TestClient
from main import app

client = TestClient(app)

def test_get_pereval_not_found():
    response = client.get("/submitData/999999/")
    assert response.status_code == 404

def test_update_pereval_invalid_status():
    # Предполагаем, что перевал с ID=1 имеет статус не 'new'
    response = client.patch(
        "/submitData/1/",
        json={
            "data": {"title": "Новое название", ...},
            "images": [...],
            "activities": [...]
        }
    )
    assert response.status_code == 400
    assert "только для записей со статусом 'new'" in response.json()["detail"]

def test_get_user_perevals():
    response = client.get("/submitData/?user__email=test@example.com")
    assert response.status_code == 200
    assert isinstance(response.json()["perevals"], list)