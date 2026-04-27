"""Report verification using HMAC and Merkle proofs."""

from __future__ import annotations

from dataclasses import dataclass

from ..crypto.hmac_engine import compute_hmac, verify_hmac
from ..storage.db import ReportRecord
from ..storage.merkle import generate_proof, hash_leaf, merkle_root, verify_proof


@dataclass(frozen=True)
class VerificationResult:
    status: str
    report_id: str
    leaf_hash: str | None
    merkle_root: str
    merkle_proof: list[dict[str, str]]
    proof_valid: bool


def verify_report(
    report: ReportRecord,
    all_reports: list[ReportRecord],
    secret: bytes,
) -> VerificationResult:
    """Verify a stored report against its receipt and current Merkle tree."""

    leaf_hashes = [hash_leaf(item.encrypted_blob) for item in all_reports]
    root = merkle_root(leaf_hashes)
    leaf = hash_leaf(report.encrypted_blob)

    try:
        proof = generate_proof(report.merkle_index, leaf_hashes)
        proof_valid = verify_proof(leaf, proof, root)
    except IndexError:
        proof = []
        proof_valid = False

    hmac_valid = verify_hmac(report.encrypted_blob, report.report_id, secret)
    status = "VALID" if hmac_valid and proof_valid else "TAMPERED"

    return VerificationResult(
        status=status,
        report_id=report.report_id,
        leaf_hash=leaf,
        merkle_root=root,
        merkle_proof=proof,
        proof_valid=proof_valid,
    )


def expected_receipt(blob: bytes, secret: bytes) -> str:
    return compute_hmac(blob, secret)

