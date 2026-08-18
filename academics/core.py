from __future__ import annotations

import json
import re
from datetime import datetime, timezone
from pathlib import Path
from typing import Any
from zoneinfo import ZoneInfo

from .canvas import CanvasClient
from .env import ROOT, load_env


DATA = ROOT / "data"
COURSES_DIR = ROOT / "courses"


def slug(value: str) -> str:
    clean = re.sub(r"[^A-Za-z0-9]+", "-", value).strip("-")
    return clean[:80] or "course"


def timezone_name() -> str:
    load_env()
    import os
    return os.getenv("LOCAL_TIMEZONE", "UTC")


def local_time(value: str | None) -> datetime | None:
    if not value:
        return None
    parsed = datetime.fromisoformat(value.replace("Z", "+00:00"))
    return parsed.astimezone(ZoneInfo(timezone_name()))


def collect(client: CanvasClient | None = None) -> tuple[dict[str, Any], dict[str, Any]]:
    client = client or CanvasClient()
    profile = client.profile()
    courses: dict[str, Any] = {
        "generated_at": datetime.now(timezone.utc).isoformat(),
        "student": {"id": profile.get("id"), "name": profile.get("name")},
        "courses": [],
    }
    assignments: dict[str, Any] = {"generated_at": courses["generated_at"], "assignments": []}
    for course in client.courses():
        course_id = course.get("id")
        code = str(course.get("course_code") or course.get("name") or course_id)
        item = {
            "id": course_id,
            "code": code,
            "name": course.get("name") or code,
            "term": (course.get("term") or {}).get("name"),
            "teachers": [t.get("display_name") for t in course.get("teachers", []) if isinstance(t, dict)],
        }
        courses["courses"].append(item)
        # The Canvas course id keeps two active sections with the same course
        # code from silently sharing one folder.
        course_dir = COURSES_DIR / slug(f"{code}-{course_id}")
        course_dir.mkdir(parents=True, exist_ok=True)
        for assignment in client.assignments(course_id):
            submission = assignment.get("submission") or {}
            assignments["assignments"].append({
                "id": assignment.get("id"),
                "course_id": course_id,
                "course_code": code,
                "name": assignment.get("name"),
                "due_at": assignment.get("due_at"),
                "points_possible": assignment.get("points_possible"),
                "html_url": assignment.get("html_url"),
                "submission_types": assignment.get("submission_types") or [],
                "has_rubric": bool(assignment.get("rubric")),
                "submitted": bool(submission.get("submitted_at")),
                "missing": bool(submission.get("missing")),
                "late": bool(submission.get("late")),
                "score": submission.get("score"),
            })
    return courses, assignments


def write_json(path: Path, value: Any) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(json.dumps(value, indent=2) + "\n")
