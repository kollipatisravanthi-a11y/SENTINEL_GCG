"""SQLite (local) or LibSQL (Turso) storage layer."""

from __future__ import annotations

import os
import sqlite3
import time
from dataclasses import dataclass
from pathlib import Path
from typing import Any, Iterable

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

        self._turso_client = None
        if self.url and libsql_client:
            clean_url = self.url
            if clean_url.startswith("libsql://"):
                clean_url = clean_url.replace("libsql://", "https://")
            # ClientSync is a sync wrapper around an async client.
            # Reuse it across calls to avoid spinning up a new thread/loop per query.
            self._turso_client = libsql_client.create_client_sync(url=clean_url, auth_token=self.token)
        else:
            self.db_path.parent.mkdir(parents=True, exist_ok=True)

    def _is_turso(self) -> bool:
        return self._turso_client is not None

    def initialize(self) -> None:
        if self._is_turso():
            client = self._turso_client
            assert client is not None
            client.execute(
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
            client.execute(
                "CREATE INDEX IF NOT EXISTS idx_reports_merkle_index "
                "ON reports(merkle_index)"
            )
            return

        with self._connect_sqlite() as conn:
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
        merkle_index = self.count_reports()
        submitted_at = int(time.time())
        route_text = " -> ".join(route_path)

        if self._is_turso():
            client = self._turso_client
            assert client is not None
            client.execute(
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
                    encrypted_blob,
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

        with self._connect_sqlite() as conn:
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
        if self._is_turso():
            client = self._turso_client
            assert client is not None
            res = client.execute(
                """
                SELECT report_id, encrypted_blob, merkle_index, submitted_at, node_id, route_path
                FROM reports
                WHERE report_id = ?
                """,
                (report_id,),
            )
            row = res.rows[0] if res.rows else None
            return self._row_to_record(row) if row else None

        with self._connect_sqlite() as conn:
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
        if self._is_turso():
            client = self._turso_client
            assert client is not None
            res = client.execute(
                """
                SELECT report_id, encrypted_blob, merkle_index, submitted_at, node_id, route_path
                FROM reports
                ORDER BY merkle_index ASC
                """
            )
            return [self._row_to_record(row) for row in res.rows]

        with self._connect_sqlite() as conn:
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

    def count_reports(self) -> int:
        if self._is_turso():
            client = self._turso_client
            assert client is not None
            res = client.execute("SELECT COUNT(*) FROM reports")
            if not res.rows:
                return 0
            return int(res.rows[0][0])

        with self._connect_sqlite() as conn:
            return int(conn.execute("SELECT COUNT(*) FROM reports").fetchone()[0])

    def _connect_sqlite(self) -> sqlite3.Connection:
        conn = sqlite3.connect(self.db_path)
        conn.row_factory = sqlite3.Row
        return conn

    @staticmethod
    def _row_to_record(row: Any) -> ReportRecord:
        # sqlite3.Row and libsql_client.Row both support name-based indexing.
        # sqlite3.Row also supports numeric indexing.
        try:
            report_id = row["report_id"]
            encrypted_blob = row["encrypted_blob"]
            merkle_index = row["merkle_index"]
            submitted_at = row["submitted_at"]
            node_id = row["node_id"]
            route_path = row["route_path"]
        except Exception:
            report_id = row[0]
            encrypted_blob = row[1]
            merkle_index = row[2]
            submitted_at = row[3]
            node_id = row[4]
            route_path = row[5]

        return ReportRecord(
            report_id=str(report_id),
            encrypted_blob=bytes(encrypted_blob),
            merkle_index=int(merkle_index),
            submitted_at=int(submitted_at),
            node_id=str(node_id),
            route_path=str(route_path),
        )

