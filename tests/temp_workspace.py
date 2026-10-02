"""Isolated test folders using inherited workspace permissions on Windows."""
from pathlib import Path
import shutil
import uuid

BASE = Path(__file__).resolve().parents[1] / '.work'


def mkdtemp(dir=None):
    parent = Path(dir) if dir is not None else BASE
    parent.mkdir(parents=True, exist_ok=True)
    target = parent / ('test-' + uuid.uuid4().hex)
    target.mkdir()  # Inherit permissions; avoid Python's Windows mode=0700 ACL.
    return str(target)


class TemporaryDirectory:
    def __init__(self, dir=None):
        self.name = mkdtemp(dir)

    def __enter__(self):
        return self.name

    def cleanup(self):
        target = Path(self.name).resolve()
        if not target.is_relative_to(BASE.resolve()) or not target.name.startswith('test-'):
            raise ValueError('Refusing to remove a test directory outside .work.')
        if target.exists():
            shutil.rmtree(target)

    def __exit__(self, *args):
        self.cleanup()
