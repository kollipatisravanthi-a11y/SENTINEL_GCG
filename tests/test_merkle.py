from server.storage.merkle import (
    generate_proof,
    hash_leaf,
    merkle_root,
    verify_proof,
)


def test_merkle_proof_validates_original_leaf():
    leaves = [hash_leaf(f"report-{index}".encode()) for index in range(5)]
    root = merkle_root(leaves)
    proof = generate_proof(3, leaves)

    assert verify_proof(leaves[3], proof, root)


def test_merkle_proof_rejects_tampered_leaf():
    leaves = [hash_leaf(f"report-{index}".encode()) for index in range(4)]
    root = merkle_root(leaves)
    proof = generate_proof(2, leaves)
    tampered_leaf = hash_leaf(b"changed")

    assert not verify_proof(tampered_leaf, proof, root)

