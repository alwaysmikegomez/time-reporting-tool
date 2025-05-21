import pytest
import pandas as pd

from backend.extensions import cache
from backend.app import create_app

# Fixtures for Flask test client and app context
@pytest.fixture
def client():
    app = create_app()
    app.testing = True
    with app.test_client() as client:
        with app.app_context():
            yield client

@pytest.fixture(autouse=True)
def clear_cache():
    cache.clear()

# Stub classes for sheets
class FakeWorksheet:
    def get_all_values(self): return []
class FakeSheet:
    def worksheet(self, name): return FakeWorksheet()
class FakeClient:
    def open_by_key(self, key): return FakeSheet()

# Test refresh logic for /api/data
def test_refresh_busts_cache(monkeypatch, client):
    calls = {'n': 0}
    # Stub get_gspread_client to count calls
    def fake_get_client():
        calls['n'] += 1
        return FakeClient()
    import backend.sheets as sheets
    monkeypatch.setattr(sheets, 'get_gspread_client', fake_get_client)

    # Retrieve a valid client name dynamically
    resp = client.get('/api/clients')
    assert resp.status_code == 200
    clients = resp.get_json()
    assert clients, "No clients available"
    tab = clients[0]

    # 1st call -> cache miss
    resp1 = client.get(f'/api/data?start=2025-05-01&end=2025-05-15&client={tab}')
    assert resp1.status_code == 200
    # 2nd call -> cached -> no new fetch
    resp2 = client.get(f'/api/data?start=2025-05-01&end=2025-05-15&client={tab}')
    assert resp2.status_code == 200
    assert calls['n'] == 1, f"Expected 1 fetch, got {calls['n']}"

    # 3rd call with refresh -> cache bust -> new fetch
    resp3 = client.get(f'/api/data?start=2025-05-01&end=2025-05-15&client={tab}&refresh=1')
    assert resp3.status_code == 200
    assert calls['n'] == 2, f"Expected 2 fetches after refresh, got {calls['n']}"
