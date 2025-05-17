from typing import List
import lib.common as cm
from pathlib import Path


def read_template(name):
    with open(f"{cm.scriptDir}/templates/{name}", "r") as file:
        content = file.read()
    return content


def mkFooter(script: str, embeddedHtmlFiles: List[str], sharedScriptFiles: List[str]):
    return (
        "".join(map(lambda x: f'<script src="{x}"></script>\n', sharedScriptFiles))
        + "".join(map(read_template, embeddedHtmlFiles))
        + f"<script>\n{script}\n</script>"
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
    displayInfo = "" if infoHidden else ' style="display: none"'
    return f"""
{{{{FrontSide}}}}
<br />
<div id="backside">
  <hr id="answer" />
  {answer}
  <div id="info"{displayInfo}>{info}</div>
</div>
{footer}
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

audioElement = """<div>{{Audio}}</div>"""
pinyinElement = """<span id="pinyin">{{Pinyin}}</span>"""
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
            "config.js",
            "libs/hanzi-writer.js",
            "libs/separate-pinyin-in-syllables.js",
        ]
        self.sharedScriptFiles = []
        self.infoElement = infoElement
        self.colorPinyin = colorPinyin
        for scriptPath in scriptPaths:
            absolutePath = f"{cm.scriptDir}/templates/common/{scriptPath}"
            name = "_" + cm.cleaned_filename(deckName) + "_" + Path(absolutePath).name
            mediaColl.add(
                src=absolutePath,
                name=name,
            )
            self.sharedScriptFiles.append(name)

    def template1(self):
        return {
            "name": "Zh→Mn+Pin",
            "qfmt": mkFrontside(
                question=f"""
{idElement}
<div id="characters-target-div" style="display: block"></div>
""",
                script="""
var isBack = document.getElementById("back-indicator") !== null;
initializeCharsTarget(`{{Chinese}}`, `{{Pinyin}}`, isBack);
""",
                embeddedHtmlFiles=["common/common.html"],
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
                script="""initializeCharsTargetQuiz(`{{Chinese}}`, `{{Pinyin}}`, true, true);\n"""
                + (
                    """colorPinyinSentenceElement(`{{Example sentence pinyin}}`);"""
                    if self.colorPinyin
                    else ""
                ),
                embeddedHtmlFiles=["common/backside.html", "common/common.html"],
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
                embeddedHtmlFiles=["common/common.html"],
                sharedScriptFiles=self.sharedScriptFiles,
            ),
            "afmt": mkBackside(
                answer=f"""
{audioElement}
{pinyinElement}
<br />
{quizElement}
""",
                script="""initializeCharsTargetQuiz(`{{Chinese}}`, `{{Pinyin}}`, false, true);\n"""
                + (
                    """colorPinyinSentenceElement(`{{Example sentence pinyin}}`);"""
                    if self.colorPinyin
                    else ""
                ),
                embeddedHtmlFiles=["common/backside.html", "common/common.html"],
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
                script=""" """,
                embeddedHtmlFiles=["common/common.html"],
                sharedScriptFiles=self.sharedScriptFiles,
            ),
            "afmt": mkBackside(
                answer=f"""
{audioElement}
{meaningElement}
{quizElement}
""",
                script="""initializeCharsTargetQuiz(`{{Chinese}}`, `{{Pinyin}}`, false, true);\n"""
                + (
                    """colorPinyinSentenceElement(`{{Example sentence pinyin}}`);"""
                    if self.colorPinyin
                    else ""
                ),
                embeddedHtmlFiles=["common/backside.html", "common/common.html"],
                sharedScriptFiles=self.sharedScriptFiles,
                info=self.infoElement,
                infoHidden=True,
            ),
        }
