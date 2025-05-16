import subprocess
import tempfile
import lib.common as cm


def opencc_convert(hanzi, config):
    with tempfile.NamedTemporaryFile(mode="r") as fpo:
        with tempfile.NamedTemporaryFile(mode="w") as fpi:
            fpi.write(hanzi)
            fpi.flush()

            subprocess.run(["opencc", "-i", fpi.name, "-o", fpo.name, "-c", config])

            fpo.seek(0)
            return fpo.read()


def to_simplified(hanzi):
    return opencc_convert(hanzi, "t2s.json")


def to_traditional(hanzi, locale):
    if locale == "zh-TW":
        return opencc_convert(hanzi, "s2tw.json")
    elif locale == "zh-CN":
        return opencc_convert(hanzi, "s2t.json")
    else:
        raise Exception(f"Locale {locale} not supported")


def cached_to_traditional(hanzi, config):
    locale = config.get("locale")
    hash = cm.hash([hanzi, locale])
    cachePath = cm.cacheDir(config) + "/opencc/" + hash
    return cm.withCacheSetPath(cachePath)(to_traditional)(hanzi, locale)
