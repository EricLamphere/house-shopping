import json
import tempfile
import threading
from pathlib import Path

from app.models.house import House


class HouseStore:
    def __init__(self, memory_dir: Path) -> None:
        self._file = memory_dir / "houses.json"
        self._lock = threading.Lock()

    def _read_all(self) -> list[House]:
        if not self._file.exists():
            return []
        raw = self._file.read_text()
        if not raw.strip():
            return []
        return [House.model_validate(h) for h in json.loads(raw)]

    def _write_all(self, houses: list[House]) -> None:
        data = [h.model_dump(mode="json") for h in houses]
        fd, tmp_path = tempfile.mkstemp(
            dir=self._file.parent, suffix=".tmp"
        )
        try:
            with open(fd, "w") as f:
                json.dump(data, f, indent=2, default=str)
            Path(tmp_path).replace(self._file)
        except Exception:
            Path(tmp_path).unlink(missing_ok=True)
            raise

    def list_all(self) -> list[House]:
        with self._lock:
            houses = self._read_all()
        return sorted(houses, key=lambda h: h.added_at, reverse=True)

    def list_favorites(self) -> list[House]:
        with self._lock:
            houses = self._read_all()
        favorites = [h for h in houses if h.is_favorite]
        return sorted(
            favorites,
            key=lambda h: (
                h.favorite_sort_order if h.favorite_sort_order is not None else float("inf")
            ),
        )

    def get(self, house_id: str) -> House | None:
        with self._lock:
            houses = self._read_all()
        for h in houses:
            if h.id == house_id:
                return h
        return None

    def add(self, house: House) -> House:
        with self._lock:
            houses = self._read_all()
            updated = [*houses, house]
            self._write_all(updated)
        return house

    def remove(self, house_id: str) -> None:
        with self._lock:
            houses = self._read_all()
            updated = [h for h in houses if h.id != house_id]
            self._write_all(updated)

    def toggle_favorite(self, house_id: str) -> House | None:
        with self._lock:
            houses = self._read_all()
            target = None
            updated = []
            for h in houses:
                if h.id == house_id:
                    target = h.model_copy(update={
                        "is_favorite": not h.is_favorite,
                        "favorite_sort_order": None if h.is_favorite else 0,
                    })
                    updated.append(target)
                else:
                    updated.append(h)
            if target is not None:
                self._write_all(updated)
        return target

    def update(self, house_id: str, updates: dict) -> House | None:
        with self._lock:
            houses = self._read_all()
            target = None
            updated = []
            for h in houses:
                if h.id == house_id:
                    target = h.model_copy(update=updates)
                    updated.append(target)
                else:
                    updated.append(h)
            if target is not None:
                self._write_all(updated)
        return target

    def update_favorites_order(self, ordered_ids: list[str]) -> None:
        with self._lock:
            houses = self._read_all()
            order_map = {id_: idx for idx, id_ in enumerate(ordered_ids)}
            updated = []
            for h in houses:
                if h.id in order_map:
                    updated.append(
                        h.model_copy(update={"favorite_sort_order": order_map[h.id]})
                    )
                else:
                    updated.append(h)
            self._write_all(updated)
