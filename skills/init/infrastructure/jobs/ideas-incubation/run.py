#!/usr/bin/env python3
"""Ideas Incubation Job — finds new inbox ideas and runs headless Claude to research them.

Usage:
    python3 internals/inbox/jobs/ideas-incubation/run.py [--verbose]
"""
CADENCE = 1800  # 30 minutes
import json
import subprocess
import sys
from concurrent.futures import ThreadPoolExecutor, as_completed
from datetime import datetime, timedelta, date, timezone
from pathlib import Path

# ─── Configuration ───────────────────────────────────────────────────────────
MODEL = "sonnet"
MAX_BUDGET_USD = "1.00"
MAX_TURNS = 30
MAX_IDEAS_PER_CYCLE = 3
MAX_PARALLEL = 3
STALE_THRESHOLD_HOURS = 2  # Claude runs with 30 turns can take >1h
MAX_RETRIES = 3
ALLOWED_TOOLS = "Read,Write,Edit,Glob,Grep,WebFetch,WebSearch,mcp__qmd__query,mcp__qmd__get,mcp__qmd__multi_get,mcp__qmd__status"
DISALLOWED_TOOLS = "AskUserQuestion"

# ─── Paths ───────────────────────────────────────────────────────────────────
KNOWLEDGE_DIR = Path.home() / "Documents" / "Knowledge"
INBOX_DIR = KNOWLEDGE_DIR / "Inbox"
SKILLS_DIR = KNOWLEDGE_DIR / "skills"
JOB_DIR = SKILLS_DIR / "inbox" / "jobs" / "ideas-incubation"
PROMPT_FILE = JOB_DIR / "prompt.md"
LOG_FILE = JOB_DIR / "last-run.log"

VERBOSE = "--verbose" in sys.argv

# Add engine to import path
sys.path.insert(0, str(SKILLS_DIR / "core" / "engine"))
from frontmatter import parse_frontmatter, write_frontmatter, update_file_frontmatter


def log(msg: str):
    line = f"[{datetime.now(timezone.utc).strftime('%Y-%m-%dT%H:%M:%SZ')}] {msg}"
    print(line)
    with open(LOG_FILE, "a") as f:
        f.write(line + "\n")


def find_candidates(max_count: int) -> list[Path]:
    """Find inbox ideas with status: new, oldest first."""
    candidates = []
    for f in sorted(INBOX_DIR.glob("I????-*.md")):
        text = f.read_text(encoding="utf-8")
        fm, _ = parse_frontmatter(text)
        if fm is None:
            continue
        if str(fm.get("status", "")).strip().lower() != "new":
            continue
        subtype = str(fm.get("subtype", "")).strip().lower()
        legacy_type = str(fm.get("type", "")).strip()
        if subtype != "idea" and legacy_type != "Idea":
            continue
        created = str(fm.get("created", ""))
        candidates.append((created, f))

    candidates.sort(key=lambda c: c[0])
    return [f for _, f in candidates[:max_count]]


def recover_stale() -> int:
    """Reset items stuck in 'incubating' for too long. Returns count recovered."""
    recovered = 0
    for f in sorted(INBOX_DIR.glob("I????-*.md")):
        text = f.read_text(encoding="utf-8")
        fm, body = parse_frontmatter(text)
        if fm is None or str(fm.get("status", "")).strip().lower() != "incubating":
            continue

        started = fm.get("incubation_started")
        if started is None:
            started_dt = datetime.min.replace(tzinfo=timezone.utc)
        elif isinstance(started, datetime):
            started_dt = started if started.tzinfo else started.replace(tzinfo=timezone.utc)
        else:
            try:
                started_dt = datetime.fromisoformat(str(started))
                if started_dt.tzinfo is None:
                    started_dt = started_dt.replace(tzinfo=timezone.utc)
            except ValueError:
                started_dt = datetime.min.replace(tzinfo=timezone.utc)

        if datetime.now(timezone.utc) - started_dt < timedelta(hours=STALE_THRESHOLD_HOURS):
            continue

        retries = int(fm.get("incubation_retries", 0)) + 1
        if retries >= MAX_RETRIES:
            fm["status"] = "failed"
            log(f"  FAILED after {retries} retries: {f.name}")
        else:
            fm["status"] = "new"
            fm.pop("incubation_started", None)
            log(f"  RECOVERED (retry {retries}): {f.name}")
            recovered += 1

        fm["incubation_retries"] = retries
        fm["updated"] = date.today().isoformat()
        f.write_text(write_frontmatter(fm, body), encoding="utf-8")

    return recovered


