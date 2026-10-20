"""Run many ask() calls concurrently with per-model concurrency caps, retries and a progress bar."""
from __future__ import annotations

import threading
from concurrent.futures import ThreadPoolExecutor, as_completed
from typing import Iterable

from tenacity import retry, stop_after_attempt, wait_exponential, retry_if_result
from tqdm import tqdm

from .llm import ask, Result


def run_many(calls: Iterable[dict], *, max_per_model: int | dict = 2, retries: int = 3,
             backoff: float = 2.0, progress: bool = True, max_workers: int | None = None) -> list[Result]:
    """calls: iterable of dicts with keys model, prompt and optional system/json_schema/timeout/cache.
    Returns Results in input order. Calls that still fail after retries come back with .error set."""
    calls = list(calls)
    sems: dict[str, threading.Semaphore] = {}
    lock = threading.Lock()

    def limit_for(model: str) -> int:
        return max_per_model.get(model, 2) if isinstance(max_per_model, dict) else max_per_model

    def sem_for(model: str) -> threading.Semaphore:
        with lock:
            if model not in sems:
                sems[model] = threading.Semaphore(limit_for(model))
            return sems[model]

    def one(c: dict) -> Result:
        kw = {k: v for k, v in c.items() if k not in ("model", "prompt")}

        @retry(stop=stop_after_attempt(retries),
               wait=wait_exponential(multiplier=backoff, min=backoff, max=60),
               retry=retry_if_result(lambda r: r.error is not None),
               retry_error_callback=lambda rs: rs.outcome.result())
        def attempt() -> Result:
            with sem_for(c["model"]):
                return ask(c["model"], c["prompt"], **kw)

        return attempt()

    models = {c["model"] for c in calls}
    workers = max_workers or max(1, sum(limit_for(m) for m in models) * 2)
    results: list[Result | None] = [None] * len(calls)
    with ThreadPoolExecutor(max_workers=workers) as ex, tqdm(total=len(calls), disable=not progress) as bar:
        futs = {ex.submit(one, c): i for i, c in enumerate(calls)}
        for f in as_completed(futs):
            results[futs[f]] = f.result()
            bar.update(1)
    return results  # type: ignore[return-value]
