import os
from lib.construct import construct_deck
from lib.extract import extract_data
from lib.config import Config
import lib.common as cm
import tempfile
import re

deckName = "A Course in Contemporary Chinese B1-B6 + ε"

dataFile = "A_Course_in_Contemporary_Chinese__B1-B6_Traditional.apkg"


scriptDir = os.path.dirname(__file__)
dataDir = scriptDir + "/../data/"

with tempfile.TemporaryDirectory() as mediaDir:
    data = extract_data(
        pkgPath=dataDir + dataFile, mediaDir=mediaDir, collectionAnki21p=True
    )
    notes = []

    # We have to do many compromises here for backward compatibility
    # with my previous generated deck.
    # We therefore have to use the original modelId, deckId and the previous guids of the notes,
    # otherwise importing the deck to update the old one won't work.
    config = Config(
        {
            "modelId": data["modelId"],
            "deckId": data["deckId"],
            "deckName": deckName,
            "modelName": deckName,
            "locale": "zh-TW",
            "meaningLanguage": "English",
            "usePrevPinyin": True,
            "usePrevGUID": True,
        }
    )

    rawNotes = data["notes"]
    for rawNote in rawNotes:
        # clean html from pinyin
        cleanedPinyin = cm.cleanHtml(rawNote["flds"][3])
        # FIXME: allow additional fields, like POS
        POS = rawNote["flds"][4]
        audioFile = re.search(r"\[sound:(.+)\]", rawNote["flds"][6]).group(1)
        notes.append(
            {
                "guid": rawNote["guid"],
                "due": rawNote["due"],
                "tags": rawNote["tags"],
                "chinese": rawNote["flds"][1],
                "meaning": (
                    f"({POS}) {rawNote["flds"][5]}" if POS != "" else rawNote["flds"][5]
                ),
                "audioFile": audioFile,
                "pinyin": cleanedPinyin,
            }
        )

    construct_deck(
        config=config,
        notes=notes,
        mediaDir=mediaDir,
    )

    # TODO: the previous deck contains simplified chinese, POS (part of speech) and an ID field
