"""Flask API for SENTINEL."""

from __future__ import annotations

import base64
import hmac
import json
import logging
import os
import re
import sqlite3
import sys
from binascii import Error as Base64Error
from pathlib import Path
from typing import Any

from flask import Flask, jsonify, request, send_from_directory

if __package__ in {None, ""}:
    sys.path.insert(0, str(Path(__file__).resolve().parent.parent))

from server import config
from server.audit.verifier import verify_report
from server.crypto.aes_engine import decrypt_payload
from server.crypto.envelope import assemble_blob, parse_blob
from server.crypto.hmac_engine import compute_hmac
from server.crypto.rsa_engine import ensure_key_pair, load_private_key, unwrap_key
from server.routing.graph import select_storage_route
from server.storage.db import ReportStore
from server.storage.merkle import merkle_root

try:
    from flask_limiter import Limiter
    from flask_limiter.util import get_remote_address
except ImportError:  # pragma: no cover - dependency is optional at import time
    Limiter = None
    get_remote_address = None


REPORT_ID_RE = re.compile(r"^[0-9a-f]{64}$")
WEB_DIR = config.BASE_DIR / "client" / "web"


def create_app(test_config: dict[str, Any] | None = None) -> Flask:
    app = Flask(__name__)
    app.config.update(
        DATABASE_PATH=config.DATABASE_PATH,
        SERVER_PRIVATE_KEY_PATH=config.SERVER_PRIVATE_KEY_PATH,
        SERVER_PUBLIC_KEY_PATH=config.SERVER_PUBLIC_KEY_PATH,
        HMAC_SECRET=config.HMAC_SECRET,
        ADMIN_TOKEN=config.ADMIN_TOKEN,
        NODE_ID=config.NODE_ID,
        ENTRY_NODE=config.ENTRY_NODE,
        STORAGE_NODE=config.STORAGE_NODE,
        MAX_CONTENT_LENGTH=config.MAX_UPLOAD_BYTES * 2,
    )
    if test_config:
        app.config.update(test_config)

    private_key_path = Path(app.config["SERVER_PRIVATE_KEY_PATH"])
    public_key_path = Path(app.config["SERVER_PUBLIC_KEY_PATH"])
    ensure_key_pair(private_key_path, public_key_path)

    store = ReportStore(app.config["DATABASE_PATH"])
    store.initialize()

    limiter = None
    if Limiter and get_remote_address:
        limiter = Limiter(
            key_func=get_remote_address,
            app=app,
            default_limits=[],
            storage_uri="memory://",
        )

    def maybe_limit(fn):
        if limiter is None:
            return fn
        return limiter.limit(config.RATE_LIMIT)(fn)

    @app.get("/")
    def index_page():
        return send_from_directory(WEB_DIR, "index.html")

    @app.get("/verify")
    def verify_page():
        return send_from_directory(WEB_DIR, "verify.html")

    @app.get("/admin")
    def admin_page():
        return send_from_directory(WEB_DIR, "admin.html")

    @app.get("/crypto.js")
    def crypto_js():
        return send_from_directory(WEB_DIR, "crypto.js")

    @app.get("/api/v1/public-key")
    def public_key():
        return jsonify({"public_key_pem": public_key_path.read_text(encoding="utf-8")})

    @app.post("/api/v1/submit")
    @maybe_limit
    def submit_report():
        payload = request.get_json(silent=True) or {}
        try:
            ciphertext = _decode_b64_field(payload, "ciphertext")
            auth_tag = _decode_b64_field(payload, "auth_tag")
            iv = _decode_b64_field(payload, "iv")
            encrypted_key = _decode_b64_field(payload, "encrypted_key")
            _validate_encrypted_parts(ciphertext, auth_tag, iv, encrypted_key)
        except ValueError as exc:
            return jsonify({"error": str(exc)}), 400

        encrypted_blob = assemble_blob(
            ciphertext=ciphertext,
            auth_tag=auth_tag,
            iv=iv,
            encrypted_key=encrypted_key,
        )
        report_id = compute_hmac(encrypted_blob, app.config["HMAC_SECRET"])
        route_cost, route_path = select_storage_route(
            app.config["ENTRY_NODE"],
            app.config["STORAGE_NODE"],
        )
        app.logger.info("Optimal relay path: %s", " -> ".join(route_path))

        duplicate = False
        try:
            record = store.add_report(
                report_id=report_id,
                encrypted_blob=encrypted_blob,
                node_id=app.config["NODE_ID"],
                route_path=route_path,
            )
        except sqlite3.IntegrityError:
            duplicate = True
            record = store.get_report(report_id)
            if record is None:
                raise

        current_root = merkle_root(store.leaf_hashes())
        return jsonify(
            {
                "report_id": report_id,
                "status": "STORED",
                "duplicate": duplicate,
                "merkle_index": record.merkle_index,
                "merkle_root": current_root,
                "node_id": record.node_id,
                "route": {
                    "cost_ms": route_cost,
                    "path": route_path,
                },
            }
        )

    @app.get("/api/v1/verify/<report_id>")
    def verify(report_id: str):
        if not REPORT_ID_RE.fullmatch(report_id):
            return jsonify({"status": "INVALID_RECEIPT"}), 400

        report = store.get_report(report_id)
        if report is None:
            return jsonify(
                {
                    "status": "NOT_FOUND",
                    "report_id": report_id,
                    "merkle_root": merkle_root(store.leaf_hashes()),
                }
            ), 404

        result = verify_report(report, store.list_reports(), app.config["HMAC_SECRET"])
        return jsonify(
            {
                "status": result.status,
                "report_id": result.report_id,
                "leaf_hash": result.leaf_hash,
                "merkle_root": result.merkle_root,
                "merkle_proof": result.merkle_proof,
                "proof_valid": result.proof_valid,
                "merkle_index": report.merkle_index,
                "node_id": report.node_id,
                "route_path": report.route_path,
            }
        )

    @app.get("/api/v1/audit/merkle-root")
    def audit_merkle_root():
        leaf_hashes = store.leaf_hashes()
        return jsonify(
            {
                "merkle_root": merkle_root(leaf_hashes),
                "report_count": len(leaf_hashes),
            }
        )

    @app.get("/api/v1/admin/reports")
    def admin_reports():
        token = request.headers.get("X-Admin-Token", "")
        if not _admin_token_is_valid(token, app.config["ADMIN_TOKEN"]):
            return jsonify({"error": "admin token required"}), 403

        reports = store.list_reports()
        summaries = []
        for report in reports:
            result = verify_report(report, reports, app.config["HMAC_SECRET"])
            summaries.append(
                {
                    "report_id": report.report_id,
                    "status": result.status,
                    "merkle_index": report.merkle_index,
                    "submitted_at": report.submitted_at,
                    "node_id": report.node_id,
                    "route_path": report.route_path,
                    "leaf_hash": result.leaf_hash,
                }
            )

        return jsonify(
            {
                "reports": summaries,
                "report_count": len(summaries),
                "merkle_root": merkle_root(store.leaf_hashes()),
            }
        )

    @app.post("/api/v1/admin/decrypt")
    def admin_decrypt():
        payload = request.get_json(silent=True) or {}
        token = request.headers.get("X-Admin-Token") or payload.get("admin_token", "")
        if not _admin_token_is_valid(token, app.config["ADMIN_TOKEN"]):
            return jsonify({"error": "admin token required"}), 403

        report_id = str(payload.get("report_id", ""))
        if not REPORT_ID_RE.fullmatch(report_id):
            return jsonify({"error": "valid report_id required"}), 400

        report = store.get_report(report_id)
        if report is None:
            return jsonify({"error": "report not found"}), 404

        try:
            envelope = parse_blob(report.encrypted_blob)
            private_key = load_private_key(private_key_path)
            aes_key = unwrap_key(private_key, envelope.encrypted_key)
            plaintext = decrypt_payload(
                envelope.ciphertext,
                aes_key,
                envelope.iv,
                envelope.auth_tag,
            )
            decoded = json.loads(plaintext.decode("utf-8"))
        except Exception as exc:  # pragma: no cover - defensive API boundary
            return jsonify({"error": f"decrypt failed: {exc}"}), 422

        if not payload.get("include_attachment_data", False):
            attachment = decoded.get("attachment")
            if isinstance(attachment, dict):
                attachment.pop("data_base64", None)

        result = verify_report(report, store.list_reports(), app.config["HMAC_SECRET"])
        return jsonify(
            {
                "report_id": report_id,
                "integrity": {
                    "status": result.status,
                    "leaf_hash": result.leaf_hash,
                    "merkle_root": result.merkle_root,
                    "proof_valid": result.proof_valid,
                    "merkle_index": report.merkle_index,
                },
                "payload": decoded,
            }
        )

    return app


