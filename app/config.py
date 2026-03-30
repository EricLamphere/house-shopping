import os
from pathlib import Path


MEMORY_DIR = Path(os.environ.get("MEMORY_DIR", "memory"))
HOUSES_FILE = MEMORY_DIR / "houses.json"
ASSETS_FILE = MEMORY_DIR / "assets.yml"
