#!/usr/bin/env python3
"""Set index.html's DOC_BUILD stamp to now.

The stamp is a local-edit timestamp, and a sync IS an edit — splicing a Progress Log entry or a
maturity refresh changes what the page says. Without this the stamp goes stale in the one
direction that misleads: the page claims to be older than the content it is showing, and the
tab that carries the stamp is the one people screenshot.

Called by the sync workflow after the splices, so an automated update stamps itself the same way
a hand edit does. Idempotent within a minute; run it after the splices, never before.

    python scripts/bump_build.py            # stamp now (UTC)
    python scripts/bump_build.py 2026.07.28.1400
"""
from __future__ import annotations

import re
import sys
from datetime import datetime, timezone
from pathlib import Path

INDEX = Path(__file__).resolve().parent.parent / "index.html"
STAMP = re.compile(r'(const DOC_BUILD=")([^"]*)(")')
FORMAT = re.compile(r"\d{4}\.\d{2}\.\d{2}\.\d{4}")


def main() -> int:
    stamp = sys.argv[1] if len(sys.argv) > 1 else datetime.now(timezone.utc).strftime(
        "%Y.%m.%d.%H%M")
    if not FORMAT.fullmatch(stamp):
        raise SystemExit(f"{stamp!r} is not CalVer YYYY.MM.DD.HHMM")
    html = INDEX.read_text()
    if not STAMP.search(html):
        raise SystemExit("index.html: DOC_BUILD not found")
    old = STAMP.search(html).group(2)
    if old == stamp:
        print(f"DOC_BUILD already {stamp}")
        return 0
    INDEX.write_text(STAMP.sub(rf"\g<1>{stamp}\g<3>", html, count=1))
    print(f"DOC_BUILD {old} -> {stamp}")
    return 0


if __name__ == "__main__":
    sys.exit(main())
