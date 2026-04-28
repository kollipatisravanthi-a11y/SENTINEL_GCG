"""RSA-2048 OAEP key wrapping helpers."""

from __future__ import annotations

from pathlib import Path

from cryptography.hazmat.primitives import hashes, serialization
from cryptography.hazmat.primitives.asymmetric import padding, rsa
from cryptography.hazmat.primitives.asymmetric.rsa import RSAPrivateKey, RSAPublicKey


def generate_private_key() -> RSAPrivateKey:
    """Generate an RSA-2048 private key for the demo server."""

    return rsa.generate_private_key(public_exponent=65537, key_size=2048)


def serialize_private_key(private_key: RSAPrivateKey) -> bytes:
    return private_key.private_bytes(
        encoding=serialization.Encoding.PEM,
        format=serialization.PrivateFormat.PKCS8,
        encryption_algorithm=serialization.NoEncryption(),
    )


def serialize_public_key(public_key: RSAPublicKey) -> bytes:
    return public_key.public_bytes(
        encoding=serialization.Encoding.PEM,
        format=serialization.PublicFormat.SubjectPublicKeyInfo,
    )


def ensure_key_pair(private_path: Path, public_path: Path) -> None:
    """Create the server RSA keypair if it does not already exist."""

    private_path.parent.mkdir(parents=True, exist_ok=True)
    if private_path.exists() and public_path.exists():
        return

    private_key = generate_private_key()
    private_path.write_bytes(serialize_private_key(private_key))
    public_path.write_bytes(serialize_public_key(private_key.public_key()))


def load_private_key(pem_string: str) -> RSAPrivateKey:
    key = serialization.load_pem_private_key(pem_string.encode(), password=None)
    if not isinstance(key, RSAPrivateKey):
        raise TypeError("Expected an RSA private key")
    return key


def load_public_key(pem_string: str) -> RSAPublicKey:
    key = serialization.load_pem_public_key(pem_string.encode())
    if not isinstance(key, RSAPublicKey):
        raise TypeError("Expected an RSA public key")
    return key


def wrap_key(public_key: RSAPublicKey, aes_key: bytes) -> bytes:
    """Encrypt an AES key with the server public key."""

    return public_key.encrypt(
        aes_key,
        padding.OAEP(
            mgf=padding.MGF1(algorithm=hashes.SHA256()),
            algorithm=hashes.SHA256(),
            label=None,
        ),
    )


def unwrap_key(private_key: RSAPrivateKey, encrypted_key: bytes) -> bytes:
    """Decrypt an AES key with the server private key."""

    return private_key.decrypt(
        encrypted_key,
        padding.OAEP(
            mgf=padding.MGF1(algorithm=hashes.SHA256()),
            algorithm=hashes.SHA256(),
            label=None,
        ),
    )

