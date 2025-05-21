import pytest
from backend.app import create_app

from backend.api.data import list_client_tabs, fetch_planned_hours  # or import via sheets module
from backend.harvest import fetch_time_entries

@pytest.fixture
def app(monkeypatch):
    """
    Create a Flask app configured for testing, with mocks for external calls.
    """
    app = create_app()
    app.config.update({
        "TESTING": True,
    })

    # Default mocks: no external calls
    monkeypatch.setattr('backend.api.data.list_client_tabs',
                        lambda: ["FooCorp", "BarInc"])
    monkeypatch.setattr('backend.api.data.fetch_planned_hours',
                        lambda start, end, client: __import__('pandas').DataFrame(
                            [{"date": __import__('datetime').date(2025,5,1), "hours": 4}]
                        ))
    monkeypatch.setattr('backend.api.data.fetch_time_entries',
                        lambda start, end: [
                            {"project": {"name": "FooCorp"},
                             "hours": 2,
                             "spent_date": "2025-05-01"}
                        ])

    yield app

@pytest.fixture
def client(app):
    return app.test_client()
