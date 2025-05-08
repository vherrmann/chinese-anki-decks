import tempfile
import shutil
from pathlib import Path


class MediaCollector(tempfile.TemporaryDirectory):
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.media = []

    def __enter__(self):
        return self

    def add(self, src, name=None):
        if name is None:
            name = Path(src).name
        self.add_disabled(src=src, name=name)
        self.media.append(name)

    def add_disabled(self, src, name=None):
        if name is None:
            name = Path(src).name
        dst = f"{self.name}/{name}"
        shutil.copy(src, dst)

    def enable(self, name):
        if not Path(f"{self.name}/{name}").exists():
            raise ValueError(f"Media file {name} does not exist.")
        elif name in self.media:
            return None
        else:
            self.media.append(name)

    def disable(self, name):
        if not Path(f"{self.name}/{name}").exists():
            raise ValueError(f"Media file {name} does not exist.")
        elif name in self.media:
            self.media.remove(name)
        else:
            return None

    def get_media(self):
        return map(lambda x: f"{self.name}/{x}", self.media)
