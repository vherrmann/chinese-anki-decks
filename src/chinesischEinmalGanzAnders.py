import os
from lib.construct import construct_deck
from lib.extract import extract_data
from lib.config import Config
import lib.common as cm

deckName = "Chinesisch einmal ganz anders 1 + ε"

dataFile = "Chinesisch_einmal_ganz_anders_Band_1.apkg"

config = Config(
    {
        "modelId": 1437479615,
        "deckId": 1162970673,
        "deckName": deckName,
        "modelName": deckName,
        "locale": "zh-TW",
        "meaningLanguage": "Deutsch",
    }
)


scriptDir = os.path.dirname(__file__)
dataDir = scriptDir + "/../data/"
data = extract_data(pkgPath=dataDir + dataFile, collectionAnki21p=False)
rawNotes = data["notes"]
notes = []
for rawNote in rawNotes:
    # clean html from pinyin
    cleanedPinyin = cm.cleanHtml(rawNote["flds"][2])
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
    config=config,
    notes=notes,
)
