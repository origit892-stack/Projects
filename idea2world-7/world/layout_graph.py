"""Layout graph: routes, connectivity and the geometric questions QA needs to answer.

Pure geometry, no Roblox concepts, so it is unit-testable and can be reused by the SVG map preview.
"""
from __future__ import annotations

import heapq
import math
from typing import Iterable, Sequence

Point = tuple[float, float]


def polyline_length(points: Sequence[Point]) -> float:
    return sum(math.dist(points[i], points[i + 1]) for i in range(len(points) - 1))


def point_segment_distance(p: Point, a: Point, b: Point) -> float:
    ax, az = a
    bx, bz = b
    px, pz = p
    dx, dz = bx - ax, bz - az
    denom = dx * dx + dz * dz
    if denom == 0:
        return math.dist(p, a)
    t = max(0.0, min(1.0, ((px - ax) * dx + (pz - az) * dz) / denom))
    return math.hypot(px - (ax + t * dx), pz - (az + t * dz))


def distance_to_paths(x: float, z: float, paths: Iterable[dict]) -> float:
    best = float("inf")
    for path in paths:
        nodes = path.get("nodes") or []
        for i in range(len(nodes) - 1):
            d = point_segment_distance((x, z), tuple(nodes[i]), tuple(nodes[i + 1]))
            if d < best:
                best = d
    return best


def sample_polyline(points: Sequence[Point], spacing: float) -> list[Point]:
    if not points:
        return []
    if len(points) == 1 or spacing <= 0:
        return list(points)
    out: list[Point] = []
    carry = 0.0
    out.append(tuple(points[0]))
    for i in range(len(points) - 1):
        a, b = tuple(points[i]), tuple(points[i + 1])
        seg = math.dist(a, b)
        if seg <= 1e-9:
            continue
        travelled = carry
        while travelled < seg:
            t = travelled / seg
            out.append((a[0] + (b[0] - a[0]) * t, a[1] + (b[1] - a[1]) * t))
            travelled += spacing
        carry = travelled - seg
    out.append(tuple(points[-1]))
    return out


def path_midpoint(points: Sequence[Point]) -> Point:
    if not points:
        return (0.0, 0.0)
    if len(points) == 1:
        return tuple(points[0])
    total = polyline_length(points)
    target = total / 2.0
    walked = 0.0
    for i in range(len(points) - 1):
        a, b = tuple(points[i]), tuple(points[i + 1])
        seg = math.dist(a, b)
        if walked + seg >= target and seg > 0:
            t = (target - walked) / seg
            return (a[0] + (b[0] - a[0]) * t, a[1] + (b[1] - a[1]) * t)
        walked += seg
    return tuple(points[-1])


