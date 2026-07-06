"""
generate_vault.py — Regenerates Obsidian markdown notes from the affiliate graph database.

The database (affiliate_graph.db) is the source of truth. This script wipes and
rebuilds the generated note folders every run, so it's always safe to re-run —
never hand-edit files inside Niches/, Products/, or Programs/, since those edits
will be overwritten. Add an "Overview.md" or other manually-written notes
elsewhere in the vault if you want hand-authored content alongside the generated
graph.

Usage:
    python generate_vault.py --db affiliate_graph.db --vault /path/to/ObsidianVault
"""

import argparse
import shutil
from pathlib import Path
from db import get_conn

GENERATED_SUBFOLDER = "Affiliate Graph"  # everything generated lives under this folder in the vault


def slug(name):
    return name.strip()


def wikilink(name):
    return f"[[{slug(name)}]]"


def write_note(folder: Path, name: str, content: str):
    folder.mkdir(parents=True, exist_ok=True)
    # sanitize filename (Obsidian is tolerant, but avoid path separators)
    safe_name = slug(name).replace("/", "-")
    path = folder / f"{safe_name}.md"
    path.write_text(content, encoding="utf-8")


def generate(db_path: str, vault_path: str):
    conn = get_conn(db_path)
    root = Path(vault_path) / GENERATED_SUBFOLDER

    # Wipe and rebuild the generated folder only — never touches the rest of the vault
    if root.exists():
        shutil.rmtree(root)
    niches_dir = root / "Niches"
    products_dir = root / "Products"
    programs_dir = root / "Programs"

    niches = conn.execute("SELECT * FROM niches").fetchall()
    products = conn.execute("SELECT * FROM products").fetchall()
    programs = conn.execute("SELECT * FROM programs").fetchall()

    # --- Niche notes ---
    for n in niches:
        linked_products = conn.execute(
            """SELECT p.* FROM products p
               JOIN niche_products np ON np.product_id = p.id
               WHERE np.niche_id = ?""",
            (n["id"],),
        ).fetchall()

        lines = [
            "---",
            f'status: {n["status"] or "candidate"}',
            f'weighted_score: {n["weighted_score"]}',
            "---",
            "",
            f'# {n["name"]}',
            "",
            "## Niche Scores",
            f'- Difficulty: {n["difficulty_score"]}',
            f'- Affiliate availability: {n["affiliate_score"]}',
            f'- Volume: {n["volume_score"]}',
            f'- Content depth: {n["depth_score"]}',
            f'- Seasonality: {n["seasonality_score"]}',
            f'- **Weighted score: {n["weighted_score"]}**',
            "",
            "## Products in this niche",
        ]
        if linked_products:
            for p in linked_products:
                lines.append(f'- {wikilink(p["name"])} (score: {p["weighted_score"]})')
        else:
            lines.append("- _No products linked yet — run product-map-ops and link them._")

        if n["notes"]:
            lines += ["", "## Notes", n["notes"]]

        write_note(niches_dir, n["name"], "\n".join(lines))

    # --- Product notes ---
    for p in products:
        linked_niches = conn.execute(
            """SELECT n.* FROM niches n
               JOIN niche_products np ON np.niche_id = n.id
               WHERE np.product_id = ?""",
            (p["id"],),
        ).fetchall()
        linked_programs = conn.execute(
            """SELECT pr.*, pp.notes AS link_notes FROM programs pr
               JOIN product_programs pp ON pp.program_id = pr.id
               WHERE pp.product_id = ?""",
            (p["id"],),
        ).fetchall()

        lines = [
            "---",
            f'layer: {p["layer"] or "unclassified"}',
            f'repeat_purchase: {"true" if p["repeat_purchase"] else "false"}',
            f'weighted_score: {p["weighted_score"]}',
            "---",
            "",
            f'# {p["name"]}',
            "",
            f'**Layer:** {p["layer"] or "unclassified"}  ',
            f'**Repeat purchase:** {"Yes" if p["repeat_purchase"] else "No"}  ',
            f'**Est. price range:** {p["est_price_low"]}–{p["est_price_high"]}',
            "",
            "## Product Economics Scores",
            f'- Commission structure: {p["commission_score"]}',
            f'- Cookie duration: {p["cookie_score"]}',
            f'- Repeat purchase potential: {p["repeat_score"]}',
            f'- Program reliability: {p["reliability_score"]}',
            f'- Research-intent fit: {p["research_score"]}',
            f'- **Weighted score: {p["weighted_score"]}**',
            "",
            "## Found in niches",
        ]
        lines += [f'- {wikilink(n["name"])}' for n in linked_niches] or ["- _Not linked to a niche yet._"]

        lines += ["", "## Available affiliate programs"]
        if linked_programs:
            for pr in linked_programs:
                note_bit = f' — {pr["link_notes"]}' if pr["link_notes"] else ""
                lines.append(f'- {wikilink(pr["brand_or_merchant"])} ({pr["network"]}, {pr["application_status"]}){note_bit}')
        else:
            lines.append("- _No program found/linked yet — run program-scout-ops._")

        if p["notes"]:
            lines += ["", "## Notes", p["notes"]]

        write_note(products_dir, p["name"], "\n".join(lines))

    # --- Program notes ---
    for pr in programs:
        linked_products = conn.execute(
            """SELECT p.* FROM products p
               JOIN product_programs pp ON pp.product_id = p.id
               WHERE pp.program_id = ?""",
            (pr["id"],),
        ).fetchall()

        lines = [
            "---",
            f'network: {pr["network"] or "unknown"}',
            f'application_status: {pr["application_status"]}',
            f'last_verified: {pr["last_verified"]}',
            "---",
            "",
            f'# {pr["brand_or_merchant"]}',
            "",
            f'**Network:** {pr["network"] or "unknown"}  ',
            f'**Commission structure:** {pr["commission_structure"] or "unverified"}  ',
            f'**Cookie duration:** {pr["cookie_duration"] or "unverified"}  ',
            f'**Application status:** {pr["application_status"]}  ',
            f'**URL:** {pr["program_url"] or "n/a"}  ',
            f'**Last verified:** {pr["last_verified"]}',
            "",
            "## Products carried",
        ]
        lines += [f'- {wikilink(p["name"])}' for p in linked_products] or ["- _Not linked to any product yet._"]

        if pr["notes"]:
            lines += ["", "## Notes", pr["notes"]]

        write_note(programs_dir, pr["brand_or_merchant"], "\n".join(lines))

    # --- Index note ---
    index_lines = [
        "# Affiliate Graph — Index",
        "",
        f"Generated from `{db_path}`. Do not hand-edit notes in this folder — edit the database and regenerate.",
        "",
        f"- {len(niches)} niches",
        f"- {len(products)} products",
        f"- {len(programs)} programs",
        "",
        "## Niches",
    ]
    index_lines += [f'- {wikilink(n["name"])} (score: {n["weighted_score"]}, {n["status"]})' for n in niches]
    write_note(root, "Index", "\n".join(index_lines))

    conn.close()
    print(f"Vault generated at {root}")
    print(f"  {len(niches)} niches, {len(products)} products, {len(programs)} programs")


if __name__ == "__main__":
    ap = argparse.ArgumentParser()
    ap.add_argument("--db", default="affiliate_graph.db")
    ap.add_argument("--vault", required=True, help="Path to the root of the Obsidian vault")
    args = ap.parse_args()
    generate(args.db, args.vault)
