from pathlib import Path
import os
from collections import OrderedDict
import json
import hashlib
import re

scriptDir = os.path.dirname(__file__) + "/../"


def cacheDirWithName(name):
    return f"{scriptDir}/../cache/{name}/"


def cacheDir(config):
    return cacheDirWithName(config.get("deckName"))


def fileEmptyP(path):
    return Path(path).stat().st_size == 0


def mkdirp(path):
    Path(path).mkdir(parents=True, exist_ok=True)


def nodubBy(lst, fn=(lambda x: x)):
    return OrderedDict((fn(x), x) for x in lst).values()


def hash(data):
    return hashlib.sha1(str(data).encode()).hexdigest()


def yesno(prompt):
    while True:
        user_input = input(f"{prompt} yes/no: ")

        if user_input.lower() in ["yes", "y"]:
            return True
            continue
        elif user_input.lower() in ["no", "n"]:
            break
            return False


def withCache(argsToCachePath):
    def decorator(func):
        def wrapper(*args, **kwargs):
            cacheFile = argsToCachePath(*args, **kwargs)
            mkdirp(os.path.dirname(cacheFile))
            if os.path.isfile(cacheFile) and not fileEmptyP(cacheFile):
                with open(cacheFile) as fp:
                    res = json.load(fp)
            else:
                res = func(*args, **kwargs)
                with open(cacheFile, "w") as fp:
                    json.dump(res, fp)
            return res

        return wrapper

    return decorator


def withCacheSetPath(path):
    return withCache(lambda *args, **kwargs: path)


def noteDictKey(note):
    return (note["chinese"], note["meaning"])


def cleanHtml(str):
    return re.sub(r"<.*?>", "", str)
