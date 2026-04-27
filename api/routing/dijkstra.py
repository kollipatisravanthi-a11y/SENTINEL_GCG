"""Dijkstra shortest-path implementation for relay selection."""

from __future__ import annotations

import heapq
from collections.abc import Mapping


Graph = Mapping[str, Mapping[str, int]]


def shortest_path(graph: Graph, source: str, target: str) -> tuple[int, list[str]]:
    """Return the minimum-cost path from source to target."""

    if source not in graph:
        raise KeyError(f"Unknown source node: {source}")

    distances: dict[str, int] = {source: 0}
    previous: dict[str, str] = {}
    queue: list[tuple[int, str]] = [(0, source)]
    visited: set[str] = set()

    while queue:
        cost, node = heapq.heappop(queue)
        if node in visited:
            continue
        visited.add(node)

        if node == target:
            return cost, _reconstruct_path(previous, source, target)

        for neighbor, weight in graph.get(node, {}).items():
            if weight < 0:
                raise ValueError("Dijkstra cannot process negative edge weights")
            new_cost = cost + weight
            if new_cost < distances.get(neighbor, float("inf")):
                distances[neighbor] = new_cost
                previous[neighbor] = node
                heapq.heappush(queue, (new_cost, neighbor))

    raise ValueError(f"No route from {source} to {target}")


def _reconstruct_path(previous: dict[str, str], source: str, target: str) -> list[str]:
    path = [target]
    while path[-1] != source:
        path.append(previous[path[-1]])
    path.reverse()
    return path

