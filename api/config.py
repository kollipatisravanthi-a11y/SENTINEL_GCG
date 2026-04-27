"""Configuration defaults for the SENTINEL demo server."""

from __future__ import annotations

import os
from pathlib import Path


BASE_DIR = Path(__file__).resolve().parent.parent
DATA_DIR = BASE_DIR / "data"
DATABASE_PATH = Path(os.getenv("SENTINEL_DB", DATA_DIR / "sentinel.db"))

SERVER_PRIVATE_KEY_PATH = Path(
    os.getenv("SENTINEL_PRIVATE_KEY", DATA_DIR / "server_private_key.pem")
)
SERVER_PUBLIC_KEY_PATH = Path(
    os.getenv("SENTINEL_PUBLIC_KEY", DATA_DIR / "server_public_key.pem")
)

NODE_ID = os.getenv("SENTINEL_NODE_ID", "storage_primary")
ENTRY_NODE = os.getenv("SENTINEL_ENTRY_NODE", "entry_gateway")
STORAGE_NODE = os.getenv("SENTINEL_STORAGE_NODE", "storage_node")

HMAC_SECRET = os.getenv(
    "SENTINEL_HMAC_SECRET",
    "dev-only-change-this-hmac-secret-before-real-use",
).encode("utf-8")

ADMIN_TOKEN = os.getenv("SENTINEL_ADMIN_TOKEN", "sentinel-admin-dev-token")

MAX_UPLOAD_BYTES = int(os.getenv("SENTINEL_MAX_UPLOAD_BYTES", str(10 * 1024 * 1024)))
RATE_LIMIT = os.getenv("SENTINEL_RATE_LIMIT", "10 per hour")

