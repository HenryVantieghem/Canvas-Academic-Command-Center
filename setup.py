#!/usr/bin/env python3
from __future__ import annotations

import argparse
import getpass
import os
import shutil
import stat
import sys
from datetime import datetime
from pathlib import Path
from urllib.parse import urlsplit

from academics.canvas import CanvasClient, CanvasError
from academics.core import ROOT, collect, write_json


def normalized_url(value: str) -> str:
    value = value.strip().rstrip("/")
    if not value.startswith(("https://", "http://")):
        value = "https://" + value
    parsed = urlsplit(value)
    return f"{parsed.scheme}://{parsed.netloc}"


def detect_timezone() -> str:
    if os.getenv("TZ"):
        return os.environ["TZ"]
    tzinfo = datetime.now().astimezone().tzinfo
    key = getattr(tzinfo, "key", None)
    if key:
        return str(key)
    try:
        resolved = Path("/etc/localtime").resolve().as_posix()
        marker = "/zoneinfo/"
        if marker in resolved:
            return resolved.split(marker, 1)[1]
    except OSError:
        pass
    return "UTC"


def install_pointer(destination: Path) -> str:
    target = destination / "academics"
    target.parent.mkdir(parents=True, exist_ok=True)
    if target.exists() or target.is_symlink():
        return f"kept existing skill: {target}"
    shutil.copytree(ROOT / "skill", target)
    return f"installed: {target}"


def main() -> int:
    parser = argparse.ArgumentParser(description="Set up the Canvas Academic Command Center")
    parser.add_argument("--canvas-url", help="Canvas hostname, e.g. https://school.instructure.com")
    parser.add_argument("--timezone", help="IANA timezone; defaults to the computer's timezone")
    parser.add_argument("--no-install-skills", action="store_true")
    args = parser.parse_args()

    print("\nCanvas Academic Command Center setup\n")
    base_url = normalized_url(args.canvas_url or input("Canvas URL shown in your browser: "))
    token = getpass.getpass("Canvas access token (hidden): ").strip()
    if not token:
        print("No token supplied.", file=sys.stderr)
        return 2

    try:
        client = CanvasClient(base_url, token)
        profile = client.profile()
        print(f"Connected to Canvas as {profile.get('name') or 'current user'}.")
        courses, assignments = collect(client)
    except CanvasError as exc:
        print(f"Setup failed: {exc}", file=sys.stderr)
        return 1

    timezone = args.timezone or detect_timezone()
    env_path = ROOT / ".env"
    env_path.write_text(
        f"CANVAS_BASE_URL={base_url}\n"
        f"CANVAS_TOKEN={token}\n"
        f"LOCAL_TIMEZONE={timezone}\n"
    )
    env_path.chmod(stat.S_IRUSR | stat.S_IWUSR)
    write_json(ROOT / "data" / "courses.json", courses)
    write_json(ROOT / "data" / "assignments.json", assignments)
    write_json(ROOT / "data" / "refresh-snapshot.json", assignments)

    if not args.no_install_skills:
        print(install_pointer(Path.home() / ".codex" / "skills"))
        print(install_pointer(Path.home() / ".claude" / "skills"))

    print(f"Discovered {len(courses['courses'])} active courses and "
          f"{len(assignments['assignments'])} assignments.")
    print("\nReady. Run: python3 dashboard.py\n")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
