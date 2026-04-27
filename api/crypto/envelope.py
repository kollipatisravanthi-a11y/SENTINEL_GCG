"""Canonical binary envelope for encrypted report blobs."""

from __future__ import annotations

import struct
from dataclasses import dataclass


MAGIC = b"SENTINEL1"
PART_COUNT = 4


@dataclass(frozen=True)
class EncryptedEnvelope:
    iv: bytes
    auth_tag: bytes
    encrypted_key: bytes
    ciphertext: bytes


def assemble_blob(
    *,
    ciphertext: bytes,
    auth_tag: bytes,
    iv: bytes,
    encrypted_key: bytes,
) -> bytes:
    """Create the exact byte sequence that is sealed and stored."""

    parts = (iv, auth_tag, encrypted_key, ciphertext)
    return MAGIC + b"".join(struct.pack(">I", len(part)) + part for part in parts)


def parse_blob(blob: bytes) -> EncryptedEnvelope:
    """Parse a SENTINEL encrypted blob."""

    if not blob.startswith(MAGIC):
        raise ValueError("Invalid SENTINEL encrypted blob header")

    offset = len(MAGIC)
    parts: list[bytes] = []
    for _ in range(PART_COUNT):
        if offset + 4 > len(blob):
            raise ValueError("Truncated SENTINEL encrypted blob")
        length = struct.unpack(">I", blob[offset : offset + 4])[0]
        offset += 4
        part = blob[offset : offset + length]
        if len(part) != length:
            raise ValueError("Truncated SENTINEL encrypted blob part")
        parts.append(part)
        offset += length

    if offset != len(blob):
        raise ValueError("Unexpected trailing bytes in SENTINEL encrypted blob")

    iv, auth_tag, encrypted_key, ciphertext = parts
    return EncryptedEnvelope(
        iv=iv,
        auth_tag=auth_tag,
        encrypted_key=encrypted_key,
        ciphertext=ciphertext,
    )

