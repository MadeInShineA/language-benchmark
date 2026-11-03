"""Fetch problems from LeetCode's public GraphQL API and write problems/<id>/."""

from __future__ import annotations

import html
import json
import re
import urllib.request
from datetime import datetime, timezone

from .core import PROBLEMS, Problem, die, problem_id

API = "https://leetcode.com/graphql"
HEADERS = {
    "Content-Type": "application/json",
    "Referer": "https://leetcode.com/",
    "User-Agent": "Mozilla/5.0 (language-benchmark)",
}

DAILY_QUERY = """
query { activeDailyCodingChallengeQuestion { date question { titleSlug } } }
"""

QUESTION_QUERY = """
query q($slug: String!) {
  question(titleSlug: $slug) {
    questionFrontendId title titleSlug difficulty isPaidOnly
    content exampleTestcases metaData
    codeSnippets { langSlug code }
  }
}
"""


def _gql(query: str, variables: dict | None = None) -> dict:
    body = json.dumps({"query": query, "variables": variables or {}}).encode()
    req = urllib.request.Request(API, data=body, headers=HEADERS)
    with urllib.request.urlopen(req, timeout=30) as r:
        resp = json.load(r)
    if resp.get("errors"):
        die(f"LeetCode API: {resp['errors']}")
    return resp["data"]


def daily() -> tuple[str, str]:
    """-> (slug, date) of today's daily challenge."""
    d = _gql(DAILY_QUERY)["activeDailyCodingChallengeQuestion"]
    return d["question"]["titleSlug"], d["date"]


def slug_from(arg: str) -> str:
    """Accept a slug or any leetcode.com/problems/<slug>/... URL."""
    m = re.search(r"/problems/([\w-]+)", arg)
    return m.group(1) if m else arg.strip().strip("/")


# ---------------------------------------------------------------- parsing

def _text(fragment: str) -> str:
    return html.unescape(re.sub(r"<[^>]+>", "", fragment))


def expected_outputs(content: str) -> list[str]:
    """Pull 'Output: X' values out of the statement HTML (both old and new formats)."""
    return [m.strip() for m in re.findall(r"Output:?\s*:?\s*(.+)", _text(content))]


def example_cases(q: dict, meta: dict) -> list[dict]:
    names = [p["name"] for p in meta["params"]]
    lines = [l for l in q["exampleTestcases"].splitlines() if l.strip()]
    inputs = [lines[i : i + len(names)] for i in range(0, len(lines), len(names))]
    outputs = expected_outputs(q["content"])
    if len(outputs) != len(inputs):
        print(f"warning: found {len(inputs)} example inputs but {len(outputs)} outputs, "
              "fill in missing `expected` values in cases.json by hand")
    cases = []
    for i, values in enumerate(inputs):
        case = {"input": {n: json.loads(v) for n, v in zip(names, values)}}
        if i < len(outputs):
            try:
                case["expected"] = json.loads(outputs[i])
            except json.JSONDecodeError:
                case["expected"] = None
                print(f"warning: could not parse output {outputs[i]!r} of example {i + 1}")
        else:
            case["expected"] = None
        cases.append(case)
    return cases


def html_to_markdown(content: str) -> str:
    s = content
    s = re.sub(r"<pre>(.*?)</pre>", lambda m: "```\n" + _text(m.group(1)).strip() + "\n```", s, flags=re.S)
    s = re.sub(r"<code>(.*?)</code>", r"`\1`", s, flags=re.S)
    s = re.sub(r"</?(strong|b)[^>]*>", "**", s)
    s = re.sub(r"</?(em|i)>", "*", s)
    s = re.sub(r"<sup>(.*?)</sup>", r"^\1", s)
    s = re.sub(r"<li>\s*", "- ", s)
    s = re.sub(r"<img[^>]*src=\"([^\"]+)\"[^>]*>", r"![](\1)", s)
    s = html.unescape(re.sub(r"<[^>]+>", "", s)).replace("\xa0", " ")
    s = s.replace("****", "")
    return re.sub(r"\n{3,}", "\n\n", s).strip() + "\n"


# ---------------------------------------------------------------- writing

def fetch(slug: str, date: str | None = None) -> Problem:
    """Fetch a problem and create problems/<id>/. Existing cases.json is never overwritten."""
    q = _gql(QUESTION_QUERY, {"slug": slug})["question"]
    if q is None:
        die(f"no such problem: {slug}")
    if q["isPaidOnly"] and not q["content"]:
        die(f"{slug} is premium-only")
    meta = json.loads(q["metaData"])
    if "classname" in meta:
        print("warning: this is a 'design' problem (a class with methods), runners don't support it yet")

    pid = problem_id(q["questionFrontendId"], q["titleSlug"])
    d = PROBLEMS / pid
    d.mkdir(parents=True, exist_ok=True)

    old = json.loads((d / "problem.json").read_text()) if (d / "problem.json").exists() else {}
    data = {
        "frontend_id": q["questionFrontendId"],
        "slug": q["titleSlug"],
        "title": q["title"],
        "difficulty": q["difficulty"],
        "url": f"https://leetcode.com/problems/{q['titleSlug']}/",
        "daily_dates": sorted(set(old.get("daily_dates", []) + ([date] if date else []))),
        "added": old.get("added") or datetime.now(timezone.utc).isoformat(timespec="seconds"),
        "meta": meta,
        "snippets": {s["langSlug"]: s["code"] for s in q["codeSnippets"] or []},
    }
    (d / "problem.json").write_text(json.dumps(data, indent=2) + "\n")
    (d / "README.md").write_text(
        f"# {q['questionFrontendId']}. {q['title']} ({q['difficulty']})\n\n"
        f"{data['url']}\n\n{html_to_markdown(q['content'])}"
    )
    if not (d / "cases.json").exists():
        (d / "cases.json").write_text(json.dumps(example_cases(q, meta), indent=2) + "\n")
    return Problem(d, data)
