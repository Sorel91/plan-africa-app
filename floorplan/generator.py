from __future__ import annotations

from dataclasses import dataclass
from pathlib import Path
from typing import Dict, List, Tuple

from ortools.sat.python import cp_model


@dataclass(frozen=True)
class RoomSpec:
    name: str
    min_area: int
    max_area: int
    zone_family: str
    important: bool = False


ROOMS: List[RoomSpec] = [
    RoomSpec("living", 24, 40, "day", True),
    RoomSpec("kitchen", 8, 16, "day", True),
    RoomSpec("bedroom_1", 9, 16, "night", True),
    RoomSpec("bedroom_2", 9, 16, "night", True),
    RoomSpec("bedroom_3", 8, 14, "night", True),
    RoomSpec("bathroom", 4, 9, "service", True),
    RoomSpec("wc", 2, 5, "service", False),
]

ZONE_GEOMETRY = {
    0: {"x": 0, "y": 0, "w": 6, "h": 4, "family": "day"},
    1: {"x": 6, "y": 0, "w": 6, "h": 4, "family": "day"},
    2: {"x": 0, "y": 4, "w": 4, "h": 4, "family": "transition"},
    3: {"x": 4, "y": 4, "w": 4, "h": 4, "family": "night"},
    4: {"x": 8, "y": 4, "w": 4, "h": 4, "family": "night"},
    5: {"x": 0, "y": 8, "w": 6, "h": 4, "family": "service"},
    6: {"x": 6, "y": 8, "w": 6, "h": 4, "family": "night"},
}

ZONE_NEIGHBORS = {
    0: [1, 2, 3],
    1: [0, 3, 4],
    2: [0, 3, 5],
    3: [0, 1, 2, 4, 6],
    4: [1, 3, 6],
    5: [2, 6],
    6: [3, 4, 5],
}

MODE_WEIGHTS = {
    "balanced": {
        "kitchen_adj": 40,
        "kitchen_connected": 22,
        "kitchen_isolated": -60,
        "bedroom_connected": 14,
        "bedroom_group": 15,
        "isolated_bedroom": -22,
        "circulation": 12,
        "compactness": 5,
        "zoning": 7,
        "living_dominance": 2,
    },
    "strict_connectivity": {
        "kitchen_adj": 55,
        "kitchen_connected": 26,
        "kitchen_isolated": -90,
        "bedroom_connected": 16,
        "bedroom_group": 18,
        "isolated_bedroom": -28,
        "circulation": 15,
        "compactness": 4,
        "zoning": 6,
        "living_dominance": 2,
    },
    "zoning_first": {
        "kitchen_adj": 28,
        "kitchen_connected": 18,
        "kitchen_isolated": -45,
        "bedroom_connected": 12,
        "bedroom_group": 12,
        "isolated_bedroom": -18,
        "circulation": 10,
        "compactness": 5,
        "zoning": 12,
        "living_dominance": 3,
    },
}


def _compute_zone_distances() -> Dict[Tuple[int, int], int]:
    # BFS from each node on the zone graph
    distances: Dict[Tuple[int, int], int] = {}
    for start in ZONE_GEOMETRY:
        frontier = [start]
        visited = {start: 0}
        while frontier:
            current = frontier.pop(0)
            for nxt in ZONE_NEIGHBORS[current]:
                if nxt in visited:
                    continue
                visited[nxt] = visited[current] + 1
                frontier.append(nxt)
        for end in ZONE_GEOMETRY:
            distances[(start, end)] = visited.get(end, 99)
    return distances


ZONE_DISTANCES = _compute_zone_distances()


