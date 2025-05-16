import os
from lib.construct import construct_deck
from lib.extract import extract_data
from lib.config import Config
from lib.mediaCollector import MediaCollector
import lib.common as cm
import tempfile
import re

deckName = "Practical Audio Visual Chinese Book 1-4 + ε"

dataFile = "PAVC_1234_VocabularyGrammar_ReadingWriting.apkg"


scriptDir = os.path.dirname(__file__)
dataDir = scriptDir + "/../data/"


def fixData(rawNote):
    def replaceInFlds(id, fn):
        if rawNote["id"] == id:
            for fld in rawNote["flds"]:
                fld = fn(fld)

    replaceInFlds(1491714927757, lambda x: x.replace("physicaly", "physically"))
    replaceInFlds(1491714927781, lambda x: x.replace("usualy", "usually"))


with MediaCollector() as mediaColl:
    data = extract_data(
        pkgPath=dataDir + dataFile, mediaColl=mediaColl, collectionAnki21p=False
    )
    notes = []

    # We have to do many compromises here for backward compatibility
    # with my previous generated deck.
    # We therefore have to use the original modelId, deckId and the previous guids of the notes,
    # otherwise importing the deck to update the old one won't work.
    config = Config(
        {
            "modelId": 1744143233,
            "deckId": 1753430173,
            "deckName": deckName,
            "modelName": deckName,
            "locale": "zh-TW",
            "meaningLanguage": "English",
            "usePrevPinyin": False,  # FIXME: change
            "usePrevGUID": True,
            "traditionalSource": True,
        }
    )

    rawNotes = data["notes"]
    for rawNote in rawNotes:
        # FIXME: allow additional fields
        tags = rawNote["tags"]
        # Grammar doesn't work with the assumptions about cards
        # this deck makes
        if "Grammar" in tags:
            continue
        fixData(rawNote)
        notes.append(
            {
                "id": rawNote["flds"][0],
                "guid": rawNote["guid"],
                "due": rawNote["due"],
                "tags": tags,
                "chinese": rawNote["flds"][1],
                "meaning": rawNote["flds"][3],
                "pinyin": rawNote["flds"][2],
            }
        )

    construct_deck(
        config=config,
        notes=notes,
        mediaColl=mediaColl,
    )
