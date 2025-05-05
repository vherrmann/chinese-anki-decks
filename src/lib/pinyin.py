from pypinyin_dict.phrase_pinyin_data import cc_cedict
from pypinyin import pinyin, Style
from pypinyin.contrib.tone_convert import tone2_to_tone
from lib.gpt import askGPT
import lib.common as cm
import zhon
import re
from lib.opencc import to_simplified

# make pinyin results more accurate
cc_cedict.load()


# FIXME: This is not locale specific (does e.g. not respect taiwanes pronounciation of 星期)
# FIXME: does not work for e.g. 我星期一去打籃球, since the tone of 一 is changed
def to_pinyin_basic(txtTrad):
    # pypinyin does not work well with traditional characters
    txt = to_simplified(txtTrad)

    # This function does not work well if there are non-hanzi characters in the input
    def hanzi_to_pinyin(hanzi):
        # Generate pinyin with ü instead of v
        pin = pinyin(hanzi, style=Style.TONE2, neutral_tone_with_five=True, v_to_u=True)
        # Correct the pinyin for 不 and 一
        # We don't change the tones for multiple third tones, since
        # this this is quite hard (you need to chunk the words correctly)
        # and also people do in fact say the third tones when speaking slowly.

        pinList = [p[0] for p in pin]

        for i, h in reversed(list(enumerate(hanzi[:-1]))):
            next_tone = int(re.search(r"\d+", pinList[i + 1]).group(0))

            # if the next hanzi is 個, it is as if the next tone is 4
            if hanzi[i + 1] == "個":
                next_tone = 4

            new_tone = None
            if h == "不":
                if next_tone == 4:
                    new_tone = 2
                else:
                    new_tone = 4
            elif h == "一":
                if next_tone in [1, 2, 3]:
                    new_tone = 4
                elif next_tone == 4:
                    new_tone = 2
            if new_tone is not None:
                pinList[i] = re.sub(r"\d+", str(new_tone), pinList[i])

        return tone2_to_tone(" ".join(pinList))

    # This returns a list. For every non-hanzi characters there is an empty string
    # Blocks of hanzi characters are contained as a chunk
    regex = rf"[{zhon.hanzi.characters}]+"
    res = re.sub(regex, lambda m: hanzi_to_pinyin(m.group(0)), txt)
    return res


def to_pinyin_check(hanzi, previousPinyin):
    basicPinyin = to_pinyin_basic(hanzi)
    res = basicPinyin
    if basicPinyin != previousPinyin:
        print(f"Hanzi: {hanzi}")
        print(f"(0) Basic: {basicPinyin}")
        print(f"(1) Prev : {previousPinyin}")
        print("Prev pinyin and generated differ. Please check the result.")
        i = int(input("Which should get be used? "))
        res = [basicPinyin, previousPinyin][i]
    print(f"Got Pinyin {res} for Hanzi {hanzi}")
    return res


def cached_to_pinyin_check(config, hanzi, previousPinyin):
    locale = config.get("locale")
    cachePath = cm.cacheDirWithName("pinyin") + cm.hash([hanzi, locale])
    return cm.withCacheSetPath(cachePath)(to_pinyin_check)(
        hanzi=hanzi,
        previousPinyin=previousPinyin,
    )


# does not really work
def to_pinyin_gpt(
    locale, hanzi, meaning=None, meaningLanguage=None, previousPinyin=None
):
    basicPinyin = to_pinyin_basic(hanzi)

    meaningLanguage = "" if meaningLanguage is None else meaningLanguage
    meaningStr = (
        ""
        if meaning is None
        else f"{meaning} (language the meaning: {meaningLanguage})"
    )
    msg = f"""
You will be given a chinese word or phrase, the meaning of that word together with the language of the meaning or phrase and the hanyu-pinyin of that word or phrase.
You will also get the locale the pinyin should be in.
The chinese, the meaning, pinyin and the locale are written behind a string of dashes.
Please be aware that the pinyin uses Tone Sandhi rules for 一 and 不.
Your task is NOT to check the spacing/capitalization of the pinyin.
Your task is the following:
You should write out the word CORRECT if the pinyin fits the chinese and the meaning.
You should write out the word INCORRECT if the pinyin does not fit the chinese and the meaning.
Do not write anything other than CORRECT, if the pinyin is correct.
If the pinyin is incorrect, please explain your reasining thoroughly.
After your explanation, please write CORRECT or INCORRECT again. You may change your assessememt, if you think you made a mistake earlier.
-------------------------------
Chinese: {hanzi}
Meaning: {meaningStr}
Locale: {locale}
Pinyin: {basicPinyin}
"""
    completion = askGPT(msg, temperature=0.0, max_completion_tokens=1000)
    classif = completion.choices[0].message.content
    check = False
    classifLines = classif.strip().split("\n")
    lastLine = classifLines[-1]
    if len(classifLines) > 1:
        print(classif)
    if "INCORRECT" in lastLine or "CORRECT" not in lastLine:
        check = True

    res = basicPinyin
    if check or (basicPinyin != previousPinyin):
        if check:
            print(f"Msg: {msg}")
            print(classif)
        print(f"Hanzi: {hanzi}")
        print(f"Locale: {locale}")
        print(f"Meaning: {meaning}")
        print(f"(0) Basic: {basicPinyin}")
        print(f"(1) Prev : {previousPinyin}")
        print("pinyins differ or gpt doesn't like it. Please check the result.")
        i = int(input("Which should get be used? "))
        res = [res, basicPinyin, previousPinyin][i]
    print(f"Got Pinyin {res} for Hanzi {hanzi}")
    return res


def cached_to_pinyin_gpt(
    config, hanzi, meaning=None, meaningLanguage=None, previousPinyin=None
):
    locale = config.get("locale")
    hash = cm.hash([hanzi, meaning, locale, meaningLanguage])
    cachePath = cm.cacheDir(config) + "/pinyin/" + hash
    return cm.withCacheSetPath(cachePath)(to_pinyin_gpt)(
        locale=locale,
        hanzi=hanzi,
        meaning=meaning,
        meaningLanguage=meaningLanguage,
        previousPinyin=previousPinyin,
    )


def detect_pinyin_tone(syllable):
    # fmt: off
    tone_marks = {
        'ā': 1, 'á': 2, 'ǎ': 3, 'à': 4,
        'ē': 1, 'é': 2, 'ě': 3, 'è': 4,
        'ī': 1, 'í': 2, 'ǐ': 3, 'ì': 4,
        'ō': 1, 'ó': 2, 'ǒ': 3, 'ò': 4,
        'ū': 1, 'ú': 2, 'ǔ': 3, 'ù': 4,
        'ǖ': 1, 'ǘ': 2, 'ǚ': 3, 'ǜ': 4,
    }
    # fmt: on
    for char in syllable.lower():
        if char in tone_marks:
            return tone_marks[char]
    return 5


def color_pinyin(pinyin):
    coloredSyllab = []
    for syllable in pinyin.split(" "):
        toneNum = detect_pinyin_tone(syllable)
        if toneNum is None:
            coloredSyllab.append(syllable)
        else:
            coloredSyllab.append(f'<span class="tone{toneNum}">{syllable}</span>')
    return " ".join(coloredSyllab)
