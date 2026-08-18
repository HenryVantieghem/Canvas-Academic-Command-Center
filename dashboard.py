#!/usr/bin/env python3
from __future__ import annotations

import argparse
import json
from datetime import datetime, timedelta, timezone

from academics.core import DATA, local_time


def main() -> int:
    parser = argparse.ArgumentParser(description="Show upcoming and missing Canvas work")
    parser.add_argument("--days", type=int, default=14)
    parser.add_argument("--json", action="store_true")
    args = parser.parse_args()
    path = DATA / "assignments.json"
    if not path.exists():
        print("No Canvas data yet. Run: python3 setup.py")
        return 1
    rows = json.loads(path.read_text()).get("assignments", [])
    now = datetime.now(timezone.utc)
    cutoff = now + timedelta(days=args.days)
    due = []
    for row in rows:
        when = datetime.fromisoformat(row["due_at"].replace("Z", "+00:00")) if row.get("due_at") else None
        if row.get("missing") or (when and now <= when <= cutoff and not row.get("submitted")):
            due.append(row)
    due.sort(key=lambda row: row.get("due_at") or "9999")
    if args.json:
        print(json.dumps(due, indent=2))
        return 0
    print(f"\nCanvas dashboard — {len(due)} actionable item(s)\n")
    for row in due:
        when = local_time(row.get("due_at"))
        status = "MISSING" if row.get("missing") else "UPCOMING"
        stamp = when.strftime("%a %b %d, %I:%M %p %Z") if when else "no due date"
        print(f"[{status}] {stamp}  {row['course_code']} — {row['name']}")
        if row.get("html_url"):
            print(f"          {row['html_url']}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
