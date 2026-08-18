#!/usr/bin/env python3
from __future__ import annotations

import argparse
import getpass
import stat
import sys
from pathlib import Path

from academics.canvas import CanvasClient, CanvasError
from academics.core import ROOT, collect, write_json


def normalized_url(value: str) -> str:
    value = value.strip().rstrip("/")
    if not value.startswith(("https://", "http://")):
        value = "https://" + value
    return value


def install_pointer(destination: Path) -> str:
    target = destination / "academics"
    target.parent.mkdir(parents=True, exist_ok=True)
    if target.exists() or target.is_symlink():
        resolved = target.resolve() if target.is_symlink() else target
        if resolved == ROOT / "skill":
            return f"already installed: {target}"
        return f"kept existing skill: {target}"
    target.symlink_to(ROOT / "skill", target_is_directory=True)
    return f"installed: {target}"


def main() -> int:
    parser = argparse.ArgumentParser(description="Set up the Canvas Academic Command Center")
    parser.add_argument("--canvas-url", help="Canvas hostname, e.g. https://school.instructure.com")
    parser.add_argument("--timezone", default="UTC", help="IANA timezone, e.g. America/Chicago")
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

    env_path = ROOT / ".env"
    env_path.write_text(
        f"CANVAS_BASE_URL={base_url}\n"
        f"CANVAS_TOKEN={token}\n"
        f"LOCAL_TIMEZONE={args.timezone}\n"
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
