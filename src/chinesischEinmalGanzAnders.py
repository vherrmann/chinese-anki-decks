import os
from lib.construct import construct_deck
from lib.extract import extract_data
from lib.config import Config
from lib.mediaCollector import MediaCollector
import lib.common as cm
import genanki as ga
import csv

deckName = "Chinesisch einmal ganz anders 1-2 + ε"

dataFile = "Chinesisch_einmal_ganz_anders_Band_1.apkg"


def noteToSubDeck(note):
    min_book = min(
        map(lambda s: int(s[1:]), filter(lambda s: s.startswith("B"), note.tags))
    )
    min_chap = min(
        map(lambda s: int(s[1:]), filter(lambda s: s.startswith("C"), note.tags))
    )
    categoryTags = {
        "lek": "Lektionstexte",
        "üb": "Übungen",
        "zu": "Zusamm. Übungen",
        "gr": "Grundwortschatz",
        "wi": "Wiederholung",
    }
    categoryTag = None
    for tag in note.tags:
        if tag in categoryTags:
            categoryTag = categoryTags[tag]
            break

    return f"B{min_book}::C{min_chap:02d}" + (f"::{categoryTag}" if categoryTag else "")


config = Config(
    {
        "modelId": 1437479615,  # import random; random.randrange(1 << 30, 1 << 31)
        "deckId": 1162970673,  # import random; random.randrange(1 << 30, 1 << 31)
        "deckName": deckName,
        "deckDescription": "See also https://valentin-herrmann.de/p/my-anki-decks-for-learning-chinese/.",
        "modelName": deckName,
        "locale": "zh-TW",
        "meaningLanguage": "Deutsch",
        "usePrevPinyin": False,
        "usePrevGUID": False,
        "convertToTraditional": True,
        "genExampleSentence": True,
        "noteToSubdeck": noteToSubDeck,
    }
)


def fixData(rawNote):
    def replaceInFlds(id, fn):
        if rawNote["id"] == id:
            print(f"Fixing note {id} in deck {deckName}")
            flds = rawNote["flds"]
            for i in range(len(flds)):
                flds[i] = fn(flds[i])

    rawNote["flds"] = list(map(lambda x: x.replace("&nbsp;", ""), rawNote["flds"]))
    replaceInFlds(1521400358687, lambda x: x.replace("注意", "主意"))
    replaceInFlds(1521581889904, lambda x: x.replace("工事", "公事"))
    replaceInFlds(1521582973765, lambda x: x.replace("Resiebüro", "Reisebüro"))
    replaceInFlds(1521589713430, lambda x: x.replace("櫃台", "櫃檯"))


scriptDir = os.path.dirname(__file__)

with MediaCollector() as mediaColl:
    dataDir = scriptDir + "/../data/"
    data_band1 = extract_data(
        pkgPath=dataDir + dataFile, mediaColl=mediaColl, collectionAnki21p=False
    )
    rawNotes_band1 = data_band1["notes"]
    rawNotes = []
    for rawNote in rawNotes_band1:
        fixData(rawNote)
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
        rawNote["flds"][2] = fixedPinyin
        chapTags = list(
            map(lambda x: "C" + x, filter(lambda s: s.isdigit(), rawNote["tags"]))
        )
        rawNote["tags"] = ["B1"] + chapTags

        rawNotes.append(rawNote)

    maxDueness = max(map(lambda x: x["due"], rawNotes))
    rawNotes_band2 = []
    with open(
        dataDir + "Chinesisch_einmal_ganz_anders_Band_2_vocab_extracted_merged.csv",
        encoding="utf-8",
    ) as csvfile:
        csvreader = csv.reader(csvfile, delimiter=",", quotechar='"')
        next(csvreader)
        for i, row in enumerate(csvreader):
            rawNote = {
                "guid": ga.guid_for(str(config.get("deckId")) + "band2" + str(i)),
                "due": maxDueness + i + 1,
                "tags": ["B2", "C" + row[0], row[1]],
                "flds": [row[3], row[5], row[4]],
            }
            rawNotes_band2.append(rawNote)
    rawNotes = rawNotes + rawNotes_band2
    notes = []
    for rawNote in rawNotes:
        notes.append(
            {
                "guid": rawNote["guid"],
                "due": rawNote["due"],
                "tags": rawNote["tags"],
                "chinese": rawNote["flds"][0],
                "meaning": rawNote["flds"][1],
                "pos": "",
                "pinyin": rawNote["flds"][2],
            }
        )

    construct_deck(
        config=config,
        notes=notes,
        mediaColl=mediaColl,
    )
    # TODO: remove &nbsp; from hanzi
