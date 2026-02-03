# --- Example Execution ---
import requests
from adaptiveApiLive import AdaptiveApiLive


if __name__ == "__main__":
    # Replace these with your actual credentials
    API_SERVER = "http://localhost"
    API_TOKEN = "123"

    client = AdaptiveApiLive(API_SERVER, API_TOKEN)
    print(client.fetch_dashboard_entries())

    for m in client.fetch_machines():
        print(f"machine: {m['machine']}, type: {m.get('type', 'N/A')}")

