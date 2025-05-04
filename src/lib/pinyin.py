from pypinyin.contrib.tone_sandhi import ToneSandhiMixin
from pypinyin import pinyin
from lib.gpt import askGPT
import lib.common as cm


# NOTE: This is not locale specific (does e.g. not respect taiwanes pronounciation of 星期)
def to_pinyin_basic(hanzi):
    tsm = ToneSandhiMixin()
    # Generate pinyin
    pin = pinyin(hanzi)
    # Correct the pinyin for 不 and 一
    # We don't change the tones for multiple third tones, since
    # this this is quite hard (you need to chunk the words correctly)
    # and also people do in fact say the third tones when speaking slowly.
    pin_corrected = tsm._yi(hanzi, tsm._bu(hanzi, pin))
    return " ".join(sum(pin_corrected, []))


def to_pinyin_gpt(locale, hanzi, meaning=None, previousPinyin=None, check=True):
    meaningStr = "" if None == meaning else f' for its meaning "{meaning}"'
    msg = f"""Please return the pinyin of "{hanzi}"{meaningStr}.
            Please use tone marks instead of numbers (e.g. "nǐ hǎo" instead off "ni3 hao3").
            Please always use spaces between syllables (e.g. "nǐ hǎo" instead off "nǐhǎo").
            Please mind Tone Sandhi rules (e.g. "búkèqì" instead of "bùkèqì" and "yìshēng" instead of "yīshēng").
            Use pronounciation for the words according to locale {locale}.
            Do not capitalize any letters.
            Do not comment on the sentence. Only return the pinyin.
            Take another look at the instructions and make sure you follow them.
    """
    completion = askGPT(msg, temperature=0.0, max_completion_tokens=1000)
    res = completion.choices[0].message.content

    # check if the pinyin is correct
    resBasic = to_pinyin_basic(hanzi)
    if check and ((res != resBasic) or (res != previousPinyin)):

        print(f"Msg: {msg}")
        print(f"Hanzi: {hanzi}")
        print(f"Locale: {locale}")
        print(f"Meaning: {meaning}")
        print(f"(0) GPT  : {res}")
        print(f"(1) Basic: {resBasic}")
        print(f"(2) Prev : {previousPinyin}")
        print("GPT and basic pinyin differ. Please check the result.")
        i = int(input("Which should get be used? "))
        res = [res, resBasic, previousPinyin][i]
    print(f"Got Pinyin {res} for Hanzi {hanzi}")
    return res


def cached_to_pinyin_gpt(config, hanzi, meaning=None, previousPinyin=None, check=True):
    locale = config.get("locale")
    cachePath = cm.cacheDir(config) + "/pinyin/" + cm.hash([hanzi, meaning, locale])
    return cm.withCacheSetPath(cachePath)(to_pinyin_gpt)(
        locale=locale,
        hanzi=hanzi,
        meaning=meaning,
        previousPinyin=previousPinyin,
        check=check,
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
