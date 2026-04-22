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
    zone_tag: str
    important_for_circulation: bool = False


ROOMS: List[RoomSpec] = [
    RoomSpec("living", 22, 38, "day", True),
    RoomSpec("kitchen", 8, 18, "day", True),
    RoomSpec("bedroom_1", 9, 18, "night", True),
    RoomSpec("bedroom_2", 9, 18, "night", True),
    RoomSpec("bedroom_3", 9, 16, "night", True),
    RoomSpec("bathroom", 4, 10, "service", True),
    RoomSpec("wc", 2, 5, "service", False),
]

ZONES: Dict[int, Dict[str, object]] = {
    0: {"x": 0, "y": 0, "w": 8, "h": 4, "tag": "day"},
    1: {"x": 8, "y": 0, "w": 4, "h": 4, "tag": "day"},
    2: {"x": 0, "y": 4, "w": 6, "h": 6, "tag": "night"},
    3: {"x": 6, "y": 4, "w": 6, "h": 6, "tag": "night"},
    4: {"x": 0, "y": 10, "w": 6, "h": 2, "tag": "service"},
    5: {"x": 6, "y": 10, "w": 6, "h": 2, "tag": "service"},
}

ZONE_NEIGHBORS: Dict[int, List[int]] = {
    0: [1, 2, 3],
    1: [0, 3],
    2: [0, 3, 4],
    3: [0, 1, 2, 5],
    4: [2, 5],
    5: [3, 4],
}

MODE_WEIGHTS = {
    "balanced": {
        "compactness": 3,
        "zoning": 4,
        "living_dominance": 5,
        "kitchen_living": 14,
        "kitchen_isolation_malus": -20,
        "connected_bedrooms": 9,
        "bedroom_cluster": 6,
        "isolated_bedrooms": -12,
        "circulation": 10,
    },
    "strict_connectivity": {
        "compactness": 2,
        "zoning": 3,
        "living_dominance": 5,
        "kitchen_living": 24,
        "kitchen_isolation_malus": -35,
        "connected_bedrooms": 12,
        "bedroom_cluster": 10,
        "isolated_bedrooms": -18,
        "circulation": 14,
    },
    "zoning_first": {
        "compactness": 3,
        "zoning": 8,
        "living_dominance": 6,
        "kitchen_living": 10,
        "kitchen_isolation_malus": -16,
        "connected_bedrooms": 8,
        "bedroom_cluster": 5,
        "isolated_bedrooms": -10,
        "circulation": 9,
    },
}


