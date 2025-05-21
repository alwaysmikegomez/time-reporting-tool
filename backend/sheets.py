# backend/sheets.py
import os
import re
from typing import List
from flask import current_app as app
import pandas as pd
import gspread
from google.oauth2.service_account import Credentials

from config import (
    GOOGLE_SHEETS_CREDENTIALS_JSON,
    GOOGLE_SHEET_ID,
    CACHE_LIST_CLIENT_TABS_TIMEOUT,
    CACHE_FETCH_PLANNED_HOURS_TIMEOUT,
)
from backend.extensions import cache

SCOPES = ['https://www.googleapis.com/auth/spreadsheets.readonly']
HEADER_ROW_IDX = 7

def get_gspread_client() -> gspread.Client:
    creds_path = os.path.expandvars(os.path.expanduser(GOOGLE_SHEETS_CREDENTIALS_JSON))
    if not os.path.isfile(creds_path):
        raise FileNotFoundError(f"Credentials file not found: {creds_path}")
    credentials = Credentials.from_service_account_file(creds_path, scopes=SCOPES)
    return gspread.authorize(credentials)

@cache.memoize(timeout=CACHE_LIST_CLIENT_TABS_TIMEOUT)
def list_client_tabs() -> List[str]:
    client = get_gspread_client()
    sheet  = client.open_by_key(GOOGLE_SHEET_ID)
    filtered = []
    for ws in sheet.worksheets():
        title = ws.title.strip()
        low   = title.lower()
        if low == 'client tasks list notes':
            continue
        if re.match(r'^[A-Za-z]+ - \d{4}$', title):
            continue
        filtered.append(title)
    return filtered

@cache.memoize(timeout=CACHE_FETCH_PLANNED_HOURS_TIMEOUT)
def fetch_planned_hours(start_date: str, end_date: str, tab_name: str) -> pd.DataFrame:
    app.logger.debug("[list_client_tabs] reading tabs from Google Sheets")
    client = get_gspread_client()
    try:
        ws = client.open_by_key(GOOGLE_SHEET_ID).worksheet(tab_name)
    except gspread.WorksheetNotFound:
        raise ValueError(f"Worksheet/tab not found: {tab_name}")

    rows = ws.get_all_values()
    if len(rows) <= HEADER_ROW_IDX:
        return pd.DataFrame(columns=['Date', 'Hours'])

    headers = [c.strip() for c in rows[HEADER_ROW_IDX]]
    data    = rows[HEADER_ROW_IDX + 1:]
    df      = pd.DataFrame(data, columns=headers)

    if 'Production month' not in headers or 'Total time' not in headers:
        raise ValueError("Expected 'Production month' and 'Total time' columns in header row")

    df['Date']  = pd.to_datetime(df['Production month'], errors='coerce')
    df['Hours'] = pd.to_numeric(df['Total time'], errors='coerce').fillna(0)

    start = pd.to_datetime(start_date)
    end   = pd.to_datetime(end_date)
    df_out = df[df['Date'].between(start, end)][['Date', 'Hours']].copy()

    df_out.sort_values('Date', inplace=True)
    df_out.reset_index(drop=True, inplace=True)
    return df_out

__all__ = ['get_gspread_client', 'list_client_tabs', 'fetch_planned_hours']
