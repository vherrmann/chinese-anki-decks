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
from lib.pinyin import cached_to_pinyin_gpt, cached_to_pinyin_check, color_pinyin
from lib.exampleSentences import createExampleSentences
from lib.config import Config
from lib.model import generate_model


def gen_sound(config, hanzi):
    ttsCacheDir = cm.cacheDir(config) + "/tts/"
    locale = config.get("locale")
    deckName = config.get("deckName")
    cleanedDeckName = cm.cleaned_filename(deckName)
    cm.mkdirp(ttsCacheDir)

    charEnc = base64.urlsafe_b64encode(hanzi.encode()).decode()
    localeEnc = base64.urlsafe_b64encode(locale.encode()).decode()
    name = f"{cleanedDeckName}_{localeEnc}_{charEnc}.mp3"
    audioPath = ttsCacheDir + "/" + name

    if not os.path.isfile(audioPath) or cm.fileEmptyP(audioPath):
        print(f"Generating sound for {hanzi} in {locale}")
        tts = gTTS(hanzi, lang=locale)
        tts.save(audioPath)

    return {"name": name, "path": audioPath}


def add_hanzi_writer_data(config, mediaColl):
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
    charsJson = []
    for filename in glob.iglob(f"{dataDir}/*"):  # iterate over files
        new_filename = f"{finalDir}/_hanzi_writer_{os.path.basename(filename)}"
        os.replace(filename, new_filename)
        mediaColl.add(src=new_filename)
        charsJson.append(Path(filename).stem)

    hanziList = f"{finalDir}/_hanzi_writer_list.json"
    with open(hanziList, encoding="UTF8", mode="w") as fp:
        json.dump(charsJson, fp)
    mediaColl.add(src=hanziList)


class StandardNote(ga.Note):
    def __init__(self, deckId, guid, usePrevGUID, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.deckId = deckId
        self.oldGuid = guid
        self.usePrevGUID = usePrevGUID

    @property
    def guid(self):
        if self.usePrevGUID:
            return self.oldGuid
        else:
            return ga.guid_for(self.oldGuid + str(self.deckId))


def construct_deck(config: Config, notes, mediaColl):
    print("[Constructing deck]")
    standard_model = generate_model(config, mediaColl)

    notes = cm.nodubBy(notes, lambda x: (x["chinese"], x["meaning"]))

    exSentences = createExampleSentences(config=config, notes=notes)

    my_deck = ga.Deck(config.get("deckId"), config.get("deckName"))

    # There are some duplicated entries in the notes, so we remove them
    # We use chinese + meaning for the key and not only chinese since
    # there are notes that have the same chinese but different meaning, e.g. 還
    for note in notes:
        idField = note.get("idField", "")
        chinese = note["chinese"]
        meaning = note["meaning"]
        pos = note.get("pos", "")

        if config.get("usePrevPinyin"):
            pinyin = note["pinyin"]
        else:
            pinyin = cached_to_pinyin_gpt(
                config=config,
                hanzi=chinese,
                meaning=meaning,
                meaningLanguage=config.get("meaningLanguage"),
                previousPinyin=note["pinyin"],
            )

        # Use audio of old deck if available
        if note.get("audioFile") is not None:
            mediaColl.enable(note["audioFile"])
            audio = f"[sound:{note['audioFile']}]"
        else:
            audioRes = gen_sound(config=config, hanzi=note["chinese"])
            mediaColl.add(src=audioRes["path"], name=audioRes["name"])
            audio = f"[sound:{audioRes['name']}]"

        exampleSentence = exSentences["chinese"][cm.noteDictKey(note)]
        translatedSentence = exSentences["translated"][cm.noteDictKey(note)]
        exampleSentencePinyin = exSentences["pinyin"][cm.noteDictKey(note)]

        my_note = StandardNote(
            deckId=config.get("deckId"),
            guid=note["guid"],
            due=note["due"],
            tags=note["tags"],
            model=standard_model,
            fields=[
                idField,
                chinese,
                pinyin,
                meaning,
                pos,
                audio,
                exampleSentence,
                translatedSentence,
                exampleSentencePinyin,
            ],
            usePrevGUID=config.get("usePrevGUID"),
        )
        print(f"[[Adding note: {chinese}]]")
        my_deck.add_note(my_note)

    add_hanzi_writer_data(config=config, mediaColl=mediaColl)

    pkg = ga.Package(my_deck)
    pkg.media_files = mediaColl.get_media()

    resCacheFile = cm.cacheDir(config) + "/res/" + "output.apkg"
    cm.mkdirp(os.path.dirname(resCacheFile))
    pkg.write_to_file(resCacheFile)
