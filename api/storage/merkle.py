"""Merkle tree construction and proof verification."""

from __future__ import annotations

from hashlib import sha256
from typing import TypedDict


EMPTY_ROOT = "0" * 64


class ProofStep(TypedDict):
    position: str
    hash: str


def hash_leaf(data: bytes) -> str:
    return sha256(data).hexdigest()


def combine_hashes(left_hex: str, right_hex: str) -> str:
    return sha256(bytes.fromhex(left_hex) + bytes.fromhex(right_hex)).hexdigest()


def build_merkle_levels(leaf_hashes: list[str]) -> list[list[str]]:
    """Return all Merkle levels from leaves to root."""

    if not leaf_hashes:
        return [[EMPTY_ROOT]]

    levels = [list(leaf_hashes)]
    current = list(leaf_hashes)
    while len(current) > 1:
        if len(current) % 2 == 1:
            current = current + [current[-1]]
        parent = [
            combine_hashes(current[i], current[i + 1])
            for i in range(0, len(current), 2)
        ]
        levels.append(parent)
        current = parent
    return levels


def merkle_root(leaf_hashes: list[str]) -> str:
    return build_merkle_levels(leaf_hashes)[-1][0]


def generate_proof(index: int, leaf_hashes: list[str]) -> list[ProofStep]:
    if index < 0 or index >= len(leaf_hashes):
        raise IndexError("Merkle proof index out of range")

    proof: list[ProofStep] = []
    current_index = index
    current_level = list(leaf_hashes)

    while len(current_level) > 1:
        if len(current_level) % 2 == 1:
            current_level = current_level + [current_level[-1]]

        if current_index % 2 == 0:
            sibling_index = current_index + 1
            position = "right"
        else:
            sibling_index = current_index - 1
            position = "left"

        proof.append({"position": position, "hash": current_level[sibling_index]})

        current_index //= 2
        current_level = [
            combine_hashes(current_level[i], current_level[i + 1])
            for i in range(0, len(current_level), 2)
        ]

    return proof


def verify_proof(leaf_hash: str, proof: list[ProofStep], expected_root: str) -> bool:
    current = leaf_hash
    for step in proof:
        if step["position"] == "left":
            current = combine_hashes(step["hash"], current)
        elif step["position"] == "right":
            current = combine_hashes(current, step["hash"])
        else:
            return False
    return current == expected_root

