import pandas as pd
import pytest
import importlib

from backend import harvest
import config

# Dummy classes for mocking
class DummyResponse:
    def __init__(self, data):
        self._data = data
    def raise_for_status(self):
        pass
    def json(self):
        return self._data

class DummySession:
    def __init__(self, responses):
        # responses: list of dict to return on each get()
        self._responses = list(responses)
        self.headers = {}
    def headers_update(self, headers):
        self.headers.update(headers)
    def get(self, url, params=None):
        return DummyResponse(self._responses.pop(0))


def test_get_harvest_session_headers(monkeypatch):
    # Override config values
    monkeypatch.setattr(config, 'HARVEST_ACCESS_TOKEN', 'token123')
    monkeypatch.setattr(config, 'HARVEST_ACCOUNT_ID', '456')
    monkeypatch.setattr(config, 'HARVEST_USER_AGENT', 'App (email)')
    # Reload harvest module to pick up new config
    importlib.reload(harvest)

    session = harvest.get_harvest_session()
    headers = session.headers
    assert headers['Authorization'] == 'Bearer token123'
    assert headers['Harvest-Account-ID'] == '456'
    assert headers['User-Agent'] == 'App (email)'
    assert headers['Accept'] == 'application/json'


def test_fetch_time_entries_pagination(monkeypatch):
    # Prepare two pages of data
    page1 = {'time_entries': [{'id': 1}], 'links': {'next': 'url2'}}
    page2 = {'time_entries': [{'id': 2}], 'links': {'next': None}}
    dummy = DummySession([page1, page2])
    # monkeypatch get_harvest_session to return our dummy session
    monkeypatch.setattr(harvest, 'get_harvest_session', lambda: dummy)

    results = harvest.fetch_time_entries('2025-01-01', '2025-01-31')
    assert results == [{'id': 1}, {'id': 2}]


def test_fetch_recorded_hours_aggregation(monkeypatch):
    # Create sample entries, some matching client_id=10, some not
    entries = [
        {'client': {'id': 10}, 'spent_date': '2025-05-01', 'hours': 2},
        {'client': {'id': 10}, 'spent_date': '2025-05-01', 'hours': 3},
        {'client': {'id': 20}, 'spent_date': '2025-05-01', 'hours': 5},
        {'client': {'id': 10}, 'spent_date': '2025-05-02', 'hours': 4},
    ]
    # Monkeypatch fetch_time_entries
    monkeypatch.setattr(harvest, 'fetch_time_entries', lambda start, end: entries)

    df = harvest.fetch_recorded_hours('2025-05-01', '2025-05-31', client_id=10)
    # Expected aggregation: 2025-05-01 sum=5, 2025-05-02 sum=4
    expected = pd.DataFrame({
        'Date': pd.to_datetime(['2025-05-01', '2025-05-02']),
        'Hours': [5, 4]
    })
    pd.testing.assert_frame_equal(df.reset_index(drop=True), expected)
