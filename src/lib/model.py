import genanki as ga
from lib.templates import Templates

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


def generate_model(config, mediaColl):
    additionalFields = config.get("additionalFields?", [])
    templates = config.get("templates?", Templates(config.get("deckName"), mediaColl))
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
            templates.template1(),
            templates.template2(),
            templates.template3(),
        ],
    )
