import genanki as ga
import os

import base64
from pathlib import Path
from gtts import gTTS
import urllib.request
import shutil
import glob
import json
import lib.common as cm
from lib.pinyin import cached_to_pinyin_gpt, to_pinyin_basic, color_pinyin
from lib.exampleSentences import createExampleSentences
from lib.config import Config


def read_template(name):
    with open(f"{cm.scriptDir}/templates/{name}", "r") as file:
        content = file.read()
    return content


def get_template(cardn, frontsidep):
    cm_config = read_template("common/config.html")
    cm_hanzi_writer = read_template("common/libs/hanzi-writer.html")
    cm_common = read_template("common/common.html")
    side = "frontside" if frontsidep else "backside"
    cm_side = read_template(f"common/{side}.html")
    card_side = read_template(f"card{cardn}/{side}.html")
    return cm_config + cm_hanzi_writer + cm_common + cm_side + card_side


def gen_sound(config, hanzi):
    ttsCacheDir = cm.cacheDir(config) + "/tts/"
    locale = config.get("locale")
    deckName = config.get("deckName")
    cm.mkdirp(ttsCacheDir)

    charEnc = base64.urlsafe_b64encode(hanzi.encode()).decode()
    localeEnc = base64.urlsafe_b64encode(locale.encode()).decode()
    name = f"{deckName}_{localeEnc}_{charEnc}.mp3"
    audioPath = ttsCacheDir + "/" + name

    if not os.path.isfile(audioPath) or cm.fileEmptyP(audioPath):
        print(f"Generating sound for {hanzi} in {locale}")
        tts = gTTS(hanzi, lang=locale)
        tts.save(audioPath)

    return {"name": name, "path": audioPath}


def add_hanzi_writer_data(config, pkg):
    print("[[Adding hanzi writer data]]")
    hanziWriterDataCache = cm.cacheDir(config) + "/hanzi-writer-data.zip"

    if not os.path.isfile(hanziWriterDataCache) or cm.fileEmptyP(hanziWriterDataCache):
        urllib.request.urlretrieve(
            "https://github.com/chanind/hanzi-writer-data/archive/refs/tags/v2.0.1.zip",
            hanziWriterDataCache,
        )

    cacheDir = cm.cacheDir(config) + "/hanzi-writer-data/"
    cm.mkdirp(cacheDir)

    shutil.unpack_archive(hanziWriterDataCache, extract_dir=cacheDir, format="zip")
    dataDir = cacheDir + "/hanzi-writer-data-2.0.1/data/"
    Path.unlink(dataDir + "all.json")  # We don't want all.json in collection.media

    finalDir = cacheDir + "/final/"
    cm.mkdirp(finalDir)
    media_files = []
    charsJson = []
    for filename in glob.iglob(f"{dataDir}/*"):  # iterate over files
        new_filename = f"{finalDir}/_hanzi_writer_{os.path.basename(filename)}"
        os.replace(filename, new_filename)
        media_files.append(new_filename)
        charsJson.append(Path(filename).stem)

    hanziList = f"{finalDir}/_hanzi_writer_list.json"
    with open(hanziList, encoding="UTF8", mode="w") as fp:
        json.dump(charsJson, fp)
    media_files.append(hanziList)
    pkg.media_files = pkg.media_files + media_files


class MyNote(ga.Note):
    def __init__(self, deckId, guid, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.oldGuid = guid
        self.deckId = deckId

    @property
    def guid(self):
        return ga.guid_for(self.oldGuid + str(self.deckId))


modelCSS = """
.card {
font-family: arial;
font-size: 20px;
text-align: center;
color: black;
background-color: white;
}

# from https://github.com/jiru/ccc/blob/main/tmpl.css
.tone-1 { color: #e30000; }
.tone-2 { color: #02b31c; }
.tone-3 { color: #1510f0; }
.tone-4 { color: #8900bf; }
.tone-5 { color: #777777; }

.card.nightMode .tone { }
.card.nightMode .tone-1 { color: #ff8080; }
.card.nightMode .tone-2 { color: #80ff80; }
.card.nightMode .tone-3 { color: #8080ff; }
.card.nightMode .tone-4 { color: #df80ff; }
.card.nightMode .tone-5 { color: #c6c6c6; }

.mobile .quizButton {
    border-radius: 50%;
    width: 3em;
    height: 3em;

    margin: 1em 0.5em;
    font-family: "Sans Serif", sans-serif;
    outline: none !important;
}
"""


def construct_deck(config: Config, notes):
    my_model = ga.Model(
        model_id=config.get("modelId"),
        name=config.get("modelName"),
        css=modelCSS,
        fields=[
            {"name": "Chinese", "excludeFromSearch": False},
            {"name": "Pinyin", "excludeFromSearch": False},
            {"name": "Meaning", "excludeFromSearch": False},
            {"name": "Audio", "excludeFromSearch": True},
            {"name": "Example sentence chinese", "excludeFromSearch": True},
            {"name": "Example sentence translation", "excludeFromSearch": True},
            {"name": "Example sentence pinyin", "excludeFromSearch": True},
        ],
        templates=[
            {
                "name": "Zh→Mn+Pin",
                "qfmt": get_template(1, True),
                "afmt": get_template(1, False),
            },
            {
                "name": "Mn→Pin+Zh",
                "qfmt": get_template(2, True),
                "afmt": get_template(2, False),
            },
            {
                "name": "Pin→Zh+Mn",
                "qfmt": get_template(3, True),
                "afmt": get_template(3, False),
            },
        ],
    )

    notes = cm.nodubBy(notes, lambda x: (x["chinese"], x["meaning"]))

    exSentences = createExampleSentences(config=config, notes=notes)

    my_deck = ga.Deck(config.get("deckId"), config.get("deckName"))

    # There are some duplicated entries in the notes, so we remove them
    # We use chinese + meaning for the key and not only chinese since
    # there are notes that have the same chinese but different meaning, e.g. 還
    media_files = []
    for note in notes:
        chinese = note["chinese"]
        meaning = note["meaning"]
        # FIXME: use cached_to_pinyin_gpt
        pinyin = color_pinyin(
            to_pinyin_basic(
                # deckName=deckName,
                # locale=locale,
                chinese,
                # meaning=meaning,
                # previousPinyin=note["pinyin"],
            )
        )

        # FIXME:
        # audioRes = gen_sound(config=config, hanzi=note["chinese"])
        # media_files.append(audioRes["path"])

        audio = ""  # f"[sound:{audioRes['name']}]"
        exampleSentence = exSentences["chinese"][cm.noteDictKey(note)]
        translatedSentence = exSentences["translated"][cm.noteDictKey(note)]
        exampleSentencePinyin = color_pinyin(
            exSentences["pinyin"][cm.noteDictKey(note)]
        )
        # TODO: preserve tags

        my_note = MyNote(
            deckId=config.get("deckId"),
            guid=note["guid"],
            due=note["due"],
            tags=note["tags"],
            model=my_model,
            fields=[
                chinese,
                pinyin,
                meaning,
                audio,
                exampleSentence,
                translatedSentence,
                exampleSentencePinyin,
            ],
        )
        my_deck.add_note(my_note)

    pkg = ga.Package(my_deck)
    pkg.media_files = media_files
    add_hanzi_writer_data(config, pkg)

    pkg.write_to_file("/tmp/output.apkg")
