import os
from lib.construct import construct_deck
from lib.extract import extract_data
from lib.config import Config
from lib.mediaCollector import MediaCollector
import lib.common as cm
import tempfile
import re

deckName = "A Course in Contemporary Chinese B1-B6 + ε"

dataFile = "A_Course_in_Contemporary_Chinese__B1-B6_Traditional.apkg.zst"


scriptDir = os.path.dirname(__file__)
dataDir = scriptDir + "/../data/"

with MediaCollector() as mediaColl:
    data = extract_data(
        pkgPath=dataDir + dataFile,
        mediaColl=mediaColl,
        collectionAnki21p=True,
        decompress=True,
    )
    notes = []

    # We have to do many compromises here for backward compatibility
    # with my previous generated deck.
    # We therefore have to use the original modelId, deckId and the previous guids of the notes,
    # otherwise importing the deck to update the old one won't work.
    config = Config(
        {
            "modelId": 1085856635,
            "deckId": 2068081752,
            "deckName": deckName,
            "modelName": deckName,
            "locale": "zh-TW",
            "meaningLanguage": "English",
            "usePrevPinyin": True,
            "usePrevGUID": True,
            "traditionalSource": True,
            "genExampleSentence": True,
        }
    )

    rawNotes = data["notes"]
    for rawNote in rawNotes:
        # clean html from pinyin
        cleanedPinyin = cm.cleanHtml(rawNote["flds"][3])
        # FIXME: allow additional fields
        audioFile = re.search(r"\[sound:(.+)\]", rawNote["flds"][6]).group(1)
        notes.append(
            {
                "id": rawNote["flds"][0],
                "guid": rawNote["guid"],
                "due": rawNote["due"],
                "tags": rawNote["tags"],
                "chinese": rawNote["flds"][1],
                "meaning": rawNote["flds"][5],
                "pos": rawNote["flds"][4],
                "audioFile": audioFile,
                "pinyin": cleanedPinyin,
            }
        )

    construct_deck(
        config=config,
        notes=notes,
        mediaColl=mediaColl,
    )