def incubate(idea_file: Path) -> bool:
    """Run headless Claude on a single idea. Returns True on success."""
    name = idea_file.name
    log(f"START incubating: {name}")

    # Set status to incubating
    update_file_frontmatter(idea_file, {
        "status": "incubating",
        "incubation_started": datetime.now(timezone.utc).strftime("%Y-%m-%dT%H:%M:%SZ"),
        "updated": date.today().isoformat(),
    })

    # Build prompt
    prompt_template = PROMPT_FILE.read_text(encoding="utf-8")
    prompt = prompt_template.replace("{{IDEA_FILE}}", str(idea_file))

    mcp_config = json.dumps({
        "mcpServers": {
            "qmd": {
                "command": "npx",
                "args": ["-y", "@tobilu/qmd"],
                "env": {"QMD_PATH": str(KNOWLEDGE_DIR)},
            }
        }
    })

    result = subprocess.run(
        [
            "claude", "--print",
            "--model", MODEL,
            "--dangerously-skip-permissions",
            "--allowedTools", ALLOWED_TOOLS,
            "--disallowedTools", DISALLOWED_TOOLS,
            "--mcp-config", mcp_config,
            "--max-turns", str(MAX_TURNS),
            "--max-budget-usd", MAX_BUDGET_USD,
            "-p", prompt,
        ],
        capture_output=True,
        text=True,
    )

    # Log output
    with open(LOG_FILE, "a") as f:
        f.write(result.stdout)
        if result.stderr:
            f.write(result.stderr)

    if result.returncode != 0:
        log(f"ERROR: Claude exited {result.returncode} for {name}, setting to failed")
        if not update_file_frontmatter(idea_file, {
            "status": "failed",
            "updated": date.today().isoformat(),
        }):
            log(f"ERROR: Could not update frontmatter for {name} (file may be corrupted)")
        return False

    # Check if agent set status correctly, force incubated if not
    text = idea_file.read_text(encoding="utf-8")
    fm, _ = parse_frontmatter(text)
    current = str(fm.get("status", "")) if fm else ""

    if current == "incubated":
        log(f"DONE incubated: {name}")
    else:
        log(f"WARN: Agent left status as '{current}' for {name}, forcing to incubated")
        update_file_frontmatter(idea_file, {
            "status": "incubated",
            "incubated_at": date.today().isoformat(),
            "updated": date.today().isoformat(),
        })

    return True


def main():
    log("=== Ideas Incubation Job Start ===")

    # Step 1: Recover stale items
    log("Checking for stale incubating items...")
    recovered = recover_stale()
    log(f"Stale recovery: {recovered} item(s) reset")

    # Step 2: Find candidates
    candidates = find_candidates(MAX_IDEAS_PER_CYCLE)
    log(f"Found {len(candidates)} candidate(s)")

    if not candidates:
        log("=== Ideas Incubation Job End ===")
        return

    # Step 3: Process in parallel (threads — workload is I/O-bound subprocess calls)
    with ThreadPoolExecutor(max_workers=MAX_PARALLEL) as pool:
        futures = {pool.submit(incubate, f): f for f in candidates}
        for future in as_completed(futures):
            idea_file = futures[future]
            try:
                future.result()
            except Exception as e:
                log(f"ERROR: Exception for {idea_file.name}: {e}")

    log("=== Ideas Incubation Job End ===")


if __name__ == "__main__":
    main()
