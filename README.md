# Canvas Academic Command Center

Turn Canvas into a local academic command center that works with **Codex**,
**Claude Code**, or another terminal-capable AI coding agent.

It discovers active courses, creates one local folder per course, tracks every
assignment and submission state, detects moved deadlines and new rubrics, and
installs a reusable global `academics` skill for both Codex and Claude Code.

No paid API is required. The project uses Python's standard library and your
own Canvas access token.

## Copy this prompt into your AI coding agent

```text
Set up my personal Canvas Academic Command Center from this repository:
https://github.com/HenryVantieghem/Canvas-Academic-Command-Center

Clone it into a sensible permanent folder on my computer. Read README.md and
skill/SKILL.md completely before running anything. Check that Python 3.11 or
newer is available. Run the test suite first. Then run python3 setup.py and let
me enter my Canvas hostname and access token through the script's prompts; do
not ask me to paste the token into chat, do not print it, and do not commit it.
The Canvas hostname is the beginning of the URL visible when I am logged into
Canvas, such as https://school.instructure.com.

After setup, run python3 refresh.py and python3 dashboard.py --days 14. Confirm
that one folder exists per active course and that the academics skill is
installed for both Codex and Claude Code. Never overwrite an existing academics
skill without asking me. Never submit coursework or change Canvas data during
setup. Report the repository path, discovered course count, assignment count,
and the exact commands I can use next.
```

## Get your Canvas access token

1. Sign in to your school's Canvas website.
2. Open **Account → Settings**.
3. Scroll to **Approved Integrations**.
4. Select **New Access Token**.
5. Give it a short purpose such as `Academic Command Center` and generate it.
6. Copy it immediately—Canvas may show it only once.

Keep the browser open. The setup script also asks for the Canvas hostname shown
in the address bar because access tokens do not contain the school's hostname.

Never paste the token into an AI chat, issue, commit, screenshot, or README.
`setup.py` accepts it through a hidden terminal prompt and stores it in the
gitignored `.env` file with owner-only permissions.

## Manual setup

```bash
git clone https://github.com/HenryVantieghem/Canvas-Academic-Command-Center.git
cd Canvas-Academic-Command-Center
python3 -m unittest discover -s tests -v
python3 setup.py
python3 refresh.py
python3 dashboard.py --days 14
```

The installer:

- verifies the token against `/api/v1/users/self/profile`;
- discovers every active Canvas enrollment;
- creates one `courses/<course-code>-<canvas-id>/` folder per course;
- downloads assignment metadata and submission status;
- installs the repository's skill into `~/.codex/skills/academics` and
  `~/.claude/skills/academics` when those names are available;
- preserves any existing `academics` skill instead of overwriting it.

## Everyday use

```bash
python3 refresh.py
python3 dashboard.py
python3 dashboard.py --days 30
python3 dashboard.py --json
```

You can also ask your agent naturally:

- “What is due in the next two weeks?”
- “Did any deadline move?”
- “What work is missing?”
- “Make me a study guide for my next quiz using my course material.”

The installed skill tells the agent to refresh Canvas before answering
time-sensitive questions.

## Privacy and safety

- `.env`, Canvas data, course folders, and refresh snapshots are gitignored.
- Canvas operations in this public edition are read-only.
- The token stays on the user's computer.
- The setup prompt explicitly forbids placing the token in chat.
- The project does not bypass exam controls or automate academic dishonesty.

## Requirements

- Python 3.11+
- A Canvas LMS account that permits user-generated access tokens
- Codex or Claude Code only if you want the reusable AI skill

Canvas administrators can disable access tokens or restrict API endpoints. In
that case, contact the institution rather than trying to bypass the restriction.

## License

[MIT](LICENSE)