class FloorplanGeneratorV5:
    def __init__(self, output_dir: str = "floorplan/out") -> None:
        self.output_dir = Path(output_dir)
        self.output_dir.mkdir(parents=True, exist_ok=True)

    def generate_variants(self, variants_per_mode: int = 3) -> List[Dict[str, object]]:
        all_variants: List[Dict[str, object]] = []
        for mode in MODE_WEIGHTS:
            blocked: List[Tuple[int, ...]] = []
            for rank in range(1, variants_per_mode + 1):
                variant = self._solve_variant(mode=mode, rank=rank, blocked_layouts=blocked)
                if variant is None:
                    break
                signature = tuple(variant["zones"][room.name] for room in ROOMS)
                blocked.append(signature)
                all_variants.append(variant)
        return all_variants

    def _solve_variant(
        self,
        mode: str,
        rank: int,
        blocked_layouts: List[Tuple[int, ...]],
    ) -> Dict[str, object] | None:
        weights = MODE_WEIGHTS[mode]
        model = cp_model.CpModel()

        room_names = [r.name for r in ROOMS]
        bedrooms = ["bedroom_1", "bedroom_2", "bedroom_3"]
        zone_ids = list(ZONE_GEOMETRY.keys())

        areas = {
            room.name: model.NewIntVar(room.min_area, room.max_area, f"area_{room.name}")
            for room in ROOMS
        }
        zones = {
            room.name: model.NewIntVar(min(zone_ids), max(zone_ids), f"zone_{room.name}")
            for room in ROOMS
        }

        # Living remains the dominant room.
        for room in room_names:
            if room != "living":
                model.Add(areas["living"] >= areas[room] + 4)

        total_area = model.NewIntVar(64, 125, "total_area")
        model.Add(total_area == sum(areas.values()))

        adjacency: Dict[Tuple[str, str], cp_model.IntVar] = {}
        near: Dict[Tuple[str, str], cp_model.IntVar] = {}

        def key(a: str, b: str) -> Tuple[str, str]:
            return (a, b) if a < b else (b, a)

        # Pairwise relation table: avoid risky expression tricks.
        for i, a in enumerate(room_names):
            for b in room_names[i + 1 :]:
                adj = model.NewBoolVar(f"adj_{a}_{b}")
                adjacency[key(a, b)] = adj

                near_var = model.NewBoolVar(f"near_{a}_{b}")
                near[key(a, b)] = near_var

                adj_tuples = []
                near_tuples = []
                for za in zone_ids:
                    for zb in zone_ids:
                        is_adj = 1 if (za == zb or zb in ZONE_NEIGHBORS[za]) else 0
                        is_near = 1 if ZONE_DISTANCES[(za, zb)] <= 2 else 0
                        adj_tuples.append((za, zb, is_adj))
                        near_tuples.append((za, zb, is_near))

                model.AddAllowedAssignments([zones[a], zones[b], adj], adj_tuples)
                model.AddAllowedAssignments([zones[a], zones[b], near_var], near_tuples)

        def pair(d: Dict[Tuple[str, str], cp_model.IntVar], a: str, b: str) -> cp_model.IntVar:
            return d[key(a, b)]

        # Kitchen <-> living connectivity
        kitchen_adj_living = pair(adjacency, "kitchen", "living")
        kitchen_near_living = pair(near, "kitchen", "living")
        kitchen_connected_to_living = model.NewBoolVar("kitchen_connected_to_living")
        model.AddMaxEquality(kitchen_connected_to_living, [kitchen_adj_living, kitchen_near_living])

        kitchen_isolated = model.NewIntVar(0, 1, "kitchen_isolated")
        model.Add(kitchen_isolated == 1 - kitchen_connected_to_living)

        if mode == "strict_connectivity":
            model.Add(kitchen_adj_living == 1)

        # Bedroom connectivity
        connected_to_bedroom: Dict[str, cp_model.IntVar] = {}
        connected_to_living: Dict[str, cp_model.IntVar] = {}
        isolated_by_room: Dict[str, cp_model.IntVar] = {}

        for bed in bedrooms:
            bed_to_bed_terms = [pair(adjacency, bed, other) for other in bedrooms if other != bed]
            has_neighbor_bed = model.NewBoolVar(f"{bed}_has_neighbor_bed")
            model.AddMaxEquality(has_neighbor_bed, bed_to_bed_terms)
            connected_to_bedroom[bed] = has_neighbor_bed

            living_link = pair(adjacency, bed, "living")
            connected_to_living[bed] = living_link

            plausible_access = model.NewBoolVar(f"{bed}_plausible_access")
            model.AddMaxEquality(plausible_access, [has_neighbor_bed, living_link])

            isolated = model.NewIntVar(0, 1, f"{bed}_isolated")
            model.Add(isolated == 1 - plausible_access)
            isolated_by_room[bed] = isolated

        connected_bedrooms = model.NewIntVar(0, len(bedrooms), "connected_bedrooms")
        model.Add(connected_bedrooms == sum(connected_to_bedroom.values()))

        isolated_bedrooms = model.NewIntVar(0, len(bedrooms), "isolated_bedrooms")
        model.Add(isolated_bedrooms == sum(isolated_by_room.values()))

        bedroom_pair_edges = []
        for i, a in enumerate(bedrooms):
            for b in bedrooms[i + 1 :]:
                bedroom_pair_edges.append(pair(adjacency, a, b))

        bedroom_group_score = model.NewIntVar(0, len(bedroom_pair_edges), "bedroom_group_score")
        model.Add(bedroom_group_score == sum(bedroom_pair_edges))

        # Circulation proxy (important rooms close enough to living)
        circulation_access_terms: List[cp_model.IntVar] = []
        for room in ROOMS:
            if not room.important or room.name == "living":
                continue
            access = model.NewBoolVar(f"access_{room.name}_to_living")
            model.AddMaxEquality(
                access,
                [
                    pair(adjacency, room.name, "living"),
                    pair(near, room.name, "living"),
                ],
            )
            circulation_access_terms.append(access)

        circulation_access = model.NewIntVar(0, len(circulation_access_terms), "circulation_access")
        model.Add(circulation_access == sum(circulation_access_terms))

        # Zoning score from zone family matching
        zoning_hits = []
        for room in ROOMS:
            hit = model.NewBoolVar(f"zoning_hit_{room.name}")
            allowed = [z for z, info in ZONE_GEOMETRY.items() if info["family"] in (room.zone_family, "transition")]
            model.AddAllowedAssignments([zones[room.name], hit], [(z, 1) for z in allowed] + [(z, 0) for z in zone_ids if z not in allowed])
            zoning_hits.append(hit)

        zoning_score = model.NewIntVar(0, len(ROOMS), "zoning_score")
        model.Add(zoning_score == sum(zoning_hits))

        # Compactness: reward shared zones / nearby grouping.
        zone_used = {z: model.NewBoolVar(f"zone_used_{z}") for z in zone_ids}
        for z in zone_ids:
            room_in_z = []
            for room in room_names:
                in_z = model.NewBoolVar(f"{room}_in_{z}")
                model.Add(zones[room] == z).OnlyEnforceIf(in_z)
                model.Add(zones[room] != z).OnlyEnforceIf(in_z.Not())
                room_in_z.append(in_z)
            model.AddMaxEquality(zone_used[z], room_in_z)

        used_zones = model.NewIntVar(1, len(zone_ids), "used_zones")
        model.Add(used_zones == sum(zone_used.values()))

        compactness_score = model.NewIntVar(0, len(zone_ids), "compactness_score")
        model.Add(compactness_score == len(zone_ids) - used_zones)

        # Explicit aggregated connectivity metric (IntVar, no raw SumArray usage in output)
        connectivity_score = model.NewIntVar(-100, 200, "connectivity_score")
        model.Add(
            connectivity_score
            == 30 * kitchen_connected_to_living
            + 10 * connected_bedrooms
            + 12 * bedroom_group_score
            + 8 * circulation_access
            - 15 * isolated_bedrooms
        )

        # Final score
        score = model.NewIntVar(-5000, 5000, "score")
        model.Add(
            score
            == weights["kitchen_adj"] * kitchen_adj_living
            + weights["kitchen_connected"] * kitchen_connected_to_living
            + weights["kitchen_isolated"] * kitchen_isolated
            + weights["bedroom_connected"] * connected_bedrooms
            + weights["bedroom_group"] * bedroom_group_score
            + weights["isolated_bedroom"] * isolated_bedrooms
            + weights["circulation"] * circulation_access
            + weights["compactness"] * compactness_score
            + weights["zoning"] * zoning_score
            + weights["living_dominance"] * areas["living"]
        )

        # Variant diversity across solves in same mode
        for blocked in blocked_layouts:
            differences = []
            for idx, room in enumerate(room_names):
                different = model.NewBoolVar(f"{room}_not_{blocked[idx]}_{len(differences)}")
                model.Add(zones[room] != blocked[idx]).OnlyEnforceIf(different)
                model.Add(zones[room] == blocked[idx]).OnlyEnforceIf(different.Not())
                differences.append(different)
            model.AddBoolOr(differences)

        model.Maximize(score)
        solver = cp_model.CpSolver()
        solver.parameters.max_time_in_seconds = 10.0
        solver.parameters.num_search_workers = 8

        status = solver.Solve(model)
        if status not in (cp_model.OPTIMAL, cp_model.FEASIBLE):
            return None

        solved_areas = {name: solver.Value(var) for name, var in areas.items()}
        solved_zones = {name: solver.Value(var) for name, var in zones.items()}

        svg_path = self._export_svg(mode, rank, solved_areas, solved_zones)

        metrics = {
            "isolated_bedrooms": solver.Value(isolated_bedrooms),
            "connected_bedrooms": solver.Value(connected_bedrooms),
            "kitchen_connected_to_living": solver.Value(kitchen_connected_to_living),
            "connectivity_score": solver.Value(connectivity_score),
            "circulation_access": solver.Value(circulation_access),
            "zoning_score": solver.Value(zoning_score),
            "compactness_score": solver.Value(compactness_score),
        }

        return {
            "mode": mode,
            "rank": rank,
            "score": solver.Value(score),
            "areas": solved_areas,
            "zones": solved_zones,
            "metrics": metrics,
            "svg_path": str(svg_path),
        }

    def _export_svg(
        self,
        mode: str,
        rank: int,
        solved_areas: Dict[str, int],
        solved_zones: Dict[str, int],
    ) -> Path:
        grouped: Dict[int, List[str]] = {z: [] for z in ZONE_GEOMETRY}
        for room, z in solved_zones.items():
            grouped[z].append(room)

        colors = {
            "living": "#fecaca",
            "kitchen": "#fdba74",
            "bedroom_1": "#86efac",
            "bedroom_2": "#4ade80",
            "bedroom_3": "#22c55e",
            "bathroom": "#93c5fd",
            "wc": "#60a5fa",
        }

        scale = 52
        width = 12 * scale
        height = 12 * scale

        chunks = [
            f'<svg xmlns="http://www.w3.org/2000/svg" width="{width}" height="{height}" viewBox="0 0 {width} {height}">',
            '<rect x="0" y="0" width="100%" height="100%" fill="#f8fafc"/>',
            f'<text x="14" y="26" font-size="16" font-family="Arial">V5 {mode} #{rank}</text>',
        ]

        for z, rooms in grouped.items():
            if not rooms:
                continue
            geom = ZONE_GEOMETRY[z]
            zx = geom["x"] * scale
            zy = geom["y"] * scale
            zw = geom["w"] * scale
            zh = geom["h"] * scale

            total = sum(solved_areas[r] for r in rooms)
            current_y = zy
            for idx, room in enumerate(sorted(rooms)):
                if idx == len(rooms) - 1:
                    rh = zy + zh - current_y
                else:
                    ratio = solved_areas[room] / total if total else 1 / len(rooms)
                    rh = max(32, int(zh * ratio))

                chunks.append(
                    f'<rect x="{zx}" y="{current_y}" width="{zw}" height="{rh}" '
                    f'fill="{colors.get(room, "#cbd5e1")}" stroke="#0f172a" stroke-width="2"/>'
                )
                chunks.append(
                    f'<text x="{zx + 7}" y="{current_y + 20}" font-size="13" font-family="Arial" fill="#111827">'
                    f'{room} ({solved_areas[room]}m²)</text>'
                )
                current_y += rh

        chunks.append("</svg>")
        path = self.output_dir / f"v5_{mode}_{rank}.svg"
        path.write_text("\n".join(chunks), encoding="utf-8")
        return path
