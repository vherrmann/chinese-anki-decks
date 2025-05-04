import os
import re
from lib.construct import construct_deck
from lib.extract import extract_notes

deckName = "Chinesisch einmal ganz anders 1 with Hanzi"


class Config:
    __conf = {
        "modelId": 1437479615,
        "deckId": 1162970673,
        "deckName": deckName,
        "modelName": deckName,
        "locale": "zh-TW",
        "meaningLanguage": "Deutsch",
        "dataFile": "Chinesisch_einmal_ganz_anders_Band_1.apkg",
    }
    __setters = []

    @staticmethod
    def get(name):
        return Config.__conf[name]

    @staticmethod
    def set(name, value):
        if name in Config.__setters:
            Config.__conf[name] = value
        else:
            raise NameError("Name not accepted in set() method")


scriptDir = os.path.dirname(__file__)
dataDir = scriptDir + "/../data/"
rawNotes = extract_notes(dataDir + Config.get("dataFile"))
notes = []
for rawNote in rawNotes:
    # clean html from pinyin
    cleanedPinyin = re.sub(r"<.*?>", "", rawNote["flds"][2])
    notes.append(
        {
            "guid": rawNote["guid"],
            "due": rawNote["due"],
            "tags": rawNote["tags"],
            "chinese": rawNote["flds"][0],
            "meaning": rawNote["flds"][1],
            "pinyin": cleanedPinyin,
        }
    )
construct_deck(
    config=Config,
    notes=notes,
)
