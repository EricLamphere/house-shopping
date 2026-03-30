import json
import tempfile
import threading
from pathlib import Path

from app.models.link import Link


class LinkStore:
    def __init__(self, memory_dir: Path) -> None:
        self._file = memory_dir / "links.json"
        self._lock = threading.Lock()

    def _read_all(self) -> list[Link]:
        if not self._file.exists():
            return []
        raw = self._file.read_text()
        if not raw.strip():
            return []
        return [Link.model_validate(item) for item in json.loads(raw)]

    def _write_all(self, links: list[Link]) -> None:
        data = [link.model_dump() for link in links]
        fd, tmp_path = tempfile.mkstemp(dir=self._file.parent, suffix=".tmp")
        try:
            with open(fd, "w") as f:
                json.dump(data, f, indent=2)
            Path(tmp_path).replace(self._file)
        except Exception:
            Path(tmp_path).unlink(missing_ok=True)
            raise

    def list_all(self) -> list[Link]:
        with self._lock:
            links = self._read_all()
        return sorted(links, key=lambda link: link.sort_order)

    def get(self, link_id: str) -> Link | None:
        with self._lock:
            links = self._read_all()
        for link in links:
            if link.id == link_id:
                return link
        return None

    def update(self, link_id: str, text: str, url: str) -> Link | None:
        with self._lock:
            links = self._read_all()
            result = None
            updated = []
            for link in links:
                if link.id == link_id:
                    result = link.model_copy(update={"text": text, "url": url})
                    updated.append(result)
                else:
                    updated.append(link)
            if result is not None:
                self._write_all(updated)
        return result

    def add(self, link: Link) -> Link:
        with self._lock:
            links = self._read_all()
            next_order = max((l.sort_order for l in links), default=-1) + 1
            new_link = link.model_copy(update={"sort_order": next_order})
            updated = [*links, new_link]
            self._write_all(updated)
        return new_link

    def remove(self, link_id: str) -> None:
        with self._lock:
            links = self._read_all()
            updated = [l for l in links if l.id != link_id]
            self._write_all(updated)

    def update_order(self, ordered_ids: list[str]) -> None:
        with self._lock:
            links = self._read_all()
            order_map = {id_: idx for idx, id_ in enumerate(ordered_ids)}
            updated = [
                l.model_copy(update={"sort_order": order_map[l.id]})
                if l.id in order_map else l
                for l in links
            ]
            self._write_all(updated)
