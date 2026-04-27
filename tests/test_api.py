import base64
import json
import sqlite3

from server.app import create_app
from server.crypto.aes_engine import encrypt_payload
from server.crypto.rsa_engine import load_public_key, wrap_key


def _b64(data: bytes) -> str:
    return base64.b64encode(data).decode("ascii")


def _encrypted_submission(public_key_path, payload: dict):
    encrypted = encrypt_payload(json.dumps(payload).encode("utf-8"))
    encrypted_key = wrap_key(load_public_key(public_key_path), encrypted["key"])
    return {
        "ciphertext": _b64(encrypted["ciphertext"]),
        "auth_tag": _b64(encrypted["auth_tag"]),
        "iv": _b64(encrypted["iv"]),
        "encrypted_key": _b64(encrypted_key),
    }


def test_submit_verify_and_admin_decrypt(tmp_path):
    db_path = tmp_path / "sentinel.db"
    private_path = tmp_path / "private.pem"
    public_path = tmp_path / "public.pem"
    app = create_app(
        {
            "TESTING": True,
            "DATABASE_PATH": db_path,
            "SERVER_PRIVATE_KEY_PATH": private_path,
            "SERVER_PUBLIC_KEY_PATH": public_path,
            "HMAC_SECRET": b"test-secret",
            "ADMIN_TOKEN": "test-token",
        }
    )
    client = app.test_client()

    submission = _encrypted_submission(
        public_path,
        {"title": "case", "body": "evidence", "attachment": None},
    )
    submit_response = client.post("/api/v1/submit", json=submission)
    assert submit_response.status_code == 200
    report_id = submit_response.get_json()["report_id"]

    verify_response = client.get(f"/api/v1/verify/{report_id}")
    assert verify_response.status_code == 200
    assert verify_response.get_json()["status"] == "VALID"

    decrypt_response = client.post(
        "/api/v1/admin/decrypt",
        json={"report_id": report_id},
        headers={"X-Admin-Token": "test-token"},
    )
    assert decrypt_response.status_code == 200
    assert decrypt_response.get_json()["integrity"]["status"] == "VALID"
    assert decrypt_response.get_json()["payload"]["body"] == "evidence"

    list_response = client.get(
        "/api/v1/admin/reports",
        headers={"X-Admin-Token": "test-token"},
    )
    assert list_response.status_code == 200
    assert list_response.get_json()["report_count"] == 1
    assert list_response.get_json()["reports"][0]["report_id"] == report_id


def test_admin_pages_and_api_require_token(tmp_path):
    db_path = tmp_path / "sentinel.db"
    private_path = tmp_path / "private.pem"
    public_path = tmp_path / "public.pem"
    app = create_app(
        {
            "TESTING": True,
            "DATABASE_PATH": db_path,
            "SERVER_PRIVATE_KEY_PATH": private_path,
            "SERVER_PUBLIC_KEY_PATH": public_path,
            "HMAC_SECRET": b"test-secret",
            "ADMIN_TOKEN": "test-token",
        }
    )
    client = app.test_client()

    assert client.get("/admin").status_code == 200
    assert client.get("/api/v1/admin/reports").status_code == 403


def test_verify_marks_modified_blob_as_tampered(tmp_path):
    db_path = tmp_path / "sentinel.db"
    private_path = tmp_path / "private.pem"
    public_path = tmp_path / "public.pem"
    app = create_app(
        {
            "TESTING": True,
            "DATABASE_PATH": db_path,
            "SERVER_PRIVATE_KEY_PATH": private_path,
            "SERVER_PUBLIC_KEY_PATH": public_path,
            "HMAC_SECRET": b"test-secret",
            "ADMIN_TOKEN": "test-token",
        }
    )
    client = app.test_client()

    submission = _encrypted_submission(public_path, {"body": "original"})
    report_id = client.post("/api/v1/submit", json=submission).get_json()["report_id"]

    with sqlite3.connect(db_path) as conn:
        blob = conn.execute(
            "SELECT encrypted_blob FROM reports WHERE report_id = ?",
            (report_id,),
        ).fetchone()[0]
        tampered = bytes(blob[:-1]) + bytes([blob[-1] ^ 1])
        conn.execute(
            "UPDATE reports SET encrypted_blob = ? WHERE report_id = ?",
            (sqlite3.Binary(tampered), report_id),
        )

    verify_response = client.get(f"/api/v1/verify/{report_id}")
    assert verify_response.status_code == 200
    assert verify_response.get_json()["status"] == "TAMPERED"
