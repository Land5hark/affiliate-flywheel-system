"""
db.py — Schema and helper functions for the affiliate graph database.

This is the single source of truth for niches, products, programs, and the
relationships between them. Obsidian notes are GENERATED from this database
(see generate_vault.py) — never hand-edit the vault notes and expect changes
to persist; edit here instead, then regenerate.

Usage as a library:
    from db import get_conn, add_niche, add_product, add_program, link_product_program, link_niche_product

Usage as a CLI:
    python db.py init                          # create tables
    python db.py add-niche "Balcony Drip Irrigation" --score 4.1 ...
    python db.py add-product "Barbed Tee Fitting" --layer connective --repeat 1
    python db.py add-program "Drip Depot" --network direct --commission "8% one-time"
    python db.py link-niche-product 1 3
    python db.py link-product-program 3 2 --notes "confirmed active 2026-07"
"""

import sqlite3
import argparse
import sys
from pathlib import Path
from datetime import datetime, timezone

DEFAULT_DB_PATH = "affiliate_graph.db"

SCHEMA = """
CREATE TABLE IF NOT EXISTS niches (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    name TEXT NOT NULL UNIQUE,
    difficulty_score REAL,
    affiliate_score REAL,
    volume_score REAL,
    depth_score REAL,
    seasonality_score REAL,
    weighted_score REAL,
    status TEXT DEFAULT 'candidate',   -- candidate | active | rejected
    notes TEXT,
    created_at TEXT,
    updated_at TEXT
);

CREATE TABLE IF NOT EXISTS products (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    name TEXT NOT NULL UNIQUE,
    layer TEXT,                        -- hero | consumable | connective | tool | adjacent | upgrade | failure_mode
    est_price_low REAL,
    est_price_high REAL,
    repeat_purchase INTEGER DEFAULT 0, -- 0/1
    commission_score REAL,
    cookie_score REAL,
    repeat_score REAL,
    reliability_score REAL,
    research_score REAL,
    weighted_score REAL,
    notes TEXT,
    created_at TEXT,
    updated_at TEXT
);

CREATE TABLE IF NOT EXISTS programs (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    brand_or_merchant TEXT NOT NULL,
    network TEXT,                      -- amazon | shareasale | cj | impact | rakuten | awin | clickbank | direct | other
    commission_structure TEXT,
    cookie_duration TEXT,
    application_status TEXT DEFAULT 'not_researched',
    program_url TEXT,
    last_verified TEXT,
    notes TEXT,
    created_at TEXT,
    updated_at TEXT,
    UNIQUE(brand_or_merchant, network)
);

CREATE TABLE IF NOT EXISTS niche_products (
    niche_id INTEGER NOT NULL,
    product_id INTEGER NOT NULL,
    PRIMARY KEY (niche_id, product_id),
    FOREIGN KEY (niche_id) REFERENCES niches(id),
    FOREIGN KEY (product_id) REFERENCES products(id)
);

CREATE TABLE IF NOT EXISTS product_programs (
    product_id INTEGER NOT NULL,
    program_id INTEGER NOT NULL,
    notes TEXT,
    PRIMARY KEY (product_id, program_id),
    FOREIGN KEY (product_id) REFERENCES products(id),
    FOREIGN KEY (program_id) REFERENCES programs(id)
);
"""


def now():
    return datetime.now(timezone.utc).isoformat(timespec="seconds")


def get_conn(db_path=DEFAULT_DB_PATH):
    conn = sqlite3.connect(db_path)
    conn.execute("PRAGMA foreign_keys = ON;")
    conn.row_factory = sqlite3.Row
    return conn


def init_db(db_path=DEFAULT_DB_PATH):
    conn = get_conn(db_path)
    conn.executescript(SCHEMA)
    conn.commit()
    conn.close()
    print(f"Initialized database at {db_path}")


