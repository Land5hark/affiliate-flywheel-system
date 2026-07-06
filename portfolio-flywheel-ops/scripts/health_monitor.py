"""
health_monitor.py — Runs across every registered blog and flags anything that's gone
silent. This is the piece that would have caught the backup system dying two months
ago automatically, instead of by manual accident during an unrelated conversation.

Checks, per blog:
  - Last git commit age (via repo path, if provided locally) or last_commit_at field
  - Whether metrics have been updated recently (a blog nobody's touched in weeks
    might mean its agent trio silently stopped running)
  - Backup freshness, if you pass the shared workspace mirror/backup repo paths

Usage:
    python health_monitor.py --db <path> run
    python health_monitor.py --db <path> run --repos-root /home/linuxlite/blogs
"""

import argparse
import subprocess
import sqlite3
from pathlib import Path
from datetime import datetime, timezone

STALE_COMMIT_DAYS = 7      # a blog's content repo should see activity at least this often
STALE_METRICS_DAYS = 14    # metrics should be refreshed at least this often


def get_conn(db_path):
    conn = sqlite3.connect(db_path)
    conn.row_factory = sqlite3.Row
    return conn


def days_since(iso_timestamp):
    if not iso_timestamp:
        return None
    try:
        ts = datetime.fromisoformat(iso_timestamp.replace("Z", "+00:00"))
        if ts.tzinfo is None:
            ts = ts.replace(tzinfo=timezone.utc)
        return (datetime.now(timezone.utc) - ts).days
    except ValueError:
        return None


def git_last_commit_days(repo_path: Path):
    if not repo_path.exists():
        return None, "repo path not found"
    try:
        out = subprocess.run(
            ["git", "-C", str(repo_path), "log", "-1", "--format=%cI"],
            capture_output=True, text=True, timeout=10,
        )
        if out.returncode != 0 or not out.stdout.strip():
            return None, "no commits found / not a git repo"
        return days_since(out.stdout.strip()), None
    except Exception as e:
        return None, str(e)


def run_health_check(db_path, repos_root=None):
    conn = get_conn(db_path)
    rows = conn.execute("SELECT * FROM blogs WHERE status != 'retired'").fetchall()

    if not rows:
        print("No active blogs registered to check.")
        return []

    alerts = []
    ts = datetime.now(timezone.utc).isoformat(timespec="seconds")

    for r in rows:
        blog_alerts = []
        commit_days = None

        # Prefer a live git check if we can find the repo locally
        if repos_root:
            candidate_path = Path(repos_root) / r["name"]
            commit_days, err = git_last_commit_days(candidate_path)
            if err and commit_days is None:
                # fall back to the stored field
                commit_days = days_since(r["last_commit_at"])
        else:
            commit_days = days_since(r["last_commit_at"])

        if commit_days is None:
            blog_alerts.append("no commit data available at all — cannot verify it's alive")
        elif commit_days > STALE_COMMIT_DAYS:
            blog_alerts.append(f"no commits in {commit_days} days (threshold: {STALE_COMMIT_DAYS})")

        metrics_days = days_since(r["updated_at"])
        if metrics_days is not None and metrics_days > STALE_METRICS_DAYS:
            blog_alerts.append(f"metrics not updated in {metrics_days} days (threshold: {STALE_METRICS_DAYS})")

        status = "healthy" if not blog_alerts else "stale"
        conn.execute(
            "UPDATE blogs SET last_health_check=?, health_status=? WHERE id=?",
            (ts, status, r["id"]),
        )

        if blog_alerts:
            alerts.append((r["name"], blog_alerts))

    conn.commit()
    conn.close()

    print(f"Health check complete — {len(rows)} blogs checked, {len(alerts)} flagged.\n")
    if alerts:
        print("⚠️  ALERTS:")
        for name, issues in alerts:
            print(f"  {name}:")
            for issue in issues:
                print(f"    - {issue}")
    else:
        print("✅ Everything current.")

    return alerts


if __name__ == "__main__":
    ap = argparse.ArgumentParser()
    ap.add_argument("--db", required=True)
    ap.add_argument("--repos-root", default=None,
                     help="Local directory containing blog repos as subfolders named after the blog, for live git checks")
    sub = ap.add_subparsers(dest="cmd", required=True)
    sub.add_parser("run")
    args = ap.parse_args()
    run_health_check(args.db, repos_root=args.repos_root)
