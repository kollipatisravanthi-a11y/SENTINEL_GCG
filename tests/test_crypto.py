from server.crypto.aes_engine import decrypt_payload, encrypt_payload
from server.crypto.hmac_engine import compute_hmac, verify_hmac
from server.crypto.rsa_engine import (
    ensure_key_pair,
    load_private_key,
    load_public_key,
    unwrap_key,
    wrap_key,
)


def test_aes_gcm_round_trip():
    plaintext = b"anonymous report body"
    encrypted = encrypt_payload(plaintext)

    recovered = decrypt_payload(
        encrypted["ciphertext"],
        encrypted["key"],
        encrypted["iv"],
        encrypted["auth_tag"],
    )

    assert recovered == plaintext


def test_rsa_key_wrap_round_trip(tmp_path):
    private_path = tmp_path / "private.pem"
    public_path = tmp_path / "public.pem"
    ensure_key_pair(private_path, public_path)

    aes_key = b"a" * 32
    encrypted_key = wrap_key(load_public_key(public_path), aes_key)
    recovered = unwrap_key(load_private_key(private_path), encrypted_key)

    assert recovered == aes_key


def test_hmac_detects_tampering():
    secret = b"test-secret"
    blob = b"encrypted blob"
    receipt = compute_hmac(blob, secret)

    assert verify_hmac(blob, receipt, secret)
    assert not verify_hmac(blob + b"!", receipt, secret)

