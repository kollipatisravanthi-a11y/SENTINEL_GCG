"""AES-256-GCM helpers."""

from __future__ import annotations

import os
from typing import TypedDict

from cryptography.hazmat.primitives.ciphers.aead import AESGCM


AUTH_TAG_BYTES = 16
KEY_BYTES = 32
IV_BYTES = 12


class AesEncryptedPayload(TypedDict):
    ciphertext: bytes
    auth_tag: bytes
    iv: bytes
    key: bytes


def generate_key() -> bytes:
    """Return a fresh 256-bit AES key."""

    return AESGCM.generate_key(bit_length=256)


def generate_iv() -> bytes:
    """Return a fresh 96-bit GCM IV."""

    return os.urandom(IV_BYTES)


def encrypt_payload(
    plaintext: bytes,
    key: bytes | None = None,
    iv: bytes | None = None,
    aad: bytes | None = None,
) -> AesEncryptedPayload:
    """Encrypt bytes with AES-256-GCM and split the GCM tag."""

    if key is None:
        key = generate_key()
    if iv is None:
        iv = generate_iv()
    if len(key) != KEY_BYTES:
        raise ValueError("AES-256-GCM requires a 32-byte key")
    if len(iv) != IV_BYTES:
        raise ValueError("AES-GCM requires a 12-byte IV in SENTINEL")

    encrypted = AESGCM(key).encrypt(iv, plaintext, aad)
    return {
        "ciphertext": encrypted[:-AUTH_TAG_BYTES],
        "auth_tag": encrypted[-AUTH_TAG_BYTES:],
        "iv": iv,
        "key": key,
    }


def decrypt_payload(
    ciphertext: bytes,
    key: bytes,
    iv: bytes,
    auth_tag: bytes,
    aad: bytes | None = None,
) -> bytes:
    """Decrypt AES-256-GCM ciphertext and verify its authentication tag."""

    if len(key) != KEY_BYTES:
        raise ValueError("AES-256-GCM requires a 32-byte key")
    if len(iv) != IV_BYTES:
        raise ValueError("AES-GCM requires a 12-byte IV in SENTINEL")
    if len(auth_tag) != AUTH_TAG_BYTES:
        raise ValueError("AES-GCM authentication tag must be 16 bytes")

    return AESGCM(key).decrypt(iv, ciphertext + auth_tag, aad)

