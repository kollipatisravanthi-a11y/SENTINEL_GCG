"""HMAC-SHA256 receipt generation."""

from __future__ import annotations

import hmac
from hashlib import sha256


def compute_hmac(blob: bytes, secret: bytes) -> str:
    """Return a 64-character HMAC-SHA256 receipt for an encrypted blob."""

    return hmac.new(secret, blob, sha256).hexdigest()


def verify_hmac(blob: bytes, expected_hex: str, secret: bytes) -> bool:
    """Constant-time HMAC verification."""

    actual = compute_hmac(blob, secret)
    return hmac.compare_digest(actual, expected_hex)