def add_niche(conn, name, **scores):
    ts = now()
    conn.execute(
        """INSERT INTO niches (name, difficulty_score, affiliate_score, volume_score,
           depth_score, seasonality_score, weighted_score, status, notes, created_at, updated_at)
           VALUES (?,?,?,?,?,?,?,?,?,?,?)
           ON CONFLICT(name) DO UPDATE SET
             difficulty_score=excluded.difficulty_score,
             affiliate_score=excluded.affiliate_score,
             volume_score=excluded.volume_score,
             depth_score=excluded.depth_score,
             seasonality_score=excluded.seasonality_score,
             weighted_score=excluded.weighted_score,
             status=excluded.status,
             notes=excluded.notes,
             updated_at=excluded.updated_at
        """,
        (
            name,
            scores.get("difficulty"), scores.get("affiliate"), scores.get("volume"),
            scores.get("depth"), scores.get("seasonality"), scores.get("weighted"),
            scores.get("status", "candidate"), scores.get("notes"), ts, ts,
        ),
    )
    conn.commit()


def add_product(conn, name, layer=None, price_low=None, price_high=None, repeat=0, **scores):
    ts = now()
    conn.execute(
        """INSERT INTO products (name, layer, est_price_low, est_price_high, repeat_purchase,
           commission_score, cookie_score, repeat_score, reliability_score, research_score,
           weighted_score, notes, created_at, updated_at)
           VALUES (?,?,?,?,?,?,?,?,?,?,?,?,?,?)
           ON CONFLICT(name) DO UPDATE SET
             layer=excluded.layer,
             est_price_low=excluded.est_price_low,
             est_price_high=excluded.est_price_high,
             repeat_purchase=excluded.repeat_purchase,
             commission_score=excluded.commission_score,
             cookie_score=excluded.cookie_score,
             repeat_score=excluded.repeat_score,
             reliability_score=excluded.reliability_score,
             research_score=excluded.research_score,
             weighted_score=excluded.weighted_score,
             notes=excluded.notes,
             updated_at=excluded.updated_at
        """,
        (
            name, layer, price_low, price_high, int(bool(repeat)),
            scores.get("commission"), scores.get("cookie"), scores.get("repeat_score"),
            scores.get("reliability"), scores.get("research"), scores.get("weighted"),
            scores.get("notes"), ts, ts,
        ),
    )
    conn.commit()


def add_program(conn, brand, network=None, commission_structure=None, cookie_duration=None,
                 status="not_researched", url=None, last_verified=None, notes=None):
    ts = now()
    conn.execute(
        """INSERT INTO programs (brand_or_merchant, network, commission_structure, cookie_duration,
           application_status, program_url, last_verified, notes, created_at, updated_at)
           VALUES (?,?,?,?,?,?,?,?,?,?)
           ON CONFLICT(brand_or_merchant, network) DO UPDATE SET
             commission_structure=excluded.commission_structure,
             cookie_duration=excluded.cookie_duration,
             application_status=excluded.application_status,
             program_url=excluded.program_url,
             last_verified=excluded.last_verified,
             notes=excluded.notes,
             updated_at=excluded.updated_at
        """,
        (brand, network, commission_structure, cookie_duration, status, url,
         last_verified or ts[:10], notes, ts, ts),
    )
    conn.commit()


def link_niche_product(conn, niche_id, product_id):
    conn.execute(
        "INSERT OR IGNORE INTO niche_products (niche_id, product_id) VALUES (?,?)",
        (niche_id, product_id),
    )
    conn.commit()


def link_product_program(conn, product_id, program_id, notes=None):
    conn.execute(
        """INSERT INTO product_programs (product_id, program_id, notes) VALUES (?,?,?)
           ON CONFLICT(product_id, program_id) DO UPDATE SET notes=excluded.notes""",
        (product_id, program_id, notes),
    )
    conn.commit()


def find_id(conn, table, name_col, name):
    row = conn.execute(f"SELECT id FROM {table} WHERE {name_col} = ?", (name,)).fetchone()
    return row["id"] if row else None


