"""
blog_lifecycle.py — Tracks each blog through its lifecycle and fires the graduation
event that spawns the next blog in the flywheel.

Extends the shared affiliate_graph.db (see affiliate-graph-db skill) with a `blogs`
table. Uses the same database file — pass the same --db path you use for that skill
so blogs, niches, products, and programs all live in one place.

Lifecycle states: candidate -> building -> active -> graduated -> retired

Usage:
    python blog_lifecycle.py --db <path> init
    python blog_lifecycle.py --db <path> register "balcony-drip-guide" --niche "Balcony Drip Irrigation" --repo-url "https://github.com/Land5hark/balcony-drip-guide"
    python blog_lifecycle.py --db <path> update-metrics "balcony-drip-guide" --articles 40 --sales 1
    python blog_lifecycle.py --db <path> check-graduation "balcony-drip-guide"
    python blog_lifecycle.py --db <path> list
    python blog_lifecycle.py --db <path> graduate "balcony-drip-guide"
"""

import argparse
import sys
from datetime import datetime, timezone
import sqlite3

sys.path.insert(0, __file__.rsplit("/", 1)[0])  # allow standalone execution


def now():
    return datetime.now(timezone.utc).isoformat(timespec="seconds")


BLOGS_SCHEMA = """
CREATE TABLE IF NOT EXISTS blogs (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    name TEXT NOT NULL UNIQUE,
    niche_name TEXT,
    repo_url TEXT,
    status TEXT DEFAULT 'candidate',   -- candidate | building | active | graduated | retired
    article_count INTEGER DEFAULT 0,
    confirmed_sales INTEGER DEFAULT 0,
    graduation_trigger TEXT,           -- which condition fired: 'first_sale' | 'article_count' | 'manual'
    first_sale_at TEXT,
    graduated_at TEXT,
    last_health_check TEXT,
    health_status TEXT DEFAULT 'unknown',  -- healthy | stale | broken | unknown
    last_commit_at TEXT,
    monthly_token_cost REAL,
    monthly_revenue REAL,
    created_at TEXT,
    updated_at TEXT
);
"""

# Graduation thresholds — tune these as you learn what actually predicts a healthy blog.
GRADUATION_ARTICLE_THRESHOLD = 50
GRADUATION_SALES_THRESHOLD = 1


def get_conn(db_path):
    conn = sqlite3.connect(db_path)
    conn.row_factory = sqlite3.Row
    return conn


def init_db(db_path):
    conn = get_conn(db_path)
    conn.executescript(BLOGS_SCHEMA)
    conn.commit()
    conn.close()
    print(f"Blogs table ready in {db_path}")


def register(conn, name, niche_name=None, repo_url=None, status="candidate"):
    ts = now()
    conn.execute(
        """INSERT INTO blogs (name, niche_name, repo_url, status, created_at, updated_at)
           VALUES (?,?,?,?,?,?)
           ON CONFLICT(name) DO UPDATE SET
             niche_name=excluded.niche_name, repo_url=excluded.repo_url,
             status=excluded.status, updated_at=excluded.updated_at""",
        (name, niche_name, repo_url, status, ts, ts),
    )
    conn.commit()


def update_metrics(conn, name, articles=None, sales=None, token_cost=None, revenue=None, last_commit_at=None):
    ts = now()
    row = conn.execute("SELECT * FROM blogs WHERE name = ?", (name,)).fetchone()
    if not row:
        print(f"No blog registered named '{name}'. Register it first.", file=sys.stderr)
        sys.exit(1)

    new_articles = articles if articles is not None else row["article_count"]
    new_sales = sales if sales is not None else row["confirmed_sales"]
    first_sale_at = row["first_sale_at"]
    if new_sales and not first_sale_at:
        first_sale_at = ts

    conn.execute(
        """UPDATE blogs SET article_count=?, confirmed_sales=?, first_sale_at=?,
           monthly_token_cost=COALESCE(?, monthly_token_cost),
           monthly_revenue=COALESCE(?, monthly_revenue),
           last_commit_at=COALESCE(?, last_commit_at),
           updated_at=? WHERE name=?""",
        (new_articles, new_sales, first_sale_at, token_cost, revenue, last_commit_at, ts, name),
    )
    conn.commit()


