import os
from lib.construct import construct_deck
from lib.extract import extract_data
from lib.config import Config
from lib.mediaCollector import MediaCollector
import lib.common as cm
from lib.templates import Templates
import tempfile
import re

deckName = "All 214 Chinese Radicals + ε"

dataFile = "All_214_Chinese_Radicals.apkg"


scriptDir = os.path.dirname(__file__)
dataDir = scriptDir + "/../data/"


def templateTransformer(tmp):
    return tmp.replace("colorPinyinSentenceElement(`{{Example sentence pinyin}}`)", "")


with MediaCollector() as mediaColl:
    data = extract_data(
        pkgPath=dataDir + dataFile, mediaColl=mediaColl, collectionAnki21p=True
    )

    examplesElement = """
    <h3>Examples:</h3>
    {{Examples}}
    """
    templates = Templates(
        deckName, mediaColl, infoElement=examplesElement, colorPinyin=False
    )
    notes = []

    # We have to do many compromises here for backward compatibility
    # with my previous generated deck.
    # We therefore have to use the original modelId, deckId and the previous guids of the notes,
    # otherwise importing the deck to update the old one won't work.
    config = Config(
        {
            "modelId": 1729464388,
            "deckId": 1919351979,
            "deckName": deckName,
            "modelName": deckName,
            "locale": "zh-TW",
            "meaningLanguage": "English",
            "usePrevPinyin": True,
            "usePrevGUID": True,
            "traditionalSource": True,
            "genExampleSentence": False,
            "additionalFields?": ["Examples"],
            "templates?": templates,
        }
    )

    rawNotes = data["notes"]
    for rawNote in rawNotes:
        notes.append(
            {
                "guid": rawNote["guid"],
                "due": rawNote["due"],
                "tags": rawNote["tags"],
                "chinese": rawNote["flds"][0],
                "meaning": rawNote["flds"][3],
                "pinyin": rawNote["flds"][2],
                "additionalFields": [rawNote["flds"][4]],
            }
        )

    construct_deck(
        config=config,
        notes=notes,
        mediaColl=mediaColl,
    )
