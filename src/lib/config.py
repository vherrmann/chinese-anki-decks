from typing import TypedDict, Callable
import genanki as ga


class ConfigData(TypedDict):
    modelId: int
    deckId: float
    deckName: str
    modelName: str
    locale: str
    meaningLanguage: str
    usePrevPinyin: bool
    usePrevGUID: bool
    convertToTraditional: bool
    genExampleSentence: bool
    noteToSubdeck: Callable[ga.Note, str | None]


class Config:
    __conf: ConfigData
    __setters: list[str]

    def __init__(self, configData, setters: list[str] = []):
        self.__conf = configData
        self.__setters = setters

    def get(self, name, default=None):
        if name[-1] == "?":
            return self.__conf.get(name, default)
        else:
            return self.__conf[name]

    def set(self, name, value):
        if name in self.__setters:
            self.__conf[name] = value
        else:
            raise NameError("Name not accepted in set() method")
