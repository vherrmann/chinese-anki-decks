import lib.common as cm
import genanki as ga
import shutil
from pathlib import Path

modelCSS = """
.card {
    font-family: arial;
    font-size: 20px;
    text-align: center;
    color: black;
    background-color: white;
}

.mobile .quizButton {
    border-radius: 50%;
    width: 3em;
    height: 3em;

    margin: 1em 0.5em;
    font-family: "Sans Serif", sans-serif;
    outline: none !important;
}
"""


def read_template(name):
    with open(f"{cm.scriptDir}/templates/{name}", "r") as file:
        content = file.read()
    return content


class TemplateGen:
    def __init__(self, config, mediaColl):
        deckName = config.get("deckName")
        scriptPaths = [
            "config.js",
            "libs/hanzi-writer.js",
            "libs/separate-pinyin-in-syllables.js",
        ]
        self.scriptNames = []
        self.templateTransformer = config.get("templateTransformer", lambda x: x)
        for scriptPath in scriptPaths:
            absolutePath = f"{cm.scriptDir}/templates/common/{scriptPath}"
            name = "_" + cm.cleaned_filename(deckName) + "_" + Path(absolutePath).name
            mediaColl.add(
                src=absolutePath,
                name=name,
            )
            self.scriptNames.append(name)

    def get_template(self, cardn, frontsidep):
        includes = "".join(
            map(lambda x: f'<script src="{x}"></script>\n', self.scriptNames)
        )
        side = "frontside" if frontsidep else "backside"
        if frontsidep:
            cm_side = ""
        else:
            cm_side = read_template(f"common/backside.html")
        cm_common = read_template(f"common/common.html")
        card_side = read_template(f"card{cardn}/{side}.html")
        return self.templateTransformer(includes + cm_side + cm_common + card_side)


def generate_model(config, mediaColl):
    tGen = TemplateGen(config, mediaColl)
    additionalFields = config.get("additionalFields?", [])
    return ga.Model(
        model_id=config.get("modelId"),
        name=config.get("modelName"),
        css=modelCSS,
        fields=[
            {"name": "ID", "excludeFromSearch": False},
            {"name": "Chinese", "excludeFromSearch": False},
            {"name": "Pinyin", "excludeFromSearch": False},
            {"name": "Meaning", "excludeFromSearch": False},
            {"name": "POS", "excludeFromSearch": True},
            {"name": "Audio", "excludeFromSearch": True},
            {"name": "Example sentence chinese", "excludeFromSearch": True},
            {"name": "Example sentence translation", "excludeFromSearch": True},
            {"name": "Example sentence pinyin", "excludeFromSearch": True},
        ]
        + list(map(lambda x: {"name": x, "excludeFromSearch": True}, additionalFields)),
        templates=[
            {
                "name": "Zh→Mn+Pin",
                "qfmt": tGen.get_template(1, True),
                "afmt": tGen.get_template(1, False),
            },
            {
                "name": "Mn→Pin+Zh",
                "qfmt": tGen.get_template(2, True),
                "afmt": tGen.get_template(2, False),
            },
            {
                "name": "Pin→Zh+Mn",
                "qfmt": tGen.get_template(3, True),
                "afmt": tGen.get_template(3, False),
            },
        ],
    )