def _cli():
    p = argparse.ArgumentParser(description="Affiliate graph database CLI")
    p.add_argument("--db", default=DEFAULT_DB_PATH)
    sub = p.add_subparsers(dest="cmd", required=True)

    sub.add_parser("init")

    an = sub.add_parser("add-niche")
    an.add_argument("name")
    an.add_argument("--difficulty", type=float)
    an.add_argument("--affiliate", type=float)
    an.add_argument("--volume", type=float)
    an.add_argument("--depth", type=float)
    an.add_argument("--seasonality", type=float)
    an.add_argument("--weighted", type=float)
    an.add_argument("--status", default="candidate")
    an.add_argument("--notes", default="")

    ap = sub.add_parser("add-product")
    ap.add_argument("name")
    ap.add_argument("--layer", default="")
    ap.add_argument("--price-low", type=float, dest="price_low")
    ap.add_argument("--price-high", type=float, dest="price_high")
    ap.add_argument("--repeat", type=int, default=0)
    ap.add_argument("--commission", type=float)
    ap.add_argument("--cookie", type=float)
    ap.add_argument("--repeat-score", type=float, dest="repeat_score")
    ap.add_argument("--reliability", type=float)
    ap.add_argument("--research", type=float)
    ap.add_argument("--weighted", type=float)
    ap.add_argument("--notes", default="")

    apr = sub.add_parser("add-program")
    apr.add_argument("brand")
    apr.add_argument("--network", default="")
    apr.add_argument("--commission-structure", dest="commission_structure", default="")
    apr.add_argument("--cookie-duration", dest="cookie_duration", default="")
    apr.add_argument("--status", default="not_researched")
    apr.add_argument("--url", default="")
    apr.add_argument("--last-verified", dest="last_verified", default="")
    apr.add_argument("--notes", default="")

    lnp = sub.add_parser("link-niche-product")
    lnp.add_argument("niche_name")
    lnp.add_argument("product_name")

    lpp = sub.add_parser("link-product-program")
    lpp.add_argument("product_name")
    lpp.add_argument("program_brand")
    lpp.add_argument("--notes", default="")

    args = p.parse_args()

    if args.cmd == "init":
        init_db(args.db)
        return

    conn = get_conn(args.db)

    if args.cmd == "add-niche":
        add_niche(conn, args.name, difficulty=args.difficulty, affiliate=args.affiliate,
                   volume=args.volume, depth=args.depth, seasonality=args.seasonality,
                   weighted=args.weighted, status=args.status, notes=args.notes)
        print(f"Added/updated niche: {args.name}")

    elif args.cmd == "add-product":
        add_product(conn, args.name, layer=args.layer, price_low=args.price_low,
                     price_high=args.price_high, repeat=args.repeat, commission=args.commission,
                     cookie=args.cookie, repeat_score=args.repeat_score, reliability=args.reliability,
                     research=args.research, weighted=args.weighted, notes=args.notes)
        print(f"Added/updated product: {args.name}")

    elif args.cmd == "add-program":
        add_program(conn, args.brand, network=args.network, commission_structure=args.commission_structure,
                     cookie_duration=args.cookie_duration, status=args.status, url=args.url,
                     last_verified=args.last_verified, notes=args.notes)
        print(f"Added/updated program: {args.brand}")

    elif args.cmd == "link-niche-product":
        nid = find_id(conn, "niches", "name", args.niche_name)
        pid = find_id(conn, "products", "name", args.product_name)
        if not nid or not pid:
            print("Error: niche or product not found. Add them first.", file=sys.stderr)
            sys.exit(1)
        link_niche_product(conn, nid, pid)
        print(f"Linked niche '{args.niche_name}' <-> product '{args.product_name}'")

    elif args.cmd == "link-product-program":
        pid = find_id(conn, "products", "name", args.product_name)
        prid = find_id(conn, "programs", "brand_or_merchant", args.program_brand)
        if not pid or not prid:
            print("Error: product or program not found. Add them first.", file=sys.stderr)
            sys.exit(1)
        link_product_program(conn, pid, prid, notes=args.notes)
        print(f"Linked product '{args.product_name}' <-> program '{args.program_brand}'")

    conn.close()


if __name__ == "__main__":
    _cli()
