import os
from lib.construct import construct_deck
from lib.extract import extract_data
from lib.config import Config
from lib.mediaCollector import MediaCollector
import lib.common as cm
import tempfile
import re
import sys

convertToTraditional = "--simplified" not in sys.argv

if convertToTraditional:
    deckName = f"Chinesisch für Deutsche Buch 1-2 + ε"
else:
    deckName = f"Chinesisch für Deutsche Buch 1-2 + ε (Simplified)"

dataFile = f"Chinesisch_für_Deutsche_1+2.apkg"


scriptDir = os.path.dirname(__file__)
dataDir = scriptDir + "/../data/"


def translate_tags(tags):
    new_tags = []
    for tag in tags:
        b1 = re.match(r"(\d+)", tag)
        b2 = re.match(r"B(\d+)", tag)
        if b1 is not None:
            new_tags += ["B1", "C" + b1.group(1)]
        elif b2 is not None:
            new_tags += ["B2", "C" + b2.group(1)]
        else:
            new_tags += [tag]
    return list(set(new_tags))


def fixData(rawNote):
    def replaceInFlds(id, fn):
        if rawNote["id"] == id:
            flds = rawNote["flds"]
            for i in range(len(flds)):
                flds[i] = fn(flds[i])

    replaceInFlds(1253233319640, lambda x: x.replace("zuòtiān", "zuótiān"))
    replaceInFlds(1252888453500, lambda x: x.replace("chuānghu", "chuānghù"))


def noteToSubDeck(note):
    if "extra" in note.tags:
        return "Extra"
    bTags = list(filter(lambda s: s.startswith("B"), note.tags))
    cTags = list(filter(lambda s: s.startswith("C"), note.tags))
    min_b = min(map(int, map(lambda s: s[1:], bTags)))
    min_c = min(map(int, map(lambda s: s[1:], cTags)))

    return f"B{min_b:01d}::C{min_c:02d}"


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
            "modelId": 1553102416,
            "deckId": 1827575035,
            "deckName": deckName,
            "deckDescription": "See also https://valentin-herrmann.de/p/my-anki-decks-for-learning-chinese/.",
            "modelName": deckName,
            "locale": "zh-TW" if convertToTraditional else "zh-CN",
            "meaningLanguage": "Deutsch",
            "usePrevPinyin": True,
            "usePrevGUID": True,
            "convertToTraditional": not convertToTraditional,
            "genExampleSentence": True,
            "noteToSubdeck": noteToSubDeck,
        }
    )

    rawNotes = data["notes"]
    rawNotes.append(
        {
            "id": 0,
            "flds": ["林", "Lín", "1) Wald\n2) Lin\nchin. Familienname"],
            "guid": "b}C@}(GVIb",
            "tags": ["extra"],
            "due": 0,
        }
    )
    for rawNote in rawNotes:
        # FIXME: allow additional fields
        fixData(rawNote)
        notes.append(
            {
                "guid": rawNote["guid"],
                "due": rawNote["due"],
                "tags": translate_tags(rawNote["tags"]),
                "chinese": rawNote["flds"][0],
                "meaning": rawNote["flds"][2],
                "pinyin": rawNote["flds"][1],
            }
        )

    construct_deck(
        config=config,
        notes=notes,
        mediaColl=mediaColl,
    )
