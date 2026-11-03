"""Shared paths and the Problem model."""

from __future__ import annotations

import json
import sys
from dataclasses import dataclass
from pathlib import Path

ROOT = Path(__file__).resolve().parents[2]
PROBLEMS = ROOT / "problems"


def die(msg: str) -> None:
    print(f"error: {msg}", file=sys.stderr)
    sys.exit(1)


def problem_id(frontend_id: str, slug: str) -> str:
    """'462', 'minimum-moves-...' -> 'p0462_minimum_moves_...'

    Valid as a file name, Rust module, Go package and Python module.
    """
    return f"p{int(frontend_id):04d}_{slug.replace('-', '_')}"


@dataclass
class Problem:
    dir: Path
    data: dict

    @classmethod
    def load(cls, d: Path) -> "Problem":
        return cls(d, json.loads((d / "problem.json").read_text()))

    @property
    def id(self) -> str:
        return self.dir.name

    @property
    def number(self) -> int:
        return int(self.data["frontend_id"])

    @property
    def title(self) -> str:
        return self.data["title"]

    @property
    def meta(self) -> dict:
        """LeetCode metaData: {"name": fn, "params": [{name, type}], "return": {type}}"""
        return self.data["meta"]

    @property
    def param_names(self) -> list[str]:
        return [p["name"] for p in self.meta["params"]]

    def snippet(self, lang_slug: str) -> str | None:
        return self.data["snippets"].get(lang_slug)

    @property
    def cases_file(self) -> Path:
        return self.dir / "cases.json"


def all_problems() -> list[Problem]:
    if not PROBLEMS.exists():
        return []
    return [Problem.load(d) for d in sorted(PROBLEMS.iterdir()) if (d / "problem.json").exists()]


def resolve(query: str | None) -> Problem:
    """Find a problem by number ('462'), id, slug or URL. None -> most recently added."""
    problems = all_problems()
    if not problems:
        die("no problems yet, run `lc daily` or `lc new <slug>`")
    if query is None:
        return max(problems, key=lambda p: p.data.get("added", ""))
    q = query.strip().lower()
    for p in problems:
        if q.isdigit() and p.number == int(q):
            return p
        if q in (p.id, p.data["slug"]) or f"/problems/{p.data['slug']}" in q:
            return p
    matches = [p for p in problems if q.replace("-", "_") in p.id]
    if len(matches) == 1:
        return matches[0]
    die(f"no unique problem matching {query!r}")
    raise AssertionError  # unreachable
