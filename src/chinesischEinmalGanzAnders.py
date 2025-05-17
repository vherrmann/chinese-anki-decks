import os
from lib.construct import construct_deck
from lib.extract import extract_data
from lib.config import Config
from lib.mediaCollector import MediaCollector
import lib.common as cm
import re

deckName = "Chinesisch einmal ganz anders 1 + ε"

dataFile = "Chinesisch_einmal_ganz_anders_Band_1.apkg"

config = Config(
    {
        "modelId": 1437479615,  # import random; random.randrange(1 << 30, 1 << 31)
        "deckId": 1162970673,  # import random; random.randrange(1 << 30, 1 << 31)
        "deckName": deckName,
        "modelName": deckName,
        "locale": "zh-TW",
        "meaningLanguage": "Deutsch",
        "usePrevPinyin": False,
        "usePrevGUID": False,
        "traditionalSource": True,
        "genExampleSentence": True,
    }
)


scriptDir = os.path.dirname(__file__)

with MediaCollector() as mediaColl:
    dataDir = scriptDir + "/../data/"
    data = extract_data(
        pkgPath=dataDir + dataFile, mediaColl=mediaColl, collectionAnki21p=False
    )
    rawNotes = data["notes"]
    notes = []
    for rawNote in rawNotes:
        # pos and meaning are in the original meaning field
        prevMeaning = rawNote["flds"][1]
        meaningMatch = re.match(r"\((.+)\) (.+)", prevMeaning)
        if meaningMatch is None:
            pos = ""
            meaning = prevMeaning
        else:
            pos = meaningMatch.group(1)
            meaning = meaningMatch.group(2)
        # clean html from pinyin
        cleanedPinyin = cm.cleanHtml(rawNote["flds"][2])
        # fix common mistake in prev. deck
        fixedPinyin = (
            cleanedPinyin.replace("ǐu", "iǔ")
            .replace("ìu", "iù")
            .replace("íu", "iú")
            .replace("ío", "ió")
            .replace("īu", "iū")
        )
        notes.append(
            {
                "guid": rawNote["guid"],
                "due": rawNote["due"],
                "tags": rawNote["tags"],
                "chinese": rawNote["flds"][0],
                "meaning": meaning,
                "pos": pos,
                "pinyin": fixedPinyin,
            }
        )

    construct_deck(
        config=config,
        notes=notes,
        mediaColl=mediaColl,
    )
    # TODO: remove &nbsp; from hanzi
