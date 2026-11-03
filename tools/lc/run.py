"""`lc test`: build, run every language's runner, check results against cases.json."""

from __future__ import annotations

import json
import subprocess
import sys
from dataclasses import dataclass, field
from pathlib import Path

from .core import Problem, all_problems
from .langs import Lang

GREEN, RED, YELLOW, DIM, BOLD, RESET = (
    ("\033[32m", "\033[31m", "\033[33m", "\033[2m", "\033[1m", "\033[0m")
    if sys.stdout.isatty() else ("",) * 6
)


@dataclass
class Outcome:
    lang: str
    error: str | None = None
    skipped: str | None = None
    cases: list[dict] = field(default_factory=list)  # [{"ns", "result"}]


def normalize(v):
    if isinstance(v, float):
        return round(v, 5)
    if isinstance(v, list):
        return [normalize(x) for x in v]
    if isinstance(v, dict):
        return {k: normalize(x) for k, x in v.items()}
    return v


def short(v, n: int = 80) -> str:
    s = json.dumps(v)
    return s if len(s) <= n else s[: n - 3] + "..."


def prepare(langs: list[Lang]) -> dict[str, str]:
    """Sync glue code and build each language once. -> {lang: build error}."""
    problems = all_problems()
    errors = {}
    for lang in langs:
        lang.sync(problems)
        cmd = lang.build_cmd()
        if cmd is None:
            continue
        print(f"{DIM}building {lang.name}...{RESET}", flush=True)
        r = subprocess.run(cmd, cwd=lang.dir, capture_output=True, text=True)
        if r.stderr.strip() and r.returncode == 0:
            print(f"{DIM}{r.stderr.rstrip()}{RESET}")  # warnings
        if r.returncode != 0:
            errors[lang.name] = (r.stderr or r.stdout).strip()
    return errors


def run_lang(lang: Lang, p: Problem, cases: Path, build_errors: dict) -> Outcome:
    if not lang.has_solution(p):
        return Outcome(lang.name, skipped="no solution file")
    if lang.name in build_errors:
        return Outcome(lang.name, error="build failed:\n" + build_errors[lang.name])
    r = subprocess.run(lang.run_cmd(p, cases, 1, 0), cwd=lang.dir, capture_output=True, text=True)
    lines = [l for l in r.stdout.splitlines() if l.strip()]
    if r.returncode != 0 or not lines:
        return Outcome(lang.name, error=(r.stderr or r.stdout).strip() or f"exit code {r.returncode}")
    if len(lines) > 1:  # the solution printed something, show it
        print(f"{DIM}[{lang.name} stdout]\n" + "\n".join(lines[:-1])[:2000] + RESET)
    try:
        return Outcome(lang.name, cases=json.loads(lines[-1])["cases"])
    except (json.JSONDecodeError, KeyError) as e:
        return Outcome(lang.name, error=f"bad runner output ({e}): {lines[-1][:200]}")


def print_error(o: Outcome) -> None:
    tail = "\n".join(o.error.splitlines()[-15:])
    print(f"  {o.lang:<8} {RED}✗ error{RESET}\n" + "\n".join(f"{DIM}    │ {l}{RESET}" for l in tail.splitlines()))


def test(p: Problem, langs: list[Lang]) -> bool:
    cases = json.loads(p.cases_file.read_text())
    build_errors = prepare(langs)
    print(f"\n{BOLD}{p.id}{RESET} · {p.title}  ({len(cases)} cases)")
    ok_all = True
    for lang in langs:
        o = run_lang(lang, p, p.cases_file, build_errors)
        if o.skipped:
            print(f"  {lang.name:<8} {DIM}– {o.skipped}{RESET}")
            continue
        if o.error:
            print_error(o)
            ok_all = False
            continue
        fails = [(i, c, got) for i, (c, got) in enumerate(zip(cases, o.cases))
                 if c.get("expected") is not None and normalize(c["expected"]) != normalize(got["result"])]
        unchecked = sum(c.get("expected") is None for c in cases)
        passed = len(cases) - len(fails) - unchecked
        if fails:
            ok_all = False
            print(f"  {lang.name:<8} {RED}✗ {passed}/{len(cases)} passed{RESET}")
            for i, c, got in fails[:5]:
                print(f"    case {i + 1}: input    {short(c['input'])}\n"
                      f"            expected {short(c['expected'])}\n"
                      f"            got      {RED}{short(got['result'])}{RESET}")
        else:
            extra = f" {YELLOW}({unchecked} without expected value){RESET}" if unchecked else ""
            print(f"  {lang.name:<8} {GREEN}✓ {passed}/{len(cases)} passed{RESET}{extra}")
    return ok_all
