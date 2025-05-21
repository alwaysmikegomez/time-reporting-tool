import pytest
import pandas as pd

from backend.extensions import cache
import backend.sheets as sheets
import backend.harvest as harvest

@pytest.fixture(autouse=True)
def app_context():
    """
    Push a Flask app context so cache.memoize works
    """
    from backend.app import create_app
    app = create_app()
    ctx = app.app_context()
    ctx.push()
    yield
    ctx.pop()

@pytest.fixture(autouse=True)
def clear_cache():
    """
    Clear cache before each test
    """
    cache.clear()


def test_fetch_planned_hours_memoization(monkeypatch):
    calls = {'n': 0}

    # Stub get_gspread_client to count invocations
    class FakeWorksheet:
        def get_all_values(self):
            return []  # length <= HEADER_ROW_IDX triggers empty DataFrame

    class FakeSheet:
        def worksheet(self, tab_name):  # noqa: ARG012
            return FakeWorksheet()

    class FakeClient:
        def open_by_key(self, key):  # noqa: ARG001
            return FakeSheet()

    def fake_get_client():
        calls['n'] += 1
        return FakeClient()

    monkeypatch.setattr(sheets, 'get_gspread_client', fake_get_client)

    # Call twice with identical args
    df1 = sheets.fetch_planned_hours('2025-05-01', '2025-05-15', 'SomeTab')
    df2 = sheets.fetch_planned_hours('2025-05-01', '2025-05-15', 'SomeTab')

    # Underlying get_gspread_client should be called only once
    assert calls['n'] == 1, f"Expected 1 call to get_gspread_client, got {calls['n']}"
    assert isinstance(df1, pd.DataFrame)
    assert df1.equals(df2)


def test_fetch_time_entries_memoization(monkeypatch):
    calls = {'n': 0}

    # Stub get_harvest_session to count invocations and return a fake session
    class FakeResponse:
        def __init__(self):
            self._json = {'time_entries': [], 'links': {}}

        def raise_for_status(self):
            pass

        def json(self):
            return self._json

    class FakeSession:
        def get(self, url, params=None):  # noqa: ARG002
            return FakeResponse()

    def fake_get_harvest_session():
        calls['n'] += 1
        return FakeSession()

    monkeypatch.setattr(harvest, 'get_harvest_session', fake_get_harvest_session)

    # Call twice with identical args
    list1 = harvest.fetch_time_entries('2025-05-01', '2025-05-15')
    list2 = harvest.fetch_time_entries('2025-05-01', '2025-05-15')

    # Underlying get_harvest_session should be called only once
    assert calls['n'] == 1, f"Expected 1 call to get_harvest_session, got {calls['n']}"
    assert list1 == list2 == []
