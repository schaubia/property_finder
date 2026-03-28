"""
Persistent watchlist and saved searches using SQLite.
Database stored at: bg_property_finder/data/watchlist.db
"""
import sqlite3
import json
import datetime
import os

DB_PATH = os.path.join(os.path.dirname(__file__), "watchlist.db")


def _conn():
    return sqlite3.connect(DB_PATH)


def init_db():
    """Create tables if they don't exist."""
    with _conn() as c:
        c.execute("""
            CREATE TABLE IF NOT EXISTS watchlist (
                id          INTEGER PRIMARY KEY AUTOINCREMENT,
                prop_id     INTEGER,
                title       TEXT,
                city        TEXT,
                neighborhood TEXT,
                type_bg     TEXT,
                type_en     TEXT,
                area_sqm    REAL,
                price_eur   REAL,
                price_bgn   REAL,
                price_per_sqm REAL,
                floor       INTEGER,
                floors_total INTEGER,
                rooms       INTEGER,
                construction_type TEXT,
                features    TEXT,          -- JSON list
                description TEXT,
                agency      TEXT,
                contact     TEXT,
                listing_date TEXT,
                added_at    TEXT,
                notes       TEXT DEFAULT ''
            )
        """)
        c.execute("""
            CREATE TABLE IF NOT EXISTS saved_searches (
                id          INTEGER PRIMARY KEY AUTOINCREMENT,
                name        TEXT,
                filters     TEXT,          -- JSON dict
                saved_at    TEXT,
                alert_email TEXT DEFAULT ''
            )
        """)
        c.execute("""
            CREATE TABLE IF NOT EXISTS mortgage_scenarios (
                id          INTEGER PRIMARY KEY AUTOINCREMENT,
                name        TEXT,
                loan_eur    REAL,
                rate_pct    REAL,
                term_years  INTEGER,
                bank_id     TEXT,
                monthly_pmt REAL,
                total_paid  REAL,
                created_at  TEXT
            )
        """)
        c.commit()


# ── Watchlist ──────────────────────────────────────────────────────────────────

def add_to_watchlist(row: dict, notes: str = "") -> bool:
    """Add a property row (dict) to watchlist. Returns False if already exists."""
    init_db()
    with _conn() as c:
        exists = c.execute("SELECT id FROM watchlist WHERE prop_id=?", (row["id"],)).fetchone()
        if exists:
            return False
        c.execute("""
            INSERT INTO watchlist
            (prop_id, title, city, neighborhood, type_bg, type_en, area_sqm,
             price_eur, price_bgn, price_per_sqm, floor, floors_total, rooms,
             construction_type, features, description, agency, contact,
             listing_date, added_at, notes)
            VALUES (?,?,?,?,?,?,?,?,?,?,?,?,?,?,?,?,?,?,?,?,?)
        """, (
            row["id"], row["title"], row["city"], row["neighborhood"],
            row["type_bg"], row["type_en"], row["area_sqm"],
            row["price_eur"], row["price_bgn"], row["price_per_sqm"],
            row["floor"], row["floors_total"], row["rooms"],
            row["construction_type"],
            json.dumps(row["features"], ensure_ascii=False),
            row["description"], row["agency"], row["contact"],
            row["listing_date"],
            datetime.datetime.now().strftime("%Y-%m-%d %H:%M"),
            notes
        ))
        c.commit()
    return True


def remove_from_watchlist(prop_id: int):
    init_db()
    with _conn() as c:
        c.execute("DELETE FROM watchlist WHERE prop_id=?", (prop_id,))
        c.commit()


def get_watchlist() -> list[dict]:
    init_db()
    with _conn() as c:
        cur = c.execute("SELECT * FROM watchlist ORDER BY added_at DESC")
        cols = [d[0] for d in cur.description]
        rows = cur.fetchall()
    result = []
    for row in rows:
        d = dict(zip(cols, row))
        d["features"] = json.loads(d["features"]) if d["features"] else []
        result.append(d)
    return result


def is_in_watchlist(prop_id: int) -> bool:
    init_db()
    with _conn() as c:
        return bool(c.execute("SELECT id FROM watchlist WHERE prop_id=?", (prop_id,)).fetchone())


def update_notes(prop_id: int, notes: str):
    init_db()
    with _conn() as c:
        c.execute("UPDATE watchlist SET notes=? WHERE prop_id=?", (notes, prop_id))
        c.commit()


def watchlist_count() -> int:
    init_db()
    with _conn() as c:
        return c.execute("SELECT COUNT(*) FROM watchlist").fetchone()[0]


# ── Saved searches ─────────────────────────────────────────────────────────────

def save_search(name: str, filters: dict, alert_email: str = "") -> int:
    init_db()
    with _conn() as c:
        cur = c.execute("""
            INSERT INTO saved_searches (name, filters, saved_at, alert_email)
            VALUES (?,?,?,?)
        """, (name, json.dumps(filters, ensure_ascii=False),
              datetime.datetime.now().strftime("%Y-%m-%d %H:%M"), alert_email))
        c.commit()
        return cur.lastrowid


def get_saved_searches() -> list[dict]:
    init_db()
    with _conn() as c:
        cur = c.execute("SELECT * FROM saved_searches ORDER BY saved_at DESC")
        cols = [d[0] for d in cur.description]
        rows = cur.fetchall()
    result = []
    for row in rows:
        d = dict(zip(cols, row))
        d["filters"] = json.loads(d["filters"]) if d["filters"] else {}
        result.append(d)
    return result


def delete_saved_search(search_id: int):
    init_db()
    with _conn() as c:
        c.execute("DELETE FROM saved_searches WHERE id=?", (search_id,))
        c.commit()


# ── Mortgage scenarios ─────────────────────────────────────────────────────────

def save_mortgage_scenario(name: str, loan_eur: float, rate_pct: float,
                            term_years: int, bank_id: str,
                            monthly_pmt: float, total_paid: float) -> int:
    init_db()
    with _conn() as c:
        cur = c.execute("""
            INSERT INTO mortgage_scenarios
            (name, loan_eur, rate_pct, term_years, bank_id, monthly_pmt, total_paid, created_at)
            VALUES (?,?,?,?,?,?,?,?)
        """, (name, loan_eur, rate_pct, term_years, bank_id,
              monthly_pmt, total_paid,
              datetime.datetime.now().strftime("%Y-%m-%d %H:%M")))
        c.commit()
        return cur.lastrowid


def get_mortgage_scenarios() -> list[dict]:
    init_db()
    with _conn() as c:
        cur = c.execute("SELECT * FROM mortgage_scenarios ORDER BY created_at DESC")
        cols = [d[0] for d in cur.description]
        rows = cur.fetchall()
    return [dict(zip(cols, row)) for row in rows]


def delete_mortgage_scenario(scenario_id: int):
    init_db()
    with _conn() as c:
        c.execute("DELETE FROM mortgage_scenarios WHERE id=?", (scenario_id,))
        c.commit()
