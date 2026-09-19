"""
database.py

Local persistence for run history (SQLite). Not part of the original
4-box architecture diagram, but needed so the dashboard can show more
than just "the last run's results" — every batch run is saved so past
history is browsable later.

One file, verification.db, created next to this script on first use.
"""

import sqlite3
import os
from datetime import datetime

import paths

DB_PATH = os.path.join(paths.app_data_dir(), "verification.db")


def init_db(db_path: str = DB_PATH) -> None:
    conn = sqlite3.connect(db_path)
    conn.execute(
        """
        CREATE TABLE IF NOT EXISTS runs (
            run_id INTEGER PRIMARY KEY AUTOINCREMENT,
            run_timestamp TEXT NOT NULL,
            job_card_count INTEGER NOT NULL,
            account_book_image_count INTEGER NOT NULL
        )
        """
    )
    conn.execute(
        """
        CREATE TABLE IF NOT EXISTS results (
            result_id INTEGER PRIMARY KEY AUTOINCREMENT,
            run_id INTEGER NOT NULL,
            serial_number TEXT,
            status TEXT NOT NULL,
            reason TEXT,
            job_card_client TEXT,
            job_card_service_total REAL,
            account_book_total REAL,
            account_book_line_count INTEGER,
            source_image TEXT,
            FOREIGN KEY (run_id) REFERENCES runs (run_id)
        )
        """
    )
    conn.commit()
    conn.close()


def save_run(
    results: list,
    job_card_count: int,
    account_book_image_count: int,
    db_path: str = DB_PATH,
) -> int:
    """Saves one batch run and all its per-job-card results. Returns the new run_id."""
    conn = sqlite3.connect(db_path)
    cur = conn.cursor()
    cur.execute(
        "INSERT INTO runs (run_timestamp, job_card_count, account_book_image_count) VALUES (?, ?, ?)",
        (datetime.now().isoformat(timespec="seconds"), job_card_count, account_book_image_count),
    )
    run_id = cur.lastrowid

    for r in results:
        cur.execute(
            """
            INSERT INTO results (
                run_id, serial_number, status, reason, job_card_client,
                job_card_service_total, account_book_total,
                account_book_line_count, source_image
            ) VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?)
            """,
            (
                run_id,
                r.get("serial_number"),
                r.get("status"),
                r.get("reason"),
                r.get("job_card_client"),
                r.get("job_card_service_total"),
                r.get("account_book_total"),
                r.get("account_book_line_count"),
                r.get("source_image"),
            ),
        )
    conn.commit()
    conn.close()
    return run_id


def list_runs(db_path: str = DB_PATH) -> list:
    """Returns every run, most recent first, with a quick status breakdown."""
    conn = sqlite3.connect(db_path)
    conn.row_factory = sqlite3.Row
    runs = conn.execute("SELECT * FROM runs ORDER BY run_id DESC").fetchall()

    out = []
    for run in runs:
        counts = conn.execute(
            "SELECT status, COUNT(*) as n FROM results WHERE run_id = ? GROUP BY status",
            (run["run_id"],),
        ).fetchall()
        out.append({**dict(run), "status_counts": {c["status"]: c["n"] for c in counts}})
    conn.close()
    return out


def get_run_results(run_id: int, db_path: str = DB_PATH) -> list:
    conn = sqlite3.connect(db_path)
    conn.row_factory = sqlite3.Row
    rows = conn.execute(
        "SELECT * FROM results WHERE run_id = ? ORDER BY result_id", (run_id,)
    ).fetchall()
    conn.close()
    return [dict(r) for r in rows]


def get_all_results(db_path: str = DB_PATH) -> list:
    """Every result across every run, most recent run first — used for
    a full history view across the whole project's lifetime."""
    conn = sqlite3.connect(db_path)
    conn.row_factory = sqlite3.Row
    rows = conn.execute(
        """
        SELECT results.*, runs.run_timestamp
        FROM results
        JOIN runs ON results.run_id = runs.run_id
        ORDER BY runs.run_id DESC, results.result_id
        """
    ).fetchall()
    conn.close()
    return [dict(r) for r in rows]
