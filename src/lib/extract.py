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


def extract_data(pkgPath, collectionAnki21p):
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
        for nid, guid, flds, tags in data:
            sep = "\u001f"  # seperats fields in database
            fldsList = flds.split(sep)
            # get dueness
            due = getDueForNote(nid, con)
            # reverse ' ' + ' '.join(self.tags) + ' '
            tagList = [x for x in tags.split(" ") if x != ""]

            # FIXME: split tags to list
            notes.append({"guid": guid, "due": due, "tags": tagList, "flds": fldsList})

        prevDecksCol = cur.execute("SELECT decks FROM col").fetchone()[0]
        prevDecksColList = list(json.loads(prevDecksCol).keys())
        prevDecksColList.remove("1")
        deckId = prevDecksColList[0]
        return {"notes": notes, "deckId": deckId}
