import pytest
from fastapi.testclient import TestClient
from main import app

client = TestClient(app)

def test_root():
    """Test endpoint racine"""
    response = client.get("/")
    assert response.status_code == 200
    assert "message" in response.json()
    assert "version" in response.json()

def test_health_check():
    """Test health check endpoint"""
    response = client.get("/health")
    # 200 ou 503 selon l'état des services
    assert response.status_code in [200, 503]
    data = response.json()
    assert "status" in data
    assert "service" in data

def test_docs_available():
    """Test que la documentation est disponible"""
    response = client.get("/docs")
    assert response.status_code == 200

def test_redoc_available():
    """Test que ReDoc est disponible"""
    response = client.get("/redoc")
    assert response.status_code == 200

def test_invalid_route():
    """Test 404 sur route invalide"""
    response = client.get("/invalid-route")
    assert response.status_code == 404

if __name__ == "__main__":
    pytest.main([__file__, "-v"])
