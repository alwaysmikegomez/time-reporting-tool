# debug_sheets.py
import os, sys
sys.path.insert(0, os.getcwd())

from backend.sheets import list_client_tabs, fetch_planned_hours

print("TABS:", list_client_tabs())
print("MAY DATA:", fetch_planned_hours("2025-05-01", "2025-05-31", "Glencor Golf"))
