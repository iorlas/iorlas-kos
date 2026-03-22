#!/usr/bin/env python3
"""Kay Scheduler — runs background jobs independently.

Each job gets its own thread. A slow job never blocks a fast one.
Ctrl+C stops everything cleanly.

Usage:
    python3 ~/Documents/Knowledge/internals/core/scheduler.py
"""

import glob
import os
import re
import signal
import subprocess
import sys
import threading
import time
from datetime import datetime, timezone
from pathlib import Path

KNOWLEDGE_PATH = Path.home() / "Documents" / "Knowledge"
INTERNALS_DIR = KNOWLEDGE_PATH / "internals"
LOG_FILE = INTERNALS_DIR / "core" / "scheduler.log"
CHECK_INTERVAL = 60  # seconds between cadence checks


def log(msg: str):
    ts = datetime.now(timezone.utc).strftime("%Y-%m-%dT%H:%M:%SZ")
    line = f"[{ts}] {msg}"
    print(line, flush=True)
    try:
        with open(LOG_FILE, "a") as f:
            f.write(line + "\n")
    except OSError:
        pass


def get_cadence(run_py: Path) -> int:
    try:
        text = run_py.read_text()
        match = re.search(r"^CADENCE\s*=\s*(\d+)", text, re.MULTILINE)
        return int(match.group(1)) if match else 600
    except OSError:
        return 600


def job_loop(run_py: Path, stop_event: threading.Event):
    job_dir = run_py.parent
    job_name = job_dir.name
    skill_name = job_dir.parent.parent.name
    timestamp_file = job_dir / ".last-run-timestamp"
    cadence = get_cadence(run_py)

    log(f"Job loop started: {skill_name}/{job_name} (cadence: {cadence}s)")

    while not stop_event.is_set():
        last_run = 0
        if timestamp_file.exists():
            try:
                last_run = int(timestamp_file.read_text().strip())
            except (ValueError, OSError):
                last_run = 0

        now = int(time.time())
        elapsed = now - last_run

        if elapsed >= cadence:
            log(f"Running job: {skill_name}/{job_name}")
            try:
                result = subprocess.run(
                    [sys.executable, str(run_py)],
                    cwd=str(job_dir),
                    capture_output=True,
                    text=True,
                    timeout=3600,
                )
                if result.returncode == 0:
                    log(f"Job completed: {skill_name}/{job_name}")
                else:
                    log(f"Job failed: {skill_name}/{job_name} (exit: {result.returncode})")
                    if result.stderr:
                        log(f"  stderr: {result.stderr[:500]}")
            except subprocess.TimeoutExpired:
                log(f"Job timed out: {skill_name}/{job_name} (1h limit)")
            except Exception as e:
                log(f"Job error: {skill_name}/{job_name} ({e})")

            try:
                timestamp_file.write_text(str(int(time.time())))
            except OSError:
                pass

        stop_event.wait(CHECK_INTERVAL)


def main():
    log("=== Scheduler Start ===")

    # Find all jobs
    pattern = str(INTERNALS_DIR / "*" / "jobs" / "*" / "run.py")
    job_scripts = [Path(p) for p in glob.glob(pattern) if os.path.isfile(p)]

    if not job_scripts:
        log("No jobs found. Exiting.")
        return

    stop_event = threading.Event()
    threads = []

    for run_py in job_scripts:
        t = threading.Thread(target=job_loop, args=(run_py, stop_event), daemon=True)
        t.start()
        threads.append(t)

    log(f"Spawned {len(threads)} job loop(s)")

    # Ctrl+C / SIGTERM → clean shutdown
    def shutdown(signum, frame):
        log("Shutting down...")
        stop_event.set()

    signal.signal(signal.SIGINT, shutdown)
    signal.signal(signal.SIGTERM, shutdown)

    # Wait for stop signal
    try:
        while not stop_event.is_set():
            stop_event.wait(1)
    except KeyboardInterrupt:
        stop_event.set()

    # Wait for threads to finish current iteration
    for t in threads:
        t.join(timeout=5)

    log("=== Scheduler End ===")


if __name__ == "__main__":
    main()
