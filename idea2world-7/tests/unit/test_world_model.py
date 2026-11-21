"""Determinism and structure: the heightfield and the route graph are the two things every later
stage trusts, so they are tested without building a world."""
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[2]
sys.path.insert(0, str(ROOT))

from world.heightfield import Heightfield, fbm  # noqa: E402
from world.layout_graph import LayoutGraph, distance_to_paths, polyline_length  # noqa: E402
from world.world_spec import WorldSpec  # noqa: E402


def _graph(points, edges, kinds=None):
    graph = LayoutGraph()
    for name, (x, z) in points.items():
        graph.add_node(name, (x, z), kind=(kinds or {}).get(name, "region"))
    for a, b in edges:
        graph.add_edge(a, b)
    return graph


def test_terrain_is_deterministic():
    a = Heightfield.generate(1200, 48, 7, 1.0)
    b = Heightfield.generate(1200, 48, 7, 1.0)
    samples = [(x, z) for x in range(-500, 501, 125) for z in range(-500, 501, 125)]
    assert all(abs(a.at(x, z) - b.at(x, z)) < 1e-9 for x, z in samples)


def test_seed_changes_terrain():
    a = Heightfield.generate(1200, 48, 7, 1.0)
    b = Heightfield.generate(1200, 48, 8, 1.0)
    assert any(abs(a.at(x, z) - b.at(x, z)) > 0.5 for x in (0, 200, -300) for z in (0, 200, -300))


def test_height_is_bounded_and_interpolated():
    field = Heightfield.generate(800, 40, 3, 1.2)
    corner = field.at(390, 390)
    assert abs(corner - field.at(390, 380)) < 60
    assert field.min_height() <= field.at(0, 0) <= field.max_height()
    assert 0 <= field.slope_deg(120, -80) <= 90


def test_relief_scales_the_terrain():
    calm = Heightfield.generate(1000, 40, 5, 0.4)
    wild = Heightfield.generate(1000, 40, 5, 1.6)
    assert (wild.max_height() - wild.min_height()) > (calm.max_height() - calm.min_height())


def test_fbm_stays_in_range():
    values = [fbm(x * 0.01, z * 0.01, 42) for x in range(-40, 40) for z in range(-40, 40)]
    assert min(values) >= -1.0 and max(values) <= 1.0


def test_graph_detects_a_disconnected_island():
    graph = _graph({"a": (0, 0), "b": (100, 0), "c": (400, 0)}, [("a", "b")])
    assert len(graph.components()) == 2
    assert graph.reachable_from("a") == {"a", "b"}
    codes = {issue["code"] for issue in graph.validate()}
    assert "disconnected_area" in codes


def test_graph_finds_shortest_route():
    graph = _graph({"a": (0, 0), "b": (100, 0), "c": (300, 0)}, [("a", "b"), ("b", "c"), ("a", "c")])
    assert graph.path_between("a", "c") == ["a", "c"]
    assert graph.total_length() == 600


def test_loop_and_dead_end_detection():
    ring = _graph({"a": (0, 0), "b": (10, 0), "c": (5, 10)}, [("a", "b"), ("b", "c"), ("c", "a")])
    assert ring.has_cycle()
    tip = _graph({"a": (0, 0), "b": (10, 0), "tip": (20, 0)}, [("a", "b"), ("b", "tip")])
    assert "tip" in tip.dead_ends()
    codes = {issue["code"] for issue in tip.validate()}
    assert "no_loop" in codes


def test_path_geometry_helpers():
    points = [(0, 0), (0, 100), (100, 100)]
    assert abs(polyline_length(points) - 200) < 1e-6
    assert distance_to_paths(50, 50, [{"nodes": points, "width": 10}]) > 20
    assert distance_to_paths(0, 50, [{"nodes": points, "width": 10}]) == 0


def test_spec_rejects_missing_sections():
    spec = WorldSpec({"schema_version": 6, "idea": "x" * 10, "title": "T"})
    codes = {issue["code"] for issue in spec.validate()}
    assert "missing_regions" in codes and "missing_world" in codes


def test_spec_rejects_duplicate_ids():
    spec = WorldSpec({
        "schema_version": 6, "idea": "a world with two things", "title": "T",
        "world": {"size": 1000, "seed": 1, "water_level": 0},
        "regions": [{"id": "r1", "name": "A", "kind": "hub", "center": [0, 0], "radius": 100}],
        "pois": [{"id": "r1", "name": "P", "kind": "monument", "region": "r1", "x": 0, "z": 0}],
        "paths": [], "spawns": [{"id": "spawn", "x": 0, "z": 0}],
        "art_direction": {"palette": {"primary": "#112233"}},
        "asset_manifest": {"assets": []}, "placements": [],
        "navigation_report": {"passed": True, "issues": []},
    })
    codes = {issue["code"] for issue in spec.validate()}
    assert "duplicate_id" in codes


if __name__ == "__main__":
    for name, fn in sorted(list(globals().items())):
        if name.startswith("test_"):
            fn()
            print("ok", name)
