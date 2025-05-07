import json
import requests

# URL for AnkiConnect
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


def rename_templates_by_model(model_name, template_name_map):
    for oldName, newName in template_name_map.items():
        anki_request(
            "modelTemplateRename",
            modelName=model_name,
            oldTemplateName=oldName,
            newTemplateName=newName,
        )


rename_templates_by_model(
    "A Course in Contemporary Chinese with Hanzi Writer/Sound",
    {
        "Zh→En+Pin": "Zh→Mn+Pin",
        "En→Pin+Zh": "Mn→Pin+Zh",
        "Pin→Zh+En": "Pin→Zh+Mn",
    },
)
