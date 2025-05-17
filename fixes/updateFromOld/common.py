import json
import requests

ANKI_CONNECT_URL = "http://localhost:8765"


def anki_request(action, **params):
    """Helper function to send a request to AnkiConnect."""
    request_data = {"action": action, "version": 6, "params": params}

    response = requests.post(ANKI_CONNECT_URL, json=request_data)

    if response.status_code == 200:
        return response.json()["result"]
    else:
        raise Exception(
            f"AnkiConnect request failed with status code {response.statui_code}"
        )
