# backend/harvest.py
from typing import List

import pandas as pd
import requests

from config import (
    HARVEST_ACCOUNT_ID,
    HARVEST_ACCESS_TOKEN,
    HARVEST_USER_AGENT,
    CACHE_FETCH_TIME_ENTRIES_TIMEOUT,
)
from flask import current_app as app
from backend.extensions import cache

HARVEST_API_BASE = 'https://api.harvestapp.com/v2'

def get_harvest_session() -> requests.Session:
    session = requests.Session()
    session.headers.update({
        'Authorization': f'Bearer {HARVEST_ACCESS_TOKEN}',
        'Harvest-Account-ID': str(HARVEST_ACCOUNT_ID),
        'User-Agent': HARVEST_USER_AGENT,
        'Accept': 'application/json',
    })
    return session

@cache.memoize(timeout=CACHE_FETCH_TIME_ENTRIES_TIMEOUT)
def fetch_time_entries(start_date: str, end_date: str) -> List[dict]:
    app.logger.debug(f"[fetch_time_entries] hitting Harvest API for {start_date} → {end_date}")
    session = get_harvest_session()
    entries: List[dict] = []
    url = f"{HARVEST_API_BASE}/time_entries"
    params = {'from': start_date, 'to': end_date, 'per_page': 100}

    while url:
        try:
            resp = session.get(url, params=params)
            resp.raise_for_status()
        except requests.exceptions.HTTPError as err:
            print(f"[harvest] Warning: failed to fetch time entries ({err})")
            return []

        data = resp.json()
        entries.extend(data.get('time_entries', []))
        url = data.get('links', {}).get('next')
        params = {}
    return entries

def fetch_recorded_hours(start_date: str, end_date: str, client_id: int) -> pd.DataFrame:
    entries = fetch_time_entries(start_date, end_date)
    filtered = [e for e in entries if e.get('client', {}).get('id') == client_id]

    if not filtered:
        return pd.DataFrame(columns=['Date', 'Hours'])

    df = pd.DataFrame(filtered)
    df['Date'] = pd.to_datetime(df['spent_date'])
    df['Hours'] = pd.to_numeric(df['hours'], errors='coerce').fillna(0)
    agg = df.groupby('Date', as_index=False)['Hours'].sum()
    agg.sort_values('Date', inplace=True)
    agg.reset_index(drop=True, inplace=True)
    return agg

__all__ = ['get_harvest_session', 'fetch_time_entries', 'fetch_recorded_hours']
