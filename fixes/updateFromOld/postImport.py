import json
import requests
from common import anki_request

# URL for AnkiConnect

stdFields = [
    "ID",
    "Chinese",
    "Pinyin",
    "Meaning",
    "POS",
    "Audio",
    "Example sentence chinese",
    "Example sentence translation",
    "Example sentence pinyin",
]


def fixupFields(model_name, additional_fields=[]):
    fields = anki_request("modelFieldNames", modelName=model_name)
    # remove superfluous_fields
    superfluous_fields = set(fields) - set(stdFields) - set(additional_fields)
    for f in superfluous_fields:
        anki_request(
            "modelFieldRemove",
            modelName=model_name,
            fieldName=f,
        )
    # reposition fields
    if not (set(stdFields).union(set(additional_fields)) <= set(fields)):
        raise Exception(
            f"Model {model_name} does not contain all required fields: {stdFields + additional_fields}\n"
            f"Previous fields: {fields}"
        )
    for i, f in enumerate(stdFields + additional_fields):
        anki_request(
            "modelFieldReposition",
            modelName=model_name,
            fieldName=f,
            index=i,
        )


fixupFields(
    "Practical Audio Visual Chinese Book 1-4 + ε",
)
fixupFields(
    "Chinesisch einmal ganz anders 1 + ε",
)

fixupFields(
    "A Course in Contemporary Chinese B1-B6 + ε",
)
fixupFields(
    "Chinesisch für Deutsche Buch 1-2 + ε",
)
fixupFields("All 214 Chinese Radicals + ε", ["Examples"])