def _decode_b64_field(payload: dict[str, Any], field: str) -> bytes:
    value = payload.get(field)
    if not isinstance(value, str) or not value:
        raise ValueError(f"{field} is required")
    try:
        return base64.b64decode(value, validate=True)
    except (Base64Error, ValueError) as exc:
        raise ValueError(f"{field} must be valid base64") from exc


def _validate_encrypted_parts(
    ciphertext: bytes,
    auth_tag: bytes,
    iv: bytes,
    encrypted_key: bytes,
) -> None:
    if not ciphertext:
        raise ValueError("ciphertext cannot be empty")
    if len(auth_tag) != 16:
        raise ValueError("auth_tag must be 16 bytes")
    if len(iv) != 12:
        raise ValueError("iv must be 12 bytes")
    if len(encrypted_key) < 128:
        raise ValueError("encrypted_key is too short")


def _admin_token_is_valid(token: Any, expected: Any) -> bool:
    return hmac.compare_digest(str(token), str(expected))


if __name__ == "__main__":
    logging.getLogger("werkzeug").setLevel(logging.WARNING)
    host = os.getenv("SENTINEL_HOST", "127.0.0.1")
    port = int(os.getenv("PORT", os.getenv("SENTINEL_PORT", "5000")))
    create_app().run(host=host, port=port, debug=False)
