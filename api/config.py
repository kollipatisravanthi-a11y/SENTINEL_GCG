"""Configuration defaults for the SENTINEL demo server."""

from __future__ import annotations

import os
import tempfile
from pathlib import Path


BASE_DIR = Path(__file__).resolve().parent.parent

# For Vercel, store keys in /tmp during runtime
# For local development, store in project data/ directory
if os.getenv("VERCEL"):
    # Vercel environment - use tmp directory
    DATA_DIR = Path(tempfile.gettempdir()) / "sentinel_data"
else:
    # Local development - use project directory
    DATA_DIR = BASE_DIR / "data"

DATA_DIR.mkdir(parents=True, exist_ok=True)

DATABASE_PATH = Path(os.getenv("SENTINEL_DB", DATA_DIR / "sentinel.db"))

# RSA key paths - keys will be auto-generated if they don't exist
SERVER_PRIVATE_KEY_PATH = Path(
    os.getenv("SENTINEL_PRIVATE_KEY", DATA_DIR / "server_private_key.pem")
)
SERVER_PUBLIC_KEY_PATH = Path(
    os.getenv("SENTINEL_PUBLIC_KEY", DATA_DIR / "server_public_key.pem")
)

NODE_ID = os.getenv("SENTINEL_NODE_ID", "storage_primary")
ENTRY_NODE = os.getenv("SENTINEL_ENTRY_NODE", "entry_gateway")
STORAGE_NODE = os.getenv("SENTINEL_STORAGE_NODE", "storage_node")

# Only these two secrets are required in environment variables
HMAC_SECRET = os.getenv(
    "SENTINEL_HMAC_SECRET",
    "dev-only-change-this-hmac-secret-before-real-use",
).encode("utf-8")

ADMIN_TOKEN = os.getenv("SENTINEL_ADMIN_TOKEN", "sentinel-admin-dev-token")

MAX_UPLOAD_BYTES = int(os.getenv("SENTINEL_MAX_UPLOAD_BYTES", str(10 * 1024 * 1024)))
RATE_LIMIT = os.getenv("SENTINEL_RATE_LIMIT", "10 per hour")

