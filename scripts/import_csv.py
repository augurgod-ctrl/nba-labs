"""
NBA Labs — import_csv.py
Importa trades.csv a nba_labs.db (SQLite)

Uso:
    python scripts/import_csv.py
"""

import csv
import sqlite3
from pathlib import Path

# ─── Rutas ─────────────────────────────────────────────────────────────────────
BASE_DIR  = Path(__file__).parent.parent
CSV_PATH  = BASE_DIR / "data" / "trades.csv"
DB_PATH   = BASE_DIR / "data" / "nba_labs.db"

# ─── Schema ────────────────────────────────────────────────────────────────────
CREATE_TABLE = """
CREATE TABLE IF NOT EXISTS trades (
    trade_id    TEXT PRIMARY KEY,
    date        TEXT NOT NULL,
    symbol      TEXT NOT NULL,
    session     TEXT NOT NULL,          -- NY | LON | ASIA
    regime      INTEGER NOT NULL,       -- 1-5 (Power 5 regime)
    gravity     INTEGER NOT NULL,       -- 0-100
    velocity    INTEGER NOT NULL,       -- 0-100
    htf_bias    INTEGER NOT NULL,       -- 1 = alcista | -1 = bajista | 0 = neutral
    air_pocket  INTEGER NOT NULL,       -- 0-100
    mae         REAL,                   -- Maximum Adverse Excursion (pts)
    mfe         REAL,                   -- Maximum Favorable Excursion (pts)
    result_r    REAL,                   -- Resultado en R
    notes       TEXT
);
"""

# ─── Importar ───────────────────────────────────────────────────────────────────
def import_trades():
    conn = sqlite3.connect(DB_PATH)
    cur  = conn.cursor()
    cur.execute(CREATE_TABLE)

    with open(CSV_PATH, newline="", encoding="utf-8") as f:
        reader = csv.DictReader(f)
        rows_inserted = 0
        rows_skipped  = 0

        for row in reader:
            try:
                cur.execute("""
                    INSERT OR IGNORE INTO trades
                    (trade_id, date, symbol, session, regime,
                     gravity, velocity, htf_bias, air_pocket,
                     mae, mfe, result_r, notes)
                    VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
                """, (
                    row["trade_id"],
                    row["date"],
                    row["symbol"],
                    row["session"],
                    int(row["regime"]),
                    int(row["gravity"]),
                    int(row["velocity"]),
                    int(row["htf_bias"]),
                    int(row["air_pocket"]),
                    float(row["mae"])       if row["mae"]       else None,
                    float(row["mfe"])       if row["mfe"]       else None,
                    float(row["result_r"])  if row["result_r"]  else None,
                    row.get("notes", ""),
                ))
                if cur.rowcount:
                    rows_inserted += 1
                else:
                    rows_skipped += 1
            except Exception as e:
                print(f"  ⚠️  Error en trade {row.get('trade_id', '?')}: {e}")

    conn.commit()
    conn.close()

    total = cur.execute  # solo para referencia
    print(f"✅  Importación completa")
    print(f"   Insertados : {rows_inserted}")
    print(f"   Omitidos   : {rows_skipped} (duplicados)")
    print(f"   DB         : {DB_PATH}")


if __name__ == "__main__":
    import_trades()
