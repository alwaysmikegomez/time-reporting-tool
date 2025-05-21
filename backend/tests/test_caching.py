import time
import pytest

from backend.app import create_app
from backend.extensions import cache

@pytest.fixture
def client():
    app = create_app()
    app.testing = True
    return app.test_client()

def get_valid_client(client):
    resp = client.get("/api/clients")
    assert resp.status_code == 200
    clients = resp.get_json()
    assert clients, "No client tabs available"
    return clients[0]

def test_cache_response_times(client):
    # Ensure cache is clear before testing
    cache.clear()

    client_name = get_valid_client(client)
    start = "2025-05-01"
    end = "2025-05-15"
    url = f"/api/data?start={start}&end={end}&client={client_name}"

    # First (uncached) request
    t1_start = time.time()
    resp1 = client.get(url)
    t1 = time.time() - t1_start
    assert resp1.status_code == 200

    # Second (cached) request
    t2_start = time.time()
    resp2 = client.get(url)
    t2 = time.time() - t2_start
    assert resp2.status_code == 200

    # The cached response should be significantly faster
    assert t2 < t1 * 0.2, f"Cache did not improve response time: {t1:.3f}s -> {t2:.3f}s"
