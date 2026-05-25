#!/usr/bin/env python3
"""paprika — search the local Paprika 3 recipe database (read-only).

Usage:
    paprika [--md] [--exact] [--cap N] [--db PATH] <terms>...

Examples:
    paprika split pea                   # JSON, all matches
    paprika quinoa pepper               # AND across terms
    paprika --md split pea              # human-readable markdown
    paprika --exact "+QUINOA peppers - Mexican Quinoa Stuffed Peppers"

Output:
    Default JSON. With --md, formatted markdown (auto-collapses on many hits).

Fields returned per recipe:
    name, source, source_url, rating (0-5), ingredients, directions, uid

Notes:
    Search is name-only, case-insensitive, multi-term = AND.
    Opens the Paprika SQLite DB read-only via URI mode.
"""

import argparse
import json
import sqlite3
import sys
from pathlib import Path

DEFAULT_DB = (
    Path.home()
    / "Library/Group Containers/72KVKW69K8.com.hindsightlabs.paprika.mac.v3"
    / "Data/Database/Paprika.sqlite"
)
DEFAULT_CAP = 50


def open_db(path: Path) -> sqlite3.Connection:
    if not path.exists():
        sys.exit(f"paprika: database not found at {path}")
    conn = sqlite3.connect(f"file:{path}?mode=ro", uri=True)
    conn.row_factory = sqlite3.Row
    return conn


def search(conn, terms, exact, cap):
    if exact:
        where = "ZNAME = ?"
        params = [" ".join(terms)]
    else:
        where = " AND ".join(["ZNAME LIKE ? COLLATE NOCASE"] * len(terms))
        params = [f"%{t}%" for t in terms]
    sql = (
        "SELECT ZNAME, ZSOURCE, ZSOURCEURL, ZRATING, ZINGREDIENTS, ZDIRECTIONS, ZUID "
        f"FROM ZRECIPE WHERE {where} ORDER BY ZNAME LIMIT ?"
    )
    params.append(cap)
    return conn.execute(sql, params).fetchall()


def closest_names(conn, terms, n=3):
    where = " OR ".join(["ZNAME LIKE ? COLLATE NOCASE"] * len(terms))
    params = [f"%{t}%" for t in terms] + [n]
    sql = f"SELECT ZNAME FROM ZRECIPE WHERE {where} ORDER BY ZNAME LIMIT ?"
    return [r["ZNAME"] for r in conn.execute(sql, params).fetchall()]


def row_to_dict(row):
    return {
        "name": row["ZNAME"] or "",
        "source": row["ZSOURCE"] or "",
        "source_url": row["ZSOURCEURL"] or "",
        "rating": int(row["ZRATING"] or 0),
        "ingredients": row["ZINGREDIENTS"] or "",
        "directions": row["ZDIRECTIONS"] or "",
        "uid": row["ZUID"] or "",
    }


def emit_json(query, rows):
    out = {
        "query": query,
        "matches": len(rows),
        "recipes": [row_to_dict(r) for r in rows],
    }
    print(json.dumps(out, indent=2, ensure_ascii=False))


def emit_md(query, rows, conn, terms):
    n = len(rows)
    if n == 0:
        print(f"No match for: `{query}`")
        close = closest_names(conn, terms, 3)
        if close:
            print("\nClosest names:")
            for name in close:
                print(f"- {name}")
        return

    if n >= 6:
        print(f"{n} matches for `{query}` — refine your query:\n")
        for r in rows:
            print(f"- {r['ZNAME']}")
        return

    for i, r in enumerate(rows):
        d = row_to_dict(r)
        if i > 0:
            print("\n---\n")
        print(f"## {d['name']}\n")
        if d["ingredients"]:
            print("**Ingredients**\n")
            print(d["ingredients"].strip())
            print()
        if d["directions"]:
            print("**Directions**\n")
            print(d["directions"].strip())
            print()
        footer = []
        if d["rating"]:
            footer.append("★" * d["rating"] + "☆" * (5 - d["rating"]))
        if d["source"] and d["source_url"]:
            footer.append(f"[{d['source']}]({d['source_url']})")
        elif d["source_url"]:
            footer.append(d["source_url"])
        elif d["source"]:
            footer.append(d["source"])
        if footer:
            print("—  " + " · ".join(footer))


def main():
    p = argparse.ArgumentParser(
        prog="paprika",
        description="Search the local Paprika 3 recipe database.",
    )
    p.add_argument("terms", nargs="+", help="Search terms (AND across terms; LIKE %%term%% on recipe name)")
    p.add_argument("--md", action="store_true", help="Markdown output (default: JSON)")
    p.add_argument("--exact", action="store_true", help="Exact name match (joined terms)")
    p.add_argument("--cap", type=int, default=DEFAULT_CAP, help=f"Max results (default {DEFAULT_CAP})")
    p.add_argument("--db", type=Path, default=DEFAULT_DB, help="Override DB path")
    args = p.parse_args()

    conn = open_db(args.db)
    rows = search(conn, args.terms, args.exact, args.cap)
    query = " ".join(args.terms)

    if args.md:
        emit_md(query, rows, conn, args.terms)
    else:
        emit_json(query, rows)


if __name__ == "__main__":
    main()
