"""lc: fetch LeetCode problems, scaffold solution stubs, test them."""

from __future__ import annotations

import argparse
import sys

from . import leetcode, run
from .core import ROOT, Problem, all_problems, resolve
from .langs import LANGS


def scaffold(p: Problem) -> None:
    print(f"{p.id} · {p.title} ({p.data['difficulty']})\n  {p.dir.relative_to(ROOT)}/  (README.md, cases.json)")
    for lang in LANGS.values():
        created = lang.scaffold(p)
        if created:
            print(f"  + {created.relative_to(ROOT)}")
        elif p.snippet(lang.leetcode_slug) is None:
            print(f"  ! LeetCode has no {lang.name} snippet for this problem")
    for lang in LANGS.values():
        lang.sync(all_problems())


def pick_langs(names: list[str] | None):
    if not names:
        return list(LANGS.values())
    unknown = [n for n in names if n not in LANGS]
    if unknown:
        sys.exit(f"unknown language(s): {', '.join(unknown)} (have: {', '.join(LANGS)})")
    return [LANGS[n] for n in names]


def main(argv: list[str] | None = None) -> None:
    ap = argparse.ArgumentParser(prog="lc", description=__doc__)
    sub = ap.add_subparsers(dest="cmd", required=True)

    sub.add_parser("daily", help="fetch today's daily problem and create stubs for every language")
    s = sub.add_parser("new", help="fetch a problem by slug or URL and create stubs")
    s.add_argument("problem", help="e.g. two-sum or https://leetcode.com/problems/two-sum/")

    lang_help = f"languages to run (default: all of {', '.join(LANGS)})"
    s = sub.add_parser("test", help="check solutions against cases.json")
    s.add_argument("problem", nargs="?", help="number, slug or id (default: most recently added)")
    s.add_argument("-l", "--lang", nargs="+", help=lang_help)

    sub.add_parser("list", help="list problems and which languages have a solution file")
    sub.add_parser("sync", help="create missing stubs and regenerate glue code for all problems")

    a = ap.parse_args(argv)

    if a.cmd == "daily":
        slug, date = leetcode.daily()
        print(f"daily problem for {date}: {slug}")
        scaffold(leetcode.fetch(slug, date))
    elif a.cmd == "new":
        scaffold(leetcode.fetch(leetcode.slug_from(a.problem)))
    elif a.cmd == "test":
        ok = run.test(resolve(a.problem), pick_langs(a.lang))
        sys.exit(0 if ok else 1)
    elif a.cmd == "list":
        for p in all_problems():
            have = [l.name for l in LANGS.values() if l.has_solution(p)]
            print(f"{p.number:>5}  {p.title:<50} {p.data['difficulty']:<7} {' '.join(have)}")
    elif a.cmd == "sync":
        for p in all_problems():
            for lang in LANGS.values():
                if created := lang.scaffold(p):
                    print(f"+ {created.relative_to(ROOT)}")
        for lang in LANGS.values():
            lang.sync(all_problems())
        print("glue code regenerated")
