import pytest
from datetime import date

def test_get_clients(client):
    resp = client.get("/api/clients")
    assert resp.status_code == 200
    data = resp.get_json()
    assert isinstance(data, list)
    assert "FooCorp" in data
    assert "BarInc" in data

def test_get_data_happy_path(client):
    # Using the default mocks from conftest.py
    resp = client.get("/api/data", query_string={
        "client": "FooCorp",
        "start":  "2025-05-01",
        "end":    "2025-05-15",
    })
    assert resp.status_code == 200
    payload = resp.get_json()

    # Planned: one entry of 4 hours
    assert payload["metrics"]["total_planned"] == 4
    # Actual: one entry of 2 hours
    assert payload["metrics"]["total_actual"] == 2

    # Check list structure
    assert isinstance(payload["planned"], list)
    assert isinstance(payload["actual"], list)
    assert payload["planned"][0]["date"] == "2025-05-01"
    assert payload["actual"][0]["hours"] == 2

@pytest.mark.parametrize("params, missing_field", [
    ({}, "client"),
    ({"start": "2025-05-01"}, "client,end"),
    ({"client": "FooCorp"}, "start,end"),
])
def test_get_data_missing_params(client, params, missing_field):
    resp = client.get("/api/data", query_string=params)
    assert resp.status_code == 400
    err = resp.get_json()
    assert "error" in err

def test_get_data_bad_date_format(client):
    resp = client.get("/api/data", query_string={
        "client": "FooCorp",
        "start":  "May 1 2025",
        "end":    "2025-05-15",
    })
    assert resp.status_code == 400
    assert "Dates must be YYYY-MM-DD" in resp.get_json()["error"]

def test_get_data_start_after_end(client):
    resp = client.get("/api/data", query_string={
        "client": "FooCorp",
        "start":  "2025-05-16",
        "end":    "2025-05-15",
    })
    assert resp.status_code == 400
    assert "start must be ≤ end" in resp.get_json()["error"]