class FloorplanGeneratorV5:
    def __init__(self, output_dir: str = "floorplan/out") -> None:
        self.output_dir = Path(output_dir)
        self.output_dir.mkdir(parents=True, exist_ok=True)

    def generate_variants(self, variants_per_mode: int = 2) -> List[Dict[str, object]]:
        results: List[Dict[str, object]] = []
        for mode in MODE_WEIGHTS:
            blocked_layouts: List[Tuple[int, ...]] = []
            for rank in range(1, variants_per_mode + 1):
                variant = self._solve_one(mode=mode, blocked_layouts=blocked_layouts, rank=rank)
                if variant is None:
                    break
                blocked_layouts.append(tuple(variant["zones"][room.name] for room in ROOMS))
                results.append(variant)
        return results

    def _solve_one(self, mode: str, blocked_layouts: List[Tuple[int, ...]], rank: int) -> Dict[str, object] | None:
        model = cp_model.CpModel()
        weights = MODE_WEIGHTS[mode]

        area: Dict[str, cp_model.IntVar] = {}
        zone: Dict[str, cp_model.IntVar] = {}
        in_zone: Dict[Tuple[str, int], cp_model.BoolVar] = {}

        for spec in ROOMS:
            area[spec.name] = model.NewIntVar(spec.min_area, spec.max_area, f"area_{spec.name}")
            zone[spec.name] = model.NewIntVar(0, len(ZONES) - 1, f"zone_{spec.name}")
            for z in ZONES:
                b = model.NewBoolVar(f"{spec.name}_in_zone_{z}")
                in_zone[(spec.name, z)] = b
                model.Add(zone[spec.name] == z).OnlyEnforceIf(b)
                model.Add(zone[spec.name] != z).OnlyEnforceIf(b.Not())
            model.AddExactlyOne(in_zone[(spec.name, z)] for z in ZONES)

        # Basic area / room quality rules
        total_area = model.NewIntVar(63, 123, "total_area")
        model.Add(total_area == sum(area.values()))
        model.Add(area["living"] >= area["kitchen"] + 6)
        for bedroom in ["bedroom_1", "bedroom_2", "bedroom_3"]:
            model.Add(area["living"] >= area[bedroom] + 4)

        # Zoning preference (soft scoring term)
        zoning_hits_terms: List[cp_model.BoolVar] = []
        for spec in ROOMS:
            tag_matches: List[cp_model.BoolVar] = []
            for z, info in ZONES.items():
                if info["tag"] == spec.zone_tag:
                    tag_matches.append(in_zone[(spec.name, z)])
            hit = model.NewBoolVar(f"zoning_hit_{spec.name}")
            model.AddBoolOr(tag_matches).OnlyEnforceIf(hit)
            model.AddBoolAnd([b.Not() for b in tag_matches]).OnlyEnforceIf(hit.Not())
            zoning_hits_terms.append(hit)

        zoning_score = model.NewIntVar(0, len(ROOMS), "zoning_score")
        model.Add(zoning_score == sum(zoning_hits_terms))

        # Pairwise adjacency based on zone map
        adjacency: Dict[Tuple[str, str], cp_model.BoolVar] = {}
        proximity: Dict[Tuple[str, str], cp_model.BoolVar] = {}

        def sorted_pair(a: str, b: str) -> Tuple[str, str]:
            return (a, b) if a < b else (b, a)

        room_names = [r.name for r in ROOMS]
        for i, room_a in enumerate(room_names):
            for room_b in room_names[i + 1 :]:
                pair = sorted_pair(room_a, room_b)
                adj_terms: List[cp_model.BoolVar] = []
                prox_terms: List[cp_model.BoolVar] = []

                for z in ZONES:
                    same = model.NewBoolVar(f"same_{room_a}_{room_b}_{z}")
                    model.AddBoolAnd([in_zone[(room_a, z)], in_zone[(room_b, z)]]).OnlyEnforceIf(same)
                    model.AddBoolOr([in_zone[(room_a, z)].Not(), in_zone[(room_b, z)].Not()]).OnlyEnforceIf(same.Not())
                    adj_terms.append(same)
                    prox_terms.append(same)

                for za, neighbors in ZONE_NEIGHBORS.items():
                    for zb in neighbors:
                        if za < zb:
                            edge = model.NewBoolVar(f"edge_{room_a}_{room_b}_{za}_{zb}")
                            model.AddBoolAnd([in_zone[(room_a, za)], in_zone[(room_b, zb)]]).OnlyEnforceIf(edge)
                            model.AddBoolOr([in_zone[(room_a, za)].Not(), in_zone[(room_b, zb)].Not()]).OnlyEnforceIf(edge.Not())
                            adj_terms.append(edge)
                            prox_terms.append(edge)

                            edge_reverse = model.NewBoolVar(f"edge_{room_a}_{room_b}_{zb}_{za}")
                            model.AddBoolAnd([in_zone[(room_a, zb)], in_zone[(room_b, za)]]).OnlyEnforceIf(edge_reverse)
                            model.AddBoolOr([in_zone[(room_a, zb)].Not(), in_zone[(room_b, za)].Not()]).OnlyEnforceIf(edge_reverse.Not())
                            adj_terms.append(edge_reverse)
                            prox_terms.append(edge_reverse)

                adj = model.NewBoolVar(f"adj_{room_a}_{room_b}")
                model.AddMaxEquality(adj, adj_terms)
                adjacency[pair] = adj

                prox = model.NewBoolVar(f"prox_{room_a}_{room_b}")
                model.AddMaxEquality(prox, prox_terms)
                proximity[pair] = prox

        def pair_var(store: Dict[Tuple[str, str], cp_model.BoolVar], a: str, b: str) -> cp_model.BoolVar:
            return store[sorted_pair(a, b)]

        # Compactness: reward grouping rooms into fewer zones
        zone_used: Dict[int, cp_model.BoolVar] = {}
        for z in ZONES:
            used = model.NewBoolVar(f"zone_used_{z}")
            zone_used[z] = used
            model.AddBoolOr([in_zone[(r.name, z)] for r in ROOMS]).OnlyEnforceIf(used)
            model.AddBoolAnd([in_zone[(r.name, z)].Not() for r in ROOMS]).OnlyEnforceIf(used.Not())

        used_zone_count = model.NewIntVar(1, len(ZONES), "used_zone_count")
        model.Add(used_zone_count == sum(zone_used.values()))
        compactness_score = model.NewIntVar(0, len(ZONES), "compactness_score")
        model.Add(compactness_score == len(ZONES) - used_zone_count)

        # Kitchen <-> living connectivity
        kitchen_living_adj = pair_var(adjacency, "kitchen", "living")
        kitchen_living_prox = pair_var(proximity, "kitchen", "living")
        kitchen_connected_to_living = model.NewBoolVar("kitchen_connected_to_living")
        model.AddMaxEquality(kitchen_connected_to_living, [kitchen_living_adj, kitchen_living_prox])
        kitchen_isolated = model.NewIntVar(0, 1, "kitchen_isolated")
        model.Add(kitchen_isolated == 1 - kitchen_connected_to_living)

        if mode == "strict_connectivity":
            model.Add(kitchen_connected_to_living == 1)

        # Bedroom connectivity and group behavior
        bedroom_names = ["bedroom_1", "bedroom_2", "bedroom_3"]
        bedroom_connected_to_other: Dict[str, cp_model.BoolVar] = {}
        bedroom_connected_to_living: Dict[str, cp_model.BoolVar] = {}
        bedroom_not_isolated: Dict[str, cp_model.BoolVar] = {}
        isolated_bedroom_vars: Dict[str, cp_model.IntVar] = {}

        for bedroom in bedroom_names:
            adj_to_other_terms = [
                pair_var(adjacency, bedroom, other)
                for other in bedroom_names
                if other != bedroom
            ]
            connected_other = model.NewBoolVar(f"{bedroom}_connected_to_bedroom")
            model.AddMaxEquality(connected_other, adj_to_other_terms)
            bedroom_connected_to_other[bedroom] = connected_other

            connected_living = pair_var(adjacency, bedroom, "living")
            bedroom_connected_to_living[bedroom] = connected_living

            not_isolated = model.NewBoolVar(f"{bedroom}_not_isolated")
            model.AddMaxEquality(not_isolated, [connected_other, connected_living])
            bedroom_not_isolated[bedroom] = not_isolated

            isolated = model.NewIntVar(0, 1, f"{bedroom}_isolated")
            model.Add(isolated == 1 - not_isolated)
            isolated_bedroom_vars[bedroom] = isolated

        connected_bedrooms = model.NewIntVar(0, len(bedroom_names), "connected_bedrooms")
        model.Add(connected_bedrooms == sum(bedroom_connected_to_other.values()))

        isolated_bedrooms = model.NewIntVar(0, len(bedroom_names), "isolated_bedrooms")
        model.Add(isolated_bedrooms == sum(isolated_bedroom_vars.values()))

        pairwise_bedroom_adjacency = []
        for i, a in enumerate(bedroom_names):
            for b in bedroom_names[i + 1 :]:
                pairwise_bedroom_adjacency.append(pair_var(adjacency, a, b))
        bedroom_cluster_score = model.NewIntVar(0, len(pairwise_bedroom_adjacency), "bedroom_cluster_score")
        model.Add(bedroom_cluster_score == sum(pairwise_bedroom_adjacency))

        # Circulation proxy: every important room should be adjacent/proximate to living
        circulation_terms = []
        for spec in ROOMS:
            if spec.name == "living" or not spec.important_for_circulation:
                continue
            access = model.NewBoolVar(f"access_to_living_{spec.name}")
            adj = pair_var(adjacency, spec.name, "living")
            prox = pair_var(proximity, spec.name, "living")
            model.AddMaxEquality(access, [adj, prox])
            circulation_terms.append(access)

        circulation_access = model.NewIntVar(0, len(circulation_terms), "circulation_access")
        model.Add(circulation_access == sum(circulation_terms))

        # Aggregate connectivity score (explicit IntVar, never raw SumArray in metrics)
        connectivity_score = model.NewIntVar(0, 100, "connectivity_score")
        model.Add(
            connectivity_score
            == 10 * kitchen_connected_to_living
            + 4 * connected_bedrooms
            + 6 * bedroom_cluster_score
            + 5 * circulation_access
            - 8 * isolated_bedrooms
        )

        # Penalize too many rooms in one zone for readability (soft diversity)
        overcrowding_terms = []
        for z in ZONES:
            zone_population = model.NewIntVar(0, len(ROOMS), f"zone_population_{z}")
            model.Add(zone_population == sum(in_zone[(r.name, z)] for r in ROOMS))
            overcrowded = model.NewBoolVar(f"overcrowded_{z}")
            model.Add(zone_population >= 4).OnlyEnforceIf(overcrowded)
            model.Add(zone_population <= 3).OnlyEnforceIf(overcrowded.Not())
            overcrowding_terms.append(overcrowded)

        overcrowding_penalty = model.NewIntVar(0, len(ZONES), "overcrowding_penalty")
        model.Add(overcrowding_penalty == sum(overcrowding_terms))

        # Final score
        score = model.NewIntVar(-1000, 3000, "score")
        model.Add(
            score
            == weights["compactness"] * compactness_score
            + weights["zoning"] * zoning_score
            + weights["living_dominance"] * area["living"]
            + weights["kitchen_living"] * kitchen_living_adj
            + weights["kitchen_isolation_malus"] * kitchen_isolated
            + weights["connected_bedrooms"] * connected_bedrooms
            + weights["bedroom_cluster"] * bedroom_cluster_score
            + weights["isolated_bedrooms"] * isolated_bedrooms
            + weights["circulation"] * circulation_access
            - 4 * overcrowding_penalty
        )

        for blocked in blocked_layouts:
            model.AddBoolOr(
                [in_zone[(room.name, blocked[i])].Not() for i, room in enumerate(ROOMS)]
            )

        model.Maximize(score)
        solver = cp_model.CpSolver()
        solver.parameters.max_time_in_seconds = 10
        solver.parameters.num_search_workers = 8
        status = solver.Solve(model)
        if status not in (cp_model.OPTIMAL, cp_model.FEASIBLE):
            return None

        room_zones = {spec.name: solver.Value(zone[spec.name]) for spec in ROOMS}
        room_areas = {spec.name: solver.Value(area[spec.name]) for spec in ROOMS}

        svg_path = self._export_svg(mode, rank, room_zones, room_areas)

        metrics = {
            "isolated_bedrooms": solver.Value(isolated_bedrooms),
            "connected_bedrooms": solver.Value(connected_bedrooms),
            "kitchen_connected_to_living": solver.Value(kitchen_connected_to_living),
            "connectivity_score": solver.Value(connectivity_score),
            "zoning_score": solver.Value(zoning_score),
            "compactness_score": solver.Value(compactness_score),
            "circulation_access": solver.Value(circulation_access),
        }

        return {
            "mode": mode,
            "rank": rank,
            "score": solver.Value(score),
            "areas": room_areas,
            "zones": room_zones,
            "metrics": metrics,
            "svg_path": str(svg_path),
        }

    def _export_svg(
        self,
        mode: str,
        rank: int,
        room_zones: Dict[str, int],
        room_areas: Dict[str, int],
    ) -> Path:
        grouped: Dict[int, List[str]] = {z: [] for z in ZONES}
        for room_name, zone in room_zones.items():
            grouped[zone].append(room_name)

        scale = 45
        svg_width = 12 * scale
        svg_height = 12 * scale

        colors = {
            "living": "#fca5a5",
            "kitchen": "#fdba74",
            "bedroom_1": "#86efac",
            "bedroom_2": "#4ade80",
            "bedroom_3": "#22c55e",
            "bathroom": "#93c5fd",
            "wc": "#60a5fa",
        }

        svg_parts = [
            f'<svg xmlns="http://www.w3.org/2000/svg" width="{svg_width}" height="{svg_height}" viewBox="0 0 {svg_width} {svg_height}">',
            '<rect x="0" y="0" width="100%" height="100%" fill="#f8fafc"/>',
            '<text x="16" y="24" font-family="Arial" font-size="16" fill="#0f172a">Floorplan V5 - '
            + mode
            + f' #{rank}</text>',
        ]

        for zone_id, rooms in grouped.items():
            if not rooms:
                continue
            z = ZONES[zone_id]
            zx, zy = int(z["x"] * scale), int(z["y"] * scale)
            zw, zh = int(z["w"] * scale), int(z["h"] * scale)
            total_zone_area = sum(room_areas[r] for r in rooms)
            running_y = zy
            for idx, room in enumerate(sorted(rooms)):
                ratio = room_areas[room] / total_zone_area if total_zone_area else 1 / len(rooms)
                h = zh - (running_y - zy) if idx == len(rooms) - 1 else max(32, int(zh * ratio))
                svg_parts.append(
                    f'<rect x="{zx}" y="{running_y}" width="{zw}" height="{h}" '
                    f'fill="{colors.get(room, "#cbd5e1")}" stroke="#0f172a" stroke-width="2"/>'
                )
                svg_parts.append(
                    f'<text x="{zx + 8}" y="{running_y + 22}" font-family="Arial" font-size="14" fill="#111827">'
                    f'{room} ({room_areas[room]}m²)</text>'
                )
                running_y += h

        svg_parts.append("</svg>")
        path = self.output_dir / f"v5_{mode}_{rank}.svg"
        path.write_text("\n".join(svg_parts), encoding="utf-8")
        return path
