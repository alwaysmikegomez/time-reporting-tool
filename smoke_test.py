# smoke_test.py

import requests
import sys

def main():
    base_url = "http://127.0.0.1:5000"

    # 1) /api/clients
    print("→ GET /api/clients")
    try:
        r1 = requests.get(f"{base_url}/api/clients")
        print("  Status:", r1.status_code)
        print("  Body:", r1.text, "\n")
    except requests.exceptions.RequestException as e:
        print("❌ Failed to call /api/clients:", e)
        sys.exit(1)

    # 2) /api/data
    # pick first client from the above response if valid JSON
    try:
        clients = r1.json()
        sample_client = clients[0] if isinstance(clients, list) and clients else "ExampleClient"
    except ValueError:
        sample_client = "ExampleClient"

    params = {
        "client": sample_client,
        "start":  "2025-05-01",
        "end":    "2025-05-15"
    }
    url = f"{base_url}/api/data"
    print(f"→ GET {url}?client={params['client']}&start={params['start']}&end={params['end']}")
    try:
        r2 = requests.get(url, params=params)
        print("  Status:", r2.status_code)
        print("  Body:", r2.text)
        if r2.status_code != 200:
            sys.exit(1)
    except requests.exceptions.RequestException as e:
        print("❌ Failed to call /api/data:", e)
        sys.exit(1)

    print("\n✅ Smoke test passed!")

if __name__ == "__main__":
    main()
