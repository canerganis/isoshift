"""Generic literature search. `LiteratureSource` is the adapter interface; OpenAlex is the default backend.
A Valency MCP Bond backend can be added later by subclassing LiteratureSource (see ValencyBondSource stub)."""
from __future__ import annotations

import json
import threading
import time
from abc import ABC, abstractmethod
from dataclasses import dataclass, asdict
from pathlib import Path

import requests

from .cache import DiskCache, ROOT, sha256_hex


@dataclass
class Paper:
    id: str
    doi: str | None
    title: str
    year: int | None
    abstract: str
    cited_by_count: int
    source: str = ""

    def to_dict(self) -> dict:
        return asdict(self)


class LiteratureSource(ABC):
    """Adapter interface. Implement `search` and return Paper objects."""

    @abstractmethod
    def search(self, query: str, *, year_from: int | None = None, year_to: int | None = None,
               limit: int = 25, **filters) -> list[Paper]:
        ...


class ValencyBondSource(LiteratureSource):
    """Stub: to be implemented against the Valency MCP Bond (literature over 44.5M papers)."""

    def search(self, query, *, year_from=None, year_to=None, limit=25, **filters):
        raise NotImplementedError("Valency MCP Bond backend not implemented yet")


def reconstruct_abstract(inv: dict | None) -> str:
    if not inv:
        return ""
    pos: dict[int, str] = {}
    for word, idxs in inv.items():
        for i in idxs:
            pos[i] = word
    return " ".join(pos[i] for i in sorted(pos))


def parse_work(w: dict) -> Paper:
    doi = w.get("doi")
    if doi and doi.startswith("https://doi.org/"):
        doi = doi[len("https://doi.org/"):]
    return Paper(id=w.get("id", ""), doi=doi, title=w.get("title") or w.get("display_name") or "",
                 year=w.get("publication_year"),
                 abstract=reconstruct_abstract(w.get("abstract_inverted_index")),
                 cited_by_count=w.get("cited_by_count", 0) or 0, source="openalex")


class OpenAlexSource(LiteratureSource):
    BASE = "https://api.openalex.org/works"

    def __init__(self, cache_dir: str | Path | None = None, min_interval_s: float = 0.2,
                 timeout: int = 30):
        self.cache = DiskCache(cache_dir or ROOT / ".cache" / "openalex")
        self.min_interval = min_interval_s
        self.timeout = timeout
        self._last = 0.0
        self._lock = threading.Lock()
        # Deliberately no mailto / email in requests.
        self.session = requests.Session()
        self.session.headers["User-Agent"] = "osi-hackathon-harness/0.1"

    def _get(self, params: dict) -> dict:
        key = sha256_hex("openalex", json.dumps(params, sort_keys=True))
        hit = self.cache.get(key)
        if hit is not None:
            return hit
        r = None
        for attempt in range(4):
            with self._lock:
                wait = self.min_interval - (time.time() - self._last)
                if wait > 0:
                    time.sleep(wait)
                self._last = time.time()
            r = self.session.get(self.BASE, params=params, timeout=self.timeout)
            if r.status_code in (429, 500, 502, 503, 504):
                time.sleep(2 ** attempt)
                continue
            r.raise_for_status()
            data = r.json()
            self.cache.set(key, data)
            return data
        r.raise_for_status()
        raise RuntimeError("OpenAlex request failed")

    def search(self, query, *, year_from=None, year_to=None, limit=25,
               extra_filter: str | None = None, sort: str | None = None, **filters) -> list[Paper]:
        flt = []
        if year_from is not None:
            flt.append(f"from_publication_date:{year_from}-01-01")
        if year_to is not None:
            flt.append(f"to_publication_date:{year_to}-12-31")
        if extra_filter:
            flt.append(extra_filter)
        params = {"search": query, "per-page": min(limit, 200)}
        if flt:
            params["filter"] = ",".join(flt)
        if sort:
            params["sort"] = sort
        data = self._get(params)
        return [parse_work(w) for w in data.get("results", [])][:limit]


def search(query: str, **kw) -> list[Paper]:
    """Convenience: OpenAlex search."""
    return OpenAlexSource().search(query, **kw)