class LayoutGraph:
    def __init__(self):
        self.nodes: dict[str, Point] = {}
        self.meta: dict[str, dict] = {}
        self.edges: list[dict] = []

    # -- construction -----------------------------------------------------------------
    def add_node(self, node_id: str, point: Point, kind: str = "region", **meta) -> None:
        self.nodes[node_id] = (float(point[0]), float(point[1]))
        self.meta[node_id] = {"kind": kind, **meta}

    def add_edge(self, a: str, b: str, kind: str = "path", width: float = 10.0, path_id: str = "") -> None:
        if a not in self.nodes or b not in self.nodes or a == b:
            return
        self.edges.append({"a": a, "b": b, "kind": kind, "width": width,
                           "path_id": path_id or f"{a}->{b}",
                           "length": round(math.dist(self.nodes[a], self.nodes[b]), 2)})

    # -- queries ----------------------------------------------------------------------
    def neighbours(self, node_id: str) -> list[str]:
        out = []
        for e in self.edges:
            if e["a"] == node_id:
                out.append(e["b"])
            elif e["b"] == node_id:
                out.append(e["a"])
        return out

    def degree(self, node_id: str) -> int:
        return len(self.neighbours(node_id))

    def dijkstra(self, start: str, goal: str | None = None) -> tuple[dict[str, float], dict[str, str | None]]:
        dist: dict[str, float] = {n: float("inf") for n in self.nodes}
        prev: dict[str, str | None] = {n: None for n in self.nodes}
        if start not in self.nodes:
            return dist, prev
        dist[start] = 0.0
        pq = [(0.0, start)]
        while pq:
            d, node = heapq.heappop(pq)
            if d > dist[node]:
                continue
            if goal and node == goal:
                break
            for nb in self.neighbours(node):
                w = math.dist(self.nodes[node], self.nodes[nb])
                if d + w < dist[nb]:
                    dist[nb] = d + w
                    prev[nb] = node
                    heapq.heappush(pq, (d + w, nb))
        return dist, prev

    def path_between(self, start: str, goal: str) -> list[str]:
        dist, prev = self.dijkstra(start, goal)
        if start not in self.nodes or goal not in self.nodes or dist.get(goal, float("inf")) == float("inf"):
            return []
        out = [goal]
        while out[-1] != start and prev[out[-1]] is not None:
            out.append(prev[out[-1]])  # type: ignore[arg-type]
        return list(reversed(out))

    def components(self) -> list[list[str]]:
        seen: set[str] = set()
        comps: list[list[str]] = []
        for node in self.nodes:
            if node in seen:
                continue
            stack, comp = [node], []
            seen.add(node)
            while stack:
                cur = stack.pop()
                comp.append(cur)
                for nb in self.neighbours(cur):
                    if nb not in seen:
                        seen.add(nb)
                        stack.append(nb)
            comps.append(comp)
        return comps

    def is_connected(self) -> bool:
        return len(self.components()) <= 1

    def dead_ends(self) -> list[str]:
        return [n for n in self.nodes if self.degree(n) == 1]

    def has_cycle(self) -> bool:
        comps = self.components()
        for comp in comps:
            edge_count = sum(1 for e in self.edges if e["a"] in comp and e["b"] in comp)
            if edge_count >= len(comp):
                return True
        return False

    def total_length(self) -> float:
        return sum(e["length"] for e in self.edges)

    def reachable_from(self, start: str) -> set[str]:
        dist, _ = self.dijkstra(start)
        return {n for n, d in dist.items() if d < float("inf")}

    # -- validation -------------------------------------------------------------------
    def validate(self) -> list[dict]:
        issues: list[dict] = []
        comps = self.components()
        if len(comps) > 1:
            biggest = max(len(c) for c in comps)
            for comp in comps:
                if len(comp) != biggest:
                    issues.append({"code": "disconnected_area", "severity": "critical",
                                   "message": f"Isolated area(s): {', '.join(sorted(comp))}",
                                   "fix": "Connect the area with a path or remove it", "scope": "layout"})
        hubs = [n for n, m in self.meta.items() if m.get("kind") in ("region", "hub", "spawn")]
        for hub_id in hubs:
            if self.degree(hub_id) == 0:
                issues.append({"code": "orphan_region", "severity": "critical",
                               "message": f"Region '{hub_id}' has no path connection",
                               "fix": "Add a path to the main loop", "scope": "layout"})
        for node in self.dead_ends():
            kind = self.meta.get(node, {}).get("kind", "region")
            if kind in ("region", "hub"):
                issues.append({"code": "dead_end_region", "severity": "major",
                               "message": f"Path dead-ends at region '{node}'",
                               "fix": "Close the loop or add a second exit so players are not funneled into a wall",
                               "scope": "layout"})
        if not self.has_cycle():
            issues.append({"code": "no_loop", "severity": "major",
                           "message": "Layout has no loop; exploration will feel linear",
                           "fix": "Add a return path between two outer regions", "scope": "layout"})
        return issues


def graph_from_world_spec(spec) -> LayoutGraph:
    graph = LayoutGraph()
    for region in spec.regions:
        graph.add_node(region["id"], tuple(region.get("center", (0, 0))), kind="region",
                       label=region.get("name"), region_kind=region.get("kind"))
    for poi in spec.pois:
        graph.add_node(poi["id"], (poi.get("x", 0), poi.get("z", 0)), kind="poi",
                       label=poi.get("name"), poi_kind=poi.get("kind"), region=poi.get("region"))
        region_id = poi.get("region")
        if region_id in graph.nodes:
            graph.add_edge(region_id, poi["id"], kind="access", width=6.0, path_id=f"access_{poi['id']}")
    for path in spec.paths:
        nodes = path.get("nodes") or []
        connects = path.get("connects") or []
        if len(connects) >= 2:
            for i in range(len(connects) - 1):
                graph.add_edge(connects[i], connects[i + 1], kind=path.get("kind", "path"),
                               width=float(path.get("width", 10)), path_id=path.get("id", ""))
        elif len(nodes) >= 2:
            # Fall back to the two nearest region anchors.
            a = min(graph.nodes, key=lambda n: math.dist(graph.nodes[n], tuple(nodes[0]))) if graph.nodes else None
            b = min(graph.nodes, key=lambda n: math.dist(graph.nodes[n], tuple(nodes[-1]))) if graph.nodes else None
            if a and b:
                graph.add_edge(a, b, kind=path.get("kind", "path"),
                               width=float(path.get("width", 10)), path_id=path.get("id", ""))
    return graph
