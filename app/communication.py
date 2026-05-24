import os
import requests

def send_temperature(celsius: float) -> None:
    api_url = os.getenv("API_URL")
    api_key = os.getenv("API_KEY")
    response = requests.post(
        api_url,
        json={"wert": round(celsius, 2)},
        headers={"Authorization": f"Bearer {api_key}"},
        timeout=10,
    )
    response.raise_for_status()
