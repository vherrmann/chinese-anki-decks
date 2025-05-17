from common import anki_request

# URL for AnkiConnect


def rename_templates_by_model(model_name, template_name_map):
    for oldName, newName in template_name_map.items():
        anki_request(
            "modelTemplateRename",
            modelName=model_name,
            oldTemplateName=oldName,
            newTemplateName=newName,
        )


rename_templates_by_model(
    "PAVC with Hanzi Writer/Sound",
    {
        "Zh→En+Pin": "Zh→Mn+Pin",
        "En→Pin+Zh": "Mn→Pin+Zh",
        "Pin→Zh+En": "Pin→Zh+Mn",
    },
)

rename_templates_by_model(
    "A Course in Contemporary Chinese with Hanzi Writer/Sound",
    {
        "Zh→En+Pin": "Zh→Mn+Pin",
        "En→Pin+Zh": "Mn→Pin+Zh",
        "Pin→Zh+En": "Pin→Zh+Mn",
    },
)

rename_templates_by_model(
    "Radicals with Hanzi Writer/Sound",
    {
        "Zh→En+Pin": "Zh→Mn+Pin",
        "En→Pin+Zh": "Mn→Pin+Zh",
        "Pin→Zh+En": "Pin→Zh+Mn",
    },
)


rename_templates_by_model(
    "Chinesisch für Deutsche 1+2",
    {
        "Zh→De+Pin": "Zh→Mn+Pin",
        "De→Pin+Zh": "Mn→Pin+Zh",
        "Pin→Zh+De": "Pin→Zh+Mn",
    },
)
