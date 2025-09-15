import pytest
from fastapi.testclient import TestClient
from app.main import app

client = TestClient(app)

def test_presign():
    response = client.get("/api/v1/presign", params={"assignmentId": "a1", "filename": "test.txt"}, headers={"Authorization": "Bearer demo.jwt.token"})
    assert response.status_code == 200
    data = response.json()
    assert "url" in data
    assert "s3_key" in data
