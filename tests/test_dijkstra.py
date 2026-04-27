import pytest

from server.routing.dijkstra import shortest_path
from server.routing.graph import DEFAULT_RELAY_GRAPH, select_storage_route


def test_default_route_prefers_lowest_latency_path():
    cost, path = select_storage_route()

    assert cost == 51
    assert path == ["entry_gateway", "relay_2", "relay_4", "storage_node"]


def test_shortest_path_rejects_unreachable_target():
    with pytest.raises(ValueError):
        shortest_path({"a": {"b": 1}, "b": {}}, "a", "c")

