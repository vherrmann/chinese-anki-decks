from typing import List
import lib.common as cm
from pathlib import Path
import json


def read_template(name):
    with open(f"{cm.scriptDir}/templates/{name}", "r") as file:
        content = file.read()
    return content


def mkFooter(script: str, embeddedHtmlFiles: List[str], sharedScriptFiles: List[str]):
    importmap = {"imports": dict(map(lambda x: (x[0], f"./{x[1]}"), sharedScriptFiles))}
    return (
        f"""<script type="importmap">{json.dumps(importmap)}</script>\n"""
        + "".join(
            map(
                lambda x: f'<script type="module" src="{x[1]}"></script>\n',
                sharedScriptFiles,
            )
        )
        + "".join(map(read_template, embeddedHtmlFiles))
        + f"""<script type="module">\n{script}\n</script>"""
    )


def mkBackside(
    answer: str,
    script: str,
    embeddedHtmlFiles: List[str],
    sharedScriptFiles: List[str],
    info: str,
    infoHidden: bool = False,
):
    footer = mkFooter(
        script=script,
        embeddedHtmlFiles=embeddedHtmlFiles,
        sharedScriptFiles=sharedScriptFiles,
    )
    displayInfo = "" if infoHidden else 'style="display: none"'
    return f"""
{{{{FrontSide}}}}
<br />
<div id="backside">
  <hr id="answer" />
  {answer}
  <div id="info" {displayInfo}>{info}</div>
</div>
{footer}
<div id="back-indicator" style="display: none">
  <!-- Can be used in js to check if we are on the front or back -->
</div>
"""


def mkFrontside(
    question: str,
    script: str,
    embeddedHtmlFiles: List[str],
    sharedScriptFiles: List[str],
):
    footer = mkFooter(
        script=script,
        embeddedHtmlFiles=embeddedHtmlFiles,
        sharedScriptFiles=sharedScriptFiles,
    )
    return f"""
{question}
{footer}
"""


idElement = (
    """<div class="termid" style="font-size: 8px; color: #8882">({{ID}})</div>"""
)
chineseElement = """<span class="chinese">{{Chinese}}</span>"""
audioElement = """<div>{{Audio}}</div>"""
pinyinElement = """{{Pinyin}}"""
meaningElement = """<span>{{#POS}}({{POS}}){{/POS}} {{Meaning}}</span>"""
quizElement = """<div id="characters-target-div-quiz"></div>"""
exampleSentenceElement = """
<h3>Example sentence:</h3>
{{Example sentence chinese}}
<br />
<span id="exampleSentencePinyin">{{Example sentence pinyin}}</span>
<br />
{{Example sentence translation}}
<div />
"""


class Templates:
    def __init__(
        self, deckName, mediaColl, infoElement=exampleSentenceElement, colorPinyin=True
    ):
        scriptPaths = [
            ("Config", "config.js"),
            ("AnkiHanziQuiz", "libs/anki-hanzi-quiz.js"),
            ("SepPinyin", "libs/separate-pinyin-in-syllables.js"),
            ("Common", "common.js"),
            ("Backside", "backside.js"),  # FIXME: only include on backside
        ]
        self.stylePaths = ["libs/anki-hanzi-quiz.css"]  # TODO
        self.infoElement = infoElement
        self.colorPinyin = colorPinyin
        self.sharedScriptFiles = []
        for moduleName, scriptPath in scriptPaths:
            absolutePath = f"{cm.scriptDir}/templates/{scriptPath}"
            name = "_" + cm.cleaned_filename(deckName) + "_" + Path(absolutePath).name
            mediaColl.add(
                src=absolutePath,
                name=name,
            )
            self.sharedScriptFiles.append((moduleName, name))

    def getTemplateCSS(self):
        return "".join(map(lambda x: read_template(x) + "\n", self.stylePaths))

    def template1(self):
        return {
            "name": "Zh→Mn+Pin",
            "qfmt": mkFrontside(
                question=f"""
{idElement}
{chineseElement}
""",
                script="",
                embeddedHtmlFiles=[],
                sharedScriptFiles=self.sharedScriptFiles,
            ),
            "afmt": mkBackside(
                answer=f"""
{audioElement}
{pinyinElement}
<br />
{meaningElement}
{quizElement}
""",
                script="""
                import * as Backside from 'Backside';
                import * as Common from 'Common';
                Backside.initializeCharsTargetQuiz(`{{Chinese}}`, `{{Pinyin}}`, true, true);\n"""
                + (
                    """Common.colorPinyinSentenceElement(`{{Example sentence pinyin}}`);"""
                    if self.colorPinyin
                    else ""
                ),
                embeddedHtmlFiles=[],
                sharedScriptFiles=self.sharedScriptFiles,
                info=self.infoElement,
            ),
        }

    def template2(self):
        return {
            "name": "Mn→Pin+Zh",
            "qfmt": mkFrontside(
                question=f"""
{idElement}
{meaningElement}
""",
                script="",
                embeddedHtmlFiles=[],
                sharedScriptFiles=self.sharedScriptFiles,
            ),
            "afmt": mkBackside(
                answer=f"""
{audioElement}
{pinyinElement}
<br />
{quizElement}
""",
                script="""
                import * as Backside from 'Backside';
                import * as Common from 'Common';
                Backside.initializeCharsTargetQuiz(`{{Chinese}}`, `{{Pinyin}}`, false, true);\n
                """
                + (
                    """Common.colorPinyinSentenceElement(`{{Example sentence pinyin}}`);"""
                    if self.colorPinyin
                    else ""
                ),
                embeddedHtmlFiles=[],
                sharedScriptFiles=self.sharedScriptFiles,
                info=self.infoElement,
                infoHidden=True,
            ),
        }

    def template3(self):
        return {
            "name": "Pin→Zh+Mn",
            "qfmt": mkFrontside(
                question=f"""
{idElement}
{pinyinElement}
""",
                script="",
                embeddedHtmlFiles=[],
                sharedScriptFiles=self.sharedScriptFiles,
            ),
            "afmt": mkBackside(
                answer=f"""
{audioElement}
{meaningElement}
{quizElement}
""",
                script="""
                import * as Backside from 'Backside';
                import * as Common from 'Common';
                Backside.initializeCharsTargetQuiz(`{{Chinese}}`, `{{Pinyin}}`, false, true);\n"""
                + (
                    """Common.colorPinyinSentenceElement(`{{Example sentence pinyin}}`);"""
                    if self.colorPinyin
                    else ""
                ),
                embeddedHtmlFiles=[],
                sharedScriptFiles=self.sharedScriptFiles,
                info=self.infoElement,
                infoHidden=True,
            ),
        }
