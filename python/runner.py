"""Python runner. Usage: runner.py <problem_dir> <cases.json> <iters> <warmup>

See tools/lc/langs.py for the contract. Prints {"cases": [{"ns", "result"}]}.
"""

import importlib
import json
import pickle
import statistics
import sys
import time
from pathlib import Path

sys.path.insert(0, str(Path(__file__).parent))


def to_json(v):
    """numpy scalars/arrays -> plain Python."""
    if hasattr(v, "tolist"):
        return v.tolist()
    raise TypeError(f"not JSON serializable: {type(v)}")


def main() -> None:
    problem_dir, cases_file = Path(sys.argv[1]), Path(sys.argv[2])
    iters, warmup = int(sys.argv[3]), int(sys.argv[4])
    meta = json.loads((problem_dir / "problem.json").read_text())["meta"]
    names = [p["name"] for p in meta["params"]]
    void_index = meta.get("output", {}).get("paramindex", 0) if meta["return"]["type"] == "void" else None

    solution = importlib.import_module(f"problems.{problem_dir.name}").Solution()
    fn = getattr(solution, meta["name"])

    out = []
    for case in json.loads(cases_file.read_text()):
        blob = pickle.dumps([case["input"][n] for n in names])  # fast fresh copy per call
        times = []
        for i in range(warmup + iters):
            args = pickle.loads(blob)
            t0 = time.perf_counter_ns()
            result = fn(*args)
            dt = time.perf_counter_ns() - t0
            if i >= warmup:
                times.append(dt)
        if void_index is not None:
            result = args[void_index]
        out.append({"ns": int(statistics.median(times)), "result": result})
    print(json.dumps({"cases": out}, default=to_json))


if __name__ == "__main__":
    main()