def check_graduation(conn, name):
    row = conn.execute("SELECT * FROM blogs WHERE name = ?", (name,)).fetchone()
    if not row:
        print(f"No blog registered named '{name}'.", file=sys.stderr)
        sys.exit(1)

    if row["status"] == "graduated":
        print(f"'{name}' already graduated on {row['graduated_at']} (trigger: {row['graduation_trigger']})")
        return None

    reasons = []
    if row["confirmed_sales"] and row["confirmed_sales"] >= GRADUATION_SALES_THRESHOLD:
        reasons.append("first_sale")
    if row["article_count"] and row["article_count"] >= GRADUATION_ARTICLE_THRESHOLD:
        reasons.append("article_count")

    if reasons:
        print(f"'{name}' MEETS graduation criteria: {', '.join(reasons)}")
        print("Run `graduate` to fire the next-blog trigger, or do it manually if you want a final review first.")
        return reasons
    else:
        print(f"'{name}' does not yet meet graduation criteria "
              f"(articles: {row['article_count']}/{GRADUATION_ARTICLE_THRESHOLD}, "
              f"sales: {row['confirmed_sales']}/{GRADUATION_SALES_THRESHOLD})")
        return None


def graduate(conn, name, trigger="manual"):
    ts = now()
    conn.execute(
        "UPDATE blogs SET status='graduated', graduated_at=?, graduation_trigger=?, updated_at=? WHERE name=?",
        (ts, trigger, ts, name),
    )
    conn.commit()
    print(f"'{name}' marked graduated (trigger: {trigger}).")
    print("Next: run niche-scout-ops on a fresh candidate batch to pick the next niche to spawn.")


def list_blogs(conn, status=None):
    if status:
        rows = conn.execute("SELECT * FROM blogs WHERE status = ? ORDER BY updated_at DESC", (status,)).fetchall()
    else:
        rows = conn.execute("SELECT * FROM blogs ORDER BY updated_at DESC").fetchall()

    if not rows:
        print("No blogs registered yet.")
        return

    print(f"{'Name':<28} {'Status':<12} {'Articles':<9} {'Sales':<6} {'Health':<9} {'Last commit'}")
    for r in rows:
        print(f"{r['name']:<28} {r['status']:<12} {r['article_count'] or 0:<9} "
              f"{r['confirmed_sales'] or 0:<6} {r['health_status']:<9} {r['last_commit_at'] or 'n/a'}")


def _cli():
    p = argparse.ArgumentParser(description="Blog lifecycle / flywheel graduation tracker")
    p.add_argument("--db", required=True)
    sub = p.add_subparsers(dest="cmd", required=True)

    sub.add_parser("init")

    r = sub.add_parser("register")
    r.add_argument("name")
    r.add_argument("--niche", default=None)
    r.add_argument("--repo-url", default=None)
    r.add_argument("--status", default="candidate")

    u = sub.add_parser("update-metrics")
    u.add_argument("name")
    u.add_argument("--articles", type=int)
    u.add_argument("--sales", type=int)
    u.add_argument("--token-cost", type=float)
    u.add_argument("--revenue", type=float)
    u.add_argument("--last-commit-at", default=None)

    c = sub.add_parser("check-graduation")
    c.add_argument("name")

    g = sub.add_parser("graduate")
    g.add_argument("name")
    g.add_argument("--trigger", default="manual")

    ls = sub.add_parser("list")
    ls.add_argument("--status", default=None)

    args = p.parse_args()

    if args.cmd == "init":
        init_db(args.db)
        return

    conn = get_conn(args.db)

    if args.cmd == "register":
        register(conn, args.name, niche_name=args.niche, repo_url=args.repo_url, status=args.status)
        print(f"Registered blog: {args.name}")
    elif args.cmd == "update-metrics":
        update_metrics(conn, args.name, articles=args.articles, sales=args.sales,
                        token_cost=args.token_cost, revenue=args.revenue, last_commit_at=args.last_commit_at)
        print(f"Updated metrics for: {args.name}")
    elif args.cmd == "check-graduation":
        check_graduation(conn, args.name)
    elif args.cmd == "graduate":
        graduate(conn, args.name, trigger=args.trigger)
    elif args.cmd == "list":
        list_blogs(conn, status=args.status)

    conn.close()


if __name__ == "__main__":
    _cli()
