# debug_harvest_clients.py
from backend.harvest import fetch_time_entries
import pandas as pd

entries = fetch_time_entries("2025-05-01", "2025-05-15")
df = pd.DataFrame(entries)

# Extract nested names
client_names = df['project'].apply(lambda c: c.get('name') if isinstance(c, dict) else None)
print("Distinct Harvest client names:")
print(client_names.dropna().unique())
