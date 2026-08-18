---
name: academics
description: "Personal Canvas academic command center. Use for questions about classes, assignments, deadlines, missing work, grades, quizzes, exams, course files, study guides, or Canvas. Refresh Canvas before answering time-sensitive questions."
---

# Academics

This skill lives inside the Canvas Academic Command Center repository. Resolve
the repository root from this file's parent directory.

## Always refresh first

For any deadline, grade, missing-work, quiz, or exam question:

```bash
python3 refresh.py
python3 dashboard.py --days 14
```

Never answer a deadline question solely from memory. Canvas dates can move.

## Sources

- `data/courses.json`: active Canvas courses.
- `data/assignments.json`: current assignments and submission state.
- `data/last-refresh.md`: changes detected during the latest refresh.
- `courses/<COURSE>/`: user-added syllabus, notes, and study material.

For a specific assignment, follow its `html_url` in `data/assignments.json`.
Treat Canvas as authoritative for due dates and submission status.

## Boundaries

Support learning, organization, study guides, practice problems, and review of
the student's own draft. Do not bypass exam controls or disguise generated work
as the student's own. Never submit coursework unless the user explicitly asks
for that exact submission after reviewing the final artifact.
