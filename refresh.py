#!/usr/bin/env python3
from __future__ import annotations

import json
from datetime import datetime

from academics.canvas import CanvasError
from academics.core import DATA, collect, local_time, write_json


def key(row: dict) -> str:
    return f"{row.get('course_id')}::{row.get('id')}"


def main() -> int:
    try:
        courses, assignments = collect()
    except CanvasError as exc:
        print(f"Refresh failed: {exc}")
        return 1
    snapshot_path = DATA / "refresh-snapshot.json"
    old_doc = json.loads(snapshot_path.read_text()) if snapshot_path.exists() else {"assignments": []}
    old = {key(row): row for row in old_doc.get("assignments", [])}
    new = {key(row): row for row in assignments["assignments"]}
    changes: list[str] = []
    for item_key, row in new.items():
        previous = old.get(item_key)
        label = f"{row['course_code']} — {row['name']}"
        if previous is None:
            changes.append(f"NEW: {label}")
        elif previous.get("due_at") != row.get("due_at"):
            changes.append(f"DUE DATE CHANGED: {label}")
        elif previous.get("has_rubric") is False and row.get("has_rubric") is True:
            changes.append(f"RUBRIC ADDED: {label}")
    for item_key, row in old.items():
        if item_key not in new:
            changes.append(f"REMOVED OR HIDDEN: {row['course_code']} — {row['name']}")

    write_json(DATA / "courses.json", courses)
    write_json(DATA / "assignments.json", assignments)
    write_json(snapshot_path, assignments)
    report = [f"# Last refresh — {datetime.now():%Y-%m-%d %H:%M}", ""]
    report.extend(f"- {change}" for change in changes)
    if not changes:
        report.append("- No assignment changes detected.")
    (DATA / "last-refresh.md").write_text("\n".join(report) + "\n")
    print("\n".join(changes) if changes else "No assignment changes detected.")
    print(f"Tracking {len(new)} assignments across {len(courses['courses'])} courses.")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
