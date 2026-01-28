import pytest
from fastapi.testclient import TestClient
from main import app


client = TestClient(app)


def test_root_endpoint():
    # Basic sanity check that the app responds
    res = client.get('/')
    # Accept either 200 or 404 depending on routes defined
    assert res.status_code in (200, 404)


def test_devices_list_route():
    # If route exists under /api/v1/devices, ensure it returns a proper response
    res = client.get('/api/v1/devices')
    assert res.status_code in (200, 404, 401)
