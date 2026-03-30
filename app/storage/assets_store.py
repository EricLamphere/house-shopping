from pathlib import Path

import yaml

from app.models.assets import UserAssets


class AssetsStore:
    def __init__(self, memory_dir: Path) -> None:
        self._file = memory_dir / "assets.yml"

    def read(self) -> UserAssets:
        if not self._file.exists():
            return UserAssets()
        raw = self._file.read_text()
        if not raw.strip():
            return UserAssets()
        data = yaml.safe_load(raw)
        if not isinstance(data, dict):
            return UserAssets()
        return UserAssets.model_validate(data)

    def write(self, assets: UserAssets) -> None:
        data = assets.model_dump()
        self._file.write_text(yaml.dump(data, default_flow_style=False, sort_keys=False))
