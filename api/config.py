"""Configuration defaults for the SENTINEL demo server."""

from __future__ import annotations

import base64
import os
import tempfile
from pathlib import Path


BASE_DIR = Path(__file__).resolve().parent.parent
# For Vercel serverless, use /tmp for temporary file storage
DATA_DIR = Path(tempfile.gettempdir()) / "sentinel_data"
DATA_DIR.mkdir(exist_ok=True)

DATABASE_PATH = Path(os.getenv("SENTINEL_DB", DATA_DIR / "sentinel.db"))

# Support both file paths and environment variables for keys
SERVER_PRIVATE_KEY_PATH = Path(
    os.getenv("SENTINEL_PRIVATE_KEY", DATA_DIR / "server_private_key.pem")
)
SERVER_PUBLIC_KEY_PATH = Path(
    os.getenv("SENTINEL_PUBLIC_KEY", DATA_DIR / "server_public_key.pem")
)

# Environment variables for key content (base64 encoded)
_private_key_b64 = os.getenv("SENTINEL_PRIVATE_KEY_CONTENT", "")
_public_key_b64 = os.getenv("SENTINEL_PUBLIC_KEY_CONTENT", "")

SERVER_PRIVATE_KEY_CONTENT = (
    base64.b64decode(_private_key_b64) if _private_key_b64 else None
)
SERVER_PUBLIC_KEY_CONTENT = (
    base64.b64decode(_public_key_b64) if _public_key_b64 else None
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

