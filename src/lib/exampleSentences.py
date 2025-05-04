import lib.common as cm
import re
from lib.pinyin import cached_to_pinyin_gpt
import os
from lib.gpt import askGPT


class BadResponse(Exception):
    pass


def checkCompletionRes(res, hanzi):
    hanziWOParens = re.sub("（.*）|(.*)", "", hanzi)
    if not re.search(hanziWOParens.replace("…", ".*"), res):
        raise BadResponse(
            f"The example sentence for {hanzi} doesn't mention the corresponding word!"
        )


def promptExampleSentence(hanzi, locale, meaning, extraMessage=""):
    msg = f"""Please create a short chinese example sentence for the chinese word "{hanzi}" for its meaning "{meaning}".
            Please use 。for the end of the sentence.
            Please use the given hanzi in your sentence (In particular, pay attention to numerals).
            Please give the sentence some originality.
            Use characters for the words according to locale {locale}.
            {extraMessage}
            Do not comment on the sentence."""
    # Please return the data in compact json without any line breaks and whitespace using the hanzi as key with the sentences.\n
    # Your entire response is going to consist of a single JSON object, and you will NOT wrap it within JSON md markers\n
    completion = askGPT(msg)

    res = completion.choices[0].message.content
    print(f"Hanzi: {hanzi}")
    print(f"Res: {res}")

    return res


def createExampleSentences(config, notes):
    cacheDir = cm.cacheDir(config) + "/create-example-sentences/"

    def noteToCachePath(note):
        hashedKey = cm.hash([note["chinese"], note["meaning"]])
        exSentCacheFile = cacheDir + f"example_sentence_{hashedKey}.json"
        return exSentCacheFile

    def createExampleSentence(note):
        hanzi = note["chinese"]
        meaning = note["meaning"]
        while True:
            try:
                res = promptExampleSentence(hanzi=hanzi, locale=locale, meaning=meaning)

                checkCompletionRes(res, hanzi)
                return res
            except BadResponse as e:
                print(f"Error: {e}")

                if cm.yesno("Accept?"):
                    return res
                else:
                    continue
            break

    def cached_createExampleSentence(note):
        hashedKey = cm.hash([note["chinese"], note["meaning"]])
        exSentCacheFile = cacheDir + f"example_sentence_{hashedKey}.json"
        return cm.withCacheSetPath(exSentCacheFile)(createExampleSentence)(note)

    def translateSentence(meaningLanguage, sentence):
        msg = f"""Please translate the following sentence to {meaningLanguage}:
                  {sentence}"""
        completion = askGPT(msg)

        res = completion.choices[0].message.content
        print(f"Hanzi: {sentence}")
        print(f"Res: {res}")
        return res

    def cached_translateSentence(config, sentence):
        meaningLanguage = config.get("meaningLanguage")
        hashedKey = cm.hash([sentence, meaningLanguage])
        transSentCacheFile = cacheDir + f"translated_sentence_{hashedKey}.json"
        return cm.withCacheSetPath(transSentCacheFile)(translateSentence)(
            meaningLanguage, sentence
        )

    exampleSentences = {
        cm.noteDictKey(note): cached_createExampleSentence(note) for note in notes
    }

    pinyin = {
        key: cached_to_pinyin_gpt(config, hanzi=sentence, check=False)
        for key, sentence in exampleSentences.items()
    }

    translatedSentences = {
        key: cached_translateSentence(config, sentence)
        for key, sentence in exampleSentences.items()
    }

    return {
        "chinese": exampleSentences,
        "pinyin": pinyin,
        "translated": translatedSentences,
    }
