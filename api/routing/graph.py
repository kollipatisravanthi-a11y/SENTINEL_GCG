"""Weighted relay graph used for the college-project routing simulation."""

from __future__ import annotations

from .dijkstra import shortest_path


DEFAULT_RELAY_GRAPH: dict[str, dict[str, int]] = {
    "entry_gateway": {
        "relay_1": 22,
        "relay_2": 14,
        "relay_3": 35,
    },
    "relay_1": {
        "relay_3": 18,
        "relay_4": 40,
    },
    "relay_2": {
        "relay_1": 12,
        "relay_4": 20,
        "relay_5": 28,
    },
    "relay_3": {
        "relay_5": 16,
        "storage_node": 55,
    },
    "relay_4": {
        "storage_node": 17,
    },
    "relay_5": {
        "relay_4": 9,
        "storage_node": 25,
    },
    "storage_node": {},
}


def select_storage_route(
    source: str = "entry_gateway",
    target: str = "storage_node",
    graph: dict[str, dict[str, int]] | None = None,
) -> tuple[int, list[str]]:
    """Select the current lowest-latency simulated relay path."""

    return shortest_path(graph or DEFAULT_RELAY_GRAPH, source, target)

