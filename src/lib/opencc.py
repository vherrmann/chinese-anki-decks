import subprocess
import tempfile


def to_simplified(hanzi):
    with tempfile.NamedTemporaryFile(mode="r") as fpo:
        with tempfile.NamedTemporaryFile(mode="w") as fpi:
            fpi.write(hanzi)
            fpi.flush()

            subprocess.run(["opencc", "-i", fpi.name, "-o", fpo.name, "-c", "t2s.json"])

            fpo.seek(0)
            return fpo.read()
