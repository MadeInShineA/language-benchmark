# Entry point: `python3 tools/lc <command>` (or `python3 -m lc` with tools/ on PYTHONPATH).
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent.parent))

from lc.cli import main  # noqa: E402

main()
