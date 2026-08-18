from __future__ import annotations

import json
import os
import urllib.error
import urllib.parse
import urllib.request
from typing import Any

from .env import load_env


class CanvasError(RuntimeError):
    pass


class CanvasClient:
    def __init__(self, base_url: str | None = None, token: str | None = None):
        load_env()
        self.base_url = (base_url or os.getenv("CANVAS_BASE_URL", "")).rstrip("/")
        self.token = token or os.getenv("CANVAS_TOKEN", "")
        if not self.base_url.startswith("http"):
            raise CanvasError("CANVAS_BASE_URL must be the full Canvas URL, including https://")
        if not self.token:
            raise CanvasError("CANVAS_TOKEN is missing. Run: python3 setup.py")

    def request(self, path: str) -> tuple[Any, dict[str, str]]:
        url = path if path.startswith("http") else self.base_url + path
        req = urllib.request.Request(url, headers={"Authorization": f"Bearer {self.token}"})
        try:
            with urllib.request.urlopen(req, timeout=30) as response:
                raw = response.read()
                headers = {key.lower(): value for key, value in response.headers.items()}
                return (json.loads(raw) if raw else None), headers
        except urllib.error.HTTPError as exc:
            detail = exc.read().decode("utf-8", "replace")[:300]
            if exc.code == 401:
                raise CanvasError("Canvas rejected the token. Generate a new access token in Account > Settings.") from None
            raise CanvasError(f"Canvas returned HTTP {exc.code}: {detail}") from None
        except urllib.error.URLError as exc:
            raise CanvasError(f"Could not reach Canvas: {exc.reason}") from None

    def get(self, path: str) -> Any:
        return self.request(path)[0]

    def paginated(self, path: str, max_pages: int = 50) -> list[Any]:
        rows: list[Any] = []
        next_url = path
        for _ in range(max_pages):
            body, headers = self.request(next_url)
            if isinstance(body, list):
                rows.extend(body)
            link = headers.get("link", "")
            next_url = ""
            for part in link.split(","):
                if 'rel="next"' in part:
                    next_url = part.split(";", 1)[0].strip().strip("<>")
                    break
            if not next_url:
                return rows
        raise CanvasError(f"Pagination exceeded {max_pages} pages")

    def profile(self) -> dict[str, Any]:
        value = self.get("/api/v1/users/self/profile")
        return value if isinstance(value, dict) else {}

    def courses(self) -> list[dict[str, Any]]:
        rows = self.paginated(
            "/api/v1/courses?enrollment_state=active&include[]=term&include[]=teachers&per_page=100"
        )
        return [row for row in rows if isinstance(row, dict)]

    def assignments(self, course_id: int | str) -> list[dict[str, Any]]:
        encoded = urllib.parse.quote(str(course_id), safe="")
        rows = self.paginated(
            f"/api/v1/courses/{encoded}/assignments?include[]=submission&include[]=rubric&per_page=100"
        )
        return [row for row in rows if isinstance(row, dict)]
