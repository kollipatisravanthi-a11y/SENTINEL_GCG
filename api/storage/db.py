"""SQLite (local) or LibSQL (Turso) storage layer."""

from __future__ import annotations

import os
import sqlite3
import time
from dataclasses import dataclass
from pathlib import Path
from typing import Iterable, Any

try:
    import libsql_client
except ImportError:
    libsql_client = None


@dataclass(frozen=True)
class ReportRecord:
    report_id: str
    encrypted_blob: bytes
    merkle_index: int
    submitted_at: int
    node_id: str
    route_path: str


class ReportStore:
    def __init__(self, db_path: Path | str):
        self.db_path = Path(db_path)
        self.url = os.getenv("TURSO_DATABASE_URL")
        self.token = os.getenv("TURSO_AUTH_TOKEN")

        if not self.url:
            self.db_path.parent.mkdir(parents=True, exist_ok=True)

    def initialize(self) -> None:
        with self._connect() as conn:
            conn.execute(
                """
                CREATE TABLE IF NOT EXISTS reports (
                    report_id TEXT PRIMARY KEY,
                    encrypted_blob BLOB NOT NULL,
                    merkle_index INTEGER NOT NULL,
                    submitted_at INTEGER NOT NULL,
                    node_id TEXT NOT NULL,
                    route_path TEXT NOT NULL DEFAULT ''
                )
                """
            )
            conn.execute(
                "CREATE INDEX IF NOT EXISTS idx_reports_merkle_index "
                "ON reports(merkle_index)"
            )

    def add_report(
        self,
        report_id: str,
        encrypted_blob: bytes,
        node_id: str,
        route_path: Iterable[str],
    ) -> ReportRecord:
        with self._connect() as conn:
            merkle_index = self.count_reports(conn)
            submitted_at = int(time.time())
            route_text = " -> ".join(route_path)

            # Convert to bytes for blobs in Turso/libsql
            blob_data = encrypted_blob

            conn.execute(
                """
                INSERT INTO reports (
                    report_id,
                    encrypted_blob,
                    merkle_index,
                    submitted_at,
                    node_id,
                    route_path
                )
                VALUES (?, ?, ?, ?, ?, ?)
                """,
                (
                    report_id,
                    blob_data,
                    merkle_index,
                    submitted_at,
                    node_id,
                    route_text,
                ),
            )
            return ReportRecord(
                report_id=report_id,
                encrypted_blob=encrypted_blob,
                merkle_index=merkle_index,
                submitted_at=submitted_at,
                node_id=node_id,
                route_path=route_text,
            )

    def get_report(self, report_id: str) -> ReportRecord | None:
        with self._connect() as conn:
            res = conn.execute(
                """
                SELECT report_id, encrypted_blob, merkle_index, submitted_at, node_id, route_path
                FROM reports
                WHERE report_id = ?
                """,
                (report_id,),
            )
            row = res.fetchone()
        return self._row_to_record(row) if row else None

    def list_reports(self) -> list[ReportRecord]:
        with self._connect() as conn:
            res = conn.execute(
                """
                SELECT report_id, encrypted_blob, merkle_index, submitted_at, node_id, route_path
                FROM reports
                ORDER BY merkle_index ASC
                """
            )
            rows = res.fetchall()
        return [self._row_to_record(row) for row in rows]

    def leaf_hashes(self) -> list[str]:
        from .merkle import hash_leaf

        return [hash_leaf(report.encrypted_blob) for report in self.list_reports()]

    def count_reports(self, conn: Any | None = None) -> int:
        if conn is None:
            with self._connect() as own_conn:
                return self.count_reports(own_conn)
        res = conn.execute("SELECT COUNT(*) FROM reports")
        return int(res.fetchone()[0])

    def _connect(self) -> Any:
        if self.url and libsql_client:
            return libsql_client.connect(self.url, auth_token=self.token)

        conn = sqlite3.connect(self.db_path)
        conn.row_factory = sqlite3.Row
        return conn

    @staticmethod
    def _row_to_record(row: Any) -> ReportRecord:
        # libsql uses index-based or key-based access depending on the row object
        # but the client usually provides a row wrapper that handles both.
        return ReportRecord(
            report_id=row[0] if isinstance(row, tuple) else row["report_id"],
            encrypted_blob=bytes(row[1] if isinstance(row, tuple) else row["encrypted_blob"]),
            merkle_index=int(row[2] if isinstance(row, tuple) else row["merkle_index"]),
            submitted_at=int(row[3] if isinstance(row, tuple) else row["submitted_at"]),
            node_id=row[4] if isinstance(row, tuple) else row["node_id"],
            route_path=row[5] if isinstance(row, tuple) else row["route_path"],
        )

