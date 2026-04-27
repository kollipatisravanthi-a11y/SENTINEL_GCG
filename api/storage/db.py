"""SQLite storage layer for encrypted reports."""

from __future__ import annotations

import sqlite3
import time
from dataclasses import dataclass
from pathlib import Path
from typing import Iterable


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
                    sqlite3.Binary(encrypted_blob),
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
            row = conn.execute(
                """
                SELECT report_id, encrypted_blob, merkle_index, submitted_at, node_id, route_path
                FROM reports
                WHERE report_id = ?
                """,
                (report_id,),
            ).fetchone()
        return self._row_to_record(row) if row else None

    def list_reports(self) -> list[ReportRecord]:
        with self._connect() as conn:
            rows = conn.execute(
                """
                SELECT report_id, encrypted_blob, merkle_index, submitted_at, node_id, route_path
                FROM reports
                ORDER BY merkle_index ASC
                """
            ).fetchall()
        return [self._row_to_record(row) for row in rows]

    def leaf_hashes(self) -> list[str]:
        from .merkle import hash_leaf

        return [hash_leaf(report.encrypted_blob) for report in self.list_reports()]

    def count_reports(self, conn: sqlite3.Connection | None = None) -> int:
        if conn is None:
            with self._connect() as own_conn:
                return self.count_reports(own_conn)
        return int(conn.execute("SELECT COUNT(*) FROM reports").fetchone()[0])

    def _connect(self) -> sqlite3.Connection:
        conn = sqlite3.connect(self.db_path)
        conn.row_factory = sqlite3.Row
        return conn

    @staticmethod
    def _row_to_record(row: sqlite3.Row) -> ReportRecord:
        return ReportRecord(
            report_id=row["report_id"],
            encrypted_blob=bytes(row["encrypted_blob"]),
            merkle_index=int(row["merkle_index"]),
            submitted_at=int(row["submitted_at"]),
            node_id=row["node_id"],
            route_path=row["route_path"],
        )

