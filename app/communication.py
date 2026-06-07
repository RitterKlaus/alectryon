import os
import requests


def send_data(temp_cpu: float, usv: dict | None) -> None:
    api_url = os.getenv("API_URL")
    api_key = os.getenv("API_KEY")

    payload = {"temp_cpu": round(temp_cpu, 2)}
    if usv:
        payload.update(usv)

    response = requests.post(
        api_url,
        json=payload,
        headers={"Authorization": f"Bearer {api_key}"},
        timeout=10,
    )
    response.raise_for_status()
