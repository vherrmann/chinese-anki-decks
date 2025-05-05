import os
from lib.construct import construct_deck
from lib.extract import extract_data
from lib.config import Config
import lib.common as cm

deckName = "A Course in Contemporary Chinese B1-B6 + ε"

dataFile = "A_Course_in_Contemporary_Chinese__B1-B6_Traditional.apkg"


scriptDir = os.path.dirname(__file__)
dataDir = scriptDir + "/../data/"
data = extract_data(pkgPath=dataDir + dataFile, collectionAnki21p=True)
notes = []

config = Config(
    {
        "modelId": 1342696037256,
        "deckId": data["deckId"],
        "deckName": deckName,
        "modelName": deckName,
        "locale": "zh-TW",
        "meaningLanguage": "English",
    }
)

rawNotes = data["notes"]
for rawNote in rawNotes:
    # clean html from pinyin
    cleanedPinyin = cm.cleanHtml(rawNote["flds"][3])
    POS = rawNote["flds"][4]
    notes.append(
        {
            "guid": rawNote["guid"],
            "due": rawNote["due"],
            "tags": rawNote["tags"],
            "chinese": rawNote["flds"][1],
            "meaning": (
                f"({POS}) {rawNote["flds"][5]}" if POS != "" else rawNote["flds"][5]
            ),
            "pinyin": cleanedPinyin,
        }
    )

construct_deck(
    config=config,
    notes=notes,
)

# TODO: the previous deck contains simplified chinese, POS (part of speech) and an ID field
