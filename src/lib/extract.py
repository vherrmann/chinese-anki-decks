import tempfile
import shutil
import sqlite3
import json


def getDueForNote(nid, con):
    cur = con.cursor()
    data = cur.execute("SELECT due FROM cards WHERE nid=?", (nid,)).fetchall()
    if len(data) == 0:
        raise Exception("No cards found for note")
    elif len(set(data)) == 1:
        due = data[0][0]
    else:
        raise Exception("Cards have different dues")
    return due


def fixDueForNotes(notes, con):
    # If due is the same for all notes, the deck was probably generated with genanki.
    # In that case we can use the normalized node id for the due value.
    if len(set(map(lambda x: x["due"], notes))) == 1:
        notesSorted = notes.copy()
        notesSorted.sort(key=lambda x: x["id"])
        for i, note in enumerate(notesSorted):
            note["due"] = i


def addMediaFiles(tmpdirname, mediaColl):
    print(f"[[Adding media files from {tmpdirname}]]")
    with open(f"{tmpdirname}/media", encoding="UTF8", mode="r") as fp:
        media = json.load(fp)
    for i, name in media.items():
        src = f"{tmpdirname}/{i}"
        mediaColl.add_disabled(src=src, name=name)


def getColInfo(con):
    cur = con.cursor()
    prevDecksCol, prevModelsCol = cur.execute(
        "SELECT decks, models FROM col"
    ).fetchone()
    prevDecksColList = list(json.loads(prevDecksCol).keys())
    prevDecksColList.remove("1")
    print(prevDecksColList)
    assert len(prevDecksColList) == 1
    deckId = int(prevDecksColList[0])

    prevModelsColList = list(json.loads(prevModelsCol).keys())
    assert len(prevModelsColList) == 1
    modelId = int(prevModelsColList[0])
    return {"deckId": deckId, "modelId": modelId}


def extract_data(pkgPath, collectionAnki21p, mediaColl):
    print(f"[Extracting data from {pkgPath}]")
    with tempfile.TemporaryDirectory() as tmpdirname:
        # list dir content
        shutil.unpack_archive(pkgPath, tmpdirname, format="zip")
        if collectionAnki21p:
            database = f"{tmpdirname}/collection.anki21"
        else:
            database = f"{tmpdirname}/collection.anki2"

        con = sqlite3.connect(database)
        cur = con.cursor()
        data = cur.execute("SELECT id, guid, flds, tags FROM notes").fetchall()
        notes = []
        for id, guid, flds, tags in data:
            sep = "\u001f"  # seperats fields in database
            fldsList = flds.split(sep)
            # get dueness
            due = getDueForNote(id, con)
            # reverse ' ' + ' '.join(self.tags) + ' '
            tagList = [x for x in tags.split(" ") if x != ""]

            notes.append(
                {"id": id, "guid": guid, "due": due, "tags": tagList, "flds": fldsList}
            )

        fixDueForNotes(notes, con)

        addMediaFiles(tmpdirname=tmpdirname, mediaColl=mediaColl)
        return {
            "notes": notes,
        }
