"""SQLite persistence layer for jobtrack."""

import os
import sqlite3
from datetime import date
from typing import List, Optional

from .models import Application, STATUSES


def default_db_path() -> str:
    """Return the default database location (~/.jobtrack/jobtrack.db)."""
    home = os.path.expanduser("~")
    return os.path.join(home, ".jobtrack", "jobtrack.db")


class Database:
    """A thin wrapper around a SQLite connection."""

    def __init__(self, path: Optional[str] = None):
        self.path = path or default_db_path()
        os.makedirs(os.path.dirname(os.path.abspath(self.path)), exist_ok=True)
        self.conn = sqlite3.connect(self.path)
        self.conn.row_factory = sqlite3.Row
        self._create_schema()

    def _create_schema(self) -> None:
        self.conn.execute(
            """
            CREATE TABLE IF NOT EXISTS applications (
                id         INTEGER PRIMARY KEY AUTOINCREMENT,
                company    TEXT NOT NULL,
                position   TEXT NOT NULL,
                status     TEXT NOT NULL DEFAULT 'applied',
                applied_on TEXT NOT NULL DEFAULT '',
                location   TEXT NOT NULL DEFAULT '',
                url        TEXT NOT NULL DEFAULT '',
                salary     TEXT NOT NULL DEFAULT '',
                notes      TEXT NOT NULL DEFAULT ''
            )
            """
        )
        self.conn.commit()

    def add(self, app: Application) -> int:
        app.validate()
        if not app.applied_on:
            app.applied_on = date.today().isoformat()
        cur = self.conn.execute(
            """
            INSERT INTO applications
                (company, position, status, applied_on, location, url, salary, notes)
            VALUES (?, ?, ?, ?, ?, ?, ?, ?)
            """,
            (
                app.company, app.position, app.status, app.applied_on,
                app.location, app.url, app.salary, app.notes,
            ),
        )
        self.conn.commit()
        return cur.lastrowid

    def list(self, status: Optional[str] = None) -> List[Application]:
        if status is not None and status not in STATUSES:
            raise ValueError(f"invalid status '{status}'")
        if status:
            rows = self.conn.execute(
                "SELECT * FROM applications WHERE status = ? ORDER BY applied_on DESC, id DESC",
                (status,),
            ).fetchall()
        else:
            rows = self.conn.execute(
                "SELECT * FROM applications ORDER BY applied_on DESC, id DESC"
            ).fetchall()
        return [self._row_to_app(r) for r in rows]

    def get(self, app_id: int) -> Optional[Application]:
        row = self.conn.execute(
            "SELECT * FROM applications WHERE id = ?", (app_id,)
        ).fetchone()
        return self._row_to_app(row) if row else None

    def set_status(self, app_id: int, status: str) -> bool:
        if status not in STATUSES:
            raise ValueError(f"invalid status '{status}'")
        cur = self.conn.execute(
            "UPDATE applications SET status = ? WHERE id = ?", (status, app_id)
        )
        self.conn.commit()
        return cur.rowcount > 0

    def delete(self, app_id: int) -> bool:
        cur = self.conn.execute("DELETE FROM applications WHERE id = ?", (app_id,))
        self.conn.commit()
        return cur.rowcount > 0

    @staticmethod
    def _row_to_app(row: sqlite3.Row) -> Application:
        return Application(
            id=row["id"],
            company=row["company"],
            position=row["position"],
            status=row["status"],
            applied_on=row["applied_on"],
            location=row["location"],
            url=row["url"],
            salary=row["salary"],
            notes=row["notes"],
        )

    def close(self) -> None:
        self.conn.close()
