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

.chinese {
    font-family: Source Han Sans, SimSun;
    font-size: 80px;
    vertical-align: 20px;
}
"""


def generate_model(config, mediaColl):
    additionalFields = config.get("additionalFields?", [])
    templates = config.get("templates?", Templates(config.get("deckName"), mediaColl))
    return ga.Model(
        model_id=config.get("modelId"),
        name=config.get("modelName"),
        css=modelCSS + "\n" + templates.getTemplateCSS(),
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
        sort_field_index=1,
        templates=[
            templates.template1(),
            templates.template2(),
            templates.template3(),
        ],
    )
