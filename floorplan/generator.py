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
    RoomSpec("living", 22, 52, "day", True),
    RoomSpec("kitchen", 10, 24, "day", True),
    RoomSpec("bedroom_1", 10, 22, "night", True),
    RoomSpec("bedroom_2", 10, 22, "night", True),
    RoomSpec("bedroom_3", 9, 20, "night", True),
    RoomSpec("bathroom", 5, 12, "service", True),
    RoomSpec("wc", 3, 8, "service", False),
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
        "living_dominance": 4,
        "kitchen_living": 16,
        "kitchen_isolation_malus": -24,
        "connected_bedrooms": 10,
        "bedroom_cluster": 8,
        "isolated_bedrooms": -14,
        "bathroom_bedroom": 9,
        "wc_day_service": 4,
        "circulation": 12,
        "diversity": 8,
    },
    "strict_connectivity": {
        "compactness": 2,
        "zoning": 3,
        "living_dominance": 4,
        "kitchen_living": 26,
        "kitchen_isolation_malus": -40,
        "connected_bedrooms": 12,
        "bedroom_cluster": 10,
        "isolated_bedrooms": -20,
        "bathroom_bedroom": 10,
        "wc_day_service": 4,
        "circulation": 16,
        "diversity": 7,
    },
    "zoning_first": {
        "compactness": 3,
        "zoning": 10,
        "living_dominance": 5,
        "kitchen_living": 12,
        "kitchen_isolation_malus": -20,
        "connected_bedrooms": 8,
        "bedroom_cluster": 7,
        "isolated_bedrooms": -12,
        "bathroom_bedroom": 11,
        "wc_day_service": 5,
        "circulation": 10,
        "diversity": 7,
    },
}


class FloorplanGeneratorV5:
    def __init__(self, output_dir: str = "floorplan/out") -> None:
        self.output_dir = Path(output_dir)
        self.output_dir.mkdir(parents=True, exist_ok=True)

    def generate_variants(self, variants_per_mode: int = 2) -> List[Dict[str, object]]:
        results: List[Dict[str, object]] = []
        for mode in MODE_WEIGHTS:
            blocked_layouts: List[Dict[str, object]] = []
            for rank in range(1, variants_per_mode + 1):
                variant = self._solve_one(mode=mode, blocked_layouts=blocked_layouts, rank=rank)
                if variant is None:
                    break
                blocked_layouts.append(
                    {
                        "zones": tuple(variant["zones"][room.name] for room in ROOMS),
                        "centers": tuple(
                            (variant["rectangles"][room.name]["cx2"], variant["rectangles"][room.name]["cy2"])
                            for room in ROOMS
                        ),
                    }
                )
                results.append(variant)
        return results

    def _solve_one(self, mode: str, blocked_layouts: List[Dict[str, object]], rank: int) -> Dict[str, object] | None:
        model = cp_model.CpModel()
        weights = MODE_WEIGHTS[mode]

        width_limit = 12
        height_limit = 12

        area: Dict[str, cp_model.IntVar] = {}
        zone: Dict[str, cp_model.IntVar] = {}
        in_zone: Dict[Tuple[str, int], cp_model.BoolVar] = {}
        x: Dict[str, cp_model.IntVar] = {}
        y: Dict[str, cp_model.IntVar] = {}
        w: Dict[str, cp_model.IntVar] = {}
        h: Dict[str, cp_model.IntVar] = {}
        x_end: Dict[str, cp_model.IntVar] = {}
        y_end: Dict[str, cp_model.IntVar] = {}
        cx2: Dict[str, cp_model.IntVar] = {}
        cy2: Dict[str, cp_model.IntVar] = {}
        x_intervals: List[cp_model.IntervalVar] = []
        y_intervals: List[cp_model.IntervalVar] = []

        for spec in ROOMS:
            room_name = spec.name
            area[room_name] = model.NewIntVar(spec.min_area, spec.max_area, f"area_{room_name}")
            zone[room_name] = model.NewIntVar(0, len(ZONES) - 1, f"zone_{room_name}")

            w[room_name] = model.NewIntVar(2, 8, f"w_{room_name}")
            h[room_name] = model.NewIntVar(2, 8, f"h_{room_name}")
            x[room_name] = model.NewIntVar(0, width_limit - 2, f"x_{room_name}")
            y[room_name] = model.NewIntVar(0, height_limit - 2, f"y_{room_name}")
            x_end[room_name] = model.NewIntVar(2, width_limit, f"x_end_{room_name}")
            y_end[room_name] = model.NewIntVar(2, height_limit, f"y_end_{room_name}")

            model.Add(x_end[room_name] == x[room_name] + w[room_name])
            model.Add(y_end[room_name] == y[room_name] + h[room_name])
            model.Add(x_end[room_name] <= width_limit)
            model.Add(y_end[room_name] <= height_limit)
            model.AddMultiplicationEquality(area[room_name], [w[room_name], h[room_name]])

            cx2[room_name] = model.NewIntVar(0, 2 * width_limit, f"cx2_{room_name}")
            cy2[room_name] = model.NewIntVar(0, 2 * height_limit, f"cy2_{room_name}")
            model.Add(cx2[room_name] == 2 * x[room_name] + w[room_name])
            model.Add(cy2[room_name] == 2 * y[room_name] + h[room_name])

            x_intervals.append(model.NewIntervalVar(x[room_name], w[room_name], x_end[room_name], f"x_itv_{room_name}"))
            y_intervals.append(model.NewIntervalVar(y[room_name], h[room_name], y_end[room_name], f"y_itv_{room_name}"))

            for z in ZONES:
                b = model.NewBoolVar(f"{room_name}_in_zone_{z}")
                in_zone[(room_name, z)] = b
                model.Add(zone[room_name] == z).OnlyEnforceIf(b)
                model.Add(zone[room_name] != z).OnlyEnforceIf(b.Not())

            model.AddExactlyOne(in_zone[(room_name, z)] for z in ZONES)

        model.AddNoOverlap2D(x_intervals, y_intervals)

        # Anchor each room center to the selected zone.
        for spec in ROOMS:
            room_name = spec.name
            for z, info in ZONES.items():
                x_min = int(info["x"])
                y_min = int(info["y"])
                x_max = x_min + int(info["w"])
                y_max = y_min + int(info["h"])
                inside = in_zone[(room_name, z)]
                model.Add(cx2[room_name] >= 2 * x_min).OnlyEnforceIf(inside)
                model.Add(cx2[room_name] <= 2 * x_max).OnlyEnforceIf(inside)
                model.Add(cy2[room_name] >= 2 * y_min).OnlyEnforceIf(inside)
                model.Add(cy2[room_name] <= 2 * y_max).OnlyEnforceIf(inside)

        # Basic area / room quality rules.
        total_area = model.NewIntVar(63, 123, "total_area")
        model.Add(total_area == sum(area.values()))
        model.Add(area["living"] >= area["kitchen"] + 6)
        for bedroom in ["bedroom_1", "bedroom_2", "bedroom_3"]:
            model.Add(area["living"] >= area[bedroom] + 4)

        # Zoning preference (soft scoring term).
        zoning_hits_terms: List[cp_model.BoolVar] = []
        for spec in ROOMS:
            room_name = spec.name
            tag_matches = [in_zone[(room_name, z)] for z, info in ZONES.items() if info["tag"] == spec.zone_tag]
            hit = model.NewBoolVar(f"zoning_hit_{room_name}")
            model.AddBoolOr(tag_matches).OnlyEnforceIf(hit)
            model.AddBoolAnd([b.Not() for b in tag_matches]).OnlyEnforceIf(hit.Not())
            zoning_hits_terms.append(hit)

        zoning_score = model.NewIntVar(0, len(ROOMS), "zoning_score")
        model.Add(zoning_score == sum(zoning_hits_terms))

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

                            edge_reverse = model.NewBoolVar(f"edge_{room_a}_{room_b}_{zb}_{za}")
                            model.AddBoolAnd([in_zone[(room_a, zb)], in_zone[(room_b, za)]]).OnlyEnforceIf(edge_reverse)
                            model.AddBoolOr([in_zone[(room_a, zb)].Not(), in_zone[(room_b, za)].Not()]).OnlyEnforceIf(edge_reverse.Not())
                            adj_terms.append(edge_reverse)

                dx = model.NewIntVar(0, 2 * width_limit, f"dx_{room_a}_{room_b}")
                dy = model.NewIntVar(0, 2 * height_limit, f"dy_{room_a}_{room_b}")
                model.AddAbsEquality(dx, cx2[room_a] - cx2[room_b])
                model.AddAbsEquality(dy, cy2[room_a] - cy2[room_b])

                center_near = model.NewBoolVar(f"center_near_{room_a}_{room_b}")
                model.Add(dx + dy <= 16).OnlyEnforceIf(center_near)
                model.Add(dx + dy >= 17).OnlyEnforceIf(center_near.Not())

                prox_terms.append(center_near)
                adj_terms.append(center_near)

                adj = model.NewBoolVar(f"adj_{room_a}_{room_b}")
                model.AddMaxEquality(adj, adj_terms)
                adjacency[pair] = adj

                prox = model.NewBoolVar(f"prox_{room_a}_{room_b}")
                model.AddMaxEquality(prox, prox_terms)
                proximity[pair] = prox

        def pair_var(store: Dict[Tuple[str, str], cp_model.BoolVar], a: str, b: str) -> cp_model.BoolVar:
            return store[sorted_pair(a, b)]

        # Compactness: reward grouping rooms into fewer zones.
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

        # Day/night/service zoning targets.
        kitchen_living_adj = pair_var(adjacency, "kitchen", "living")
        kitchen_living_prox = pair_var(proximity, "kitchen", "living")
        kitchen_connected_to_living = model.NewBoolVar("kitchen_connected_to_living")
        model.AddMaxEquality(kitchen_connected_to_living, [kitchen_living_adj, kitchen_living_prox])

        kitchen_isolated = model.NewIntVar(0, 1, "kitchen_isolated")
        model.Add(kitchen_isolated == 1 - kitchen_connected_to_living)

        if mode == "strict_connectivity":
            model.Add(kitchen_connected_to_living == 1)

        bedroom_names = ["bedroom_1", "bedroom_2", "bedroom_3"]
        bedroom_connected_to_other: Dict[str, cp_model.BoolVar] = {}
        isolated_bedroom_vars: Dict[str, cp_model.IntVar] = {}

        for bedroom in bedroom_names:
            adj_to_other_terms = [pair_var(adjacency, bedroom, other) for other in bedroom_names if other != bedroom]
            connected_other = model.NewBoolVar(f"{bedroom}_connected_to_bedroom")
            model.AddMaxEquality(connected_other, adj_to_other_terms)
            bedroom_connected_to_other[bedroom] = connected_other

            connected_living = pair_var(adjacency, bedroom, "living")
            not_isolated = model.NewBoolVar(f"{bedroom}_not_isolated")
            model.AddMaxEquality(not_isolated, [connected_other, connected_living])

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

        bathroom_near_bedrooms_terms = [pair_var(adjacency, "bathroom", b) for b in bedroom_names]
        bathroom_near_bedrooms = model.NewIntVar(0, len(bedroom_names), "bathroom_near_bedrooms")
        model.Add(bathroom_near_bedrooms == sum(bathroom_near_bedrooms_terms))

        wc_day_service_hit = model.NewBoolVar("wc_day_service_hit")
        wc_day_service_terms = [in_zone[("wc", z)] for z, info in ZONES.items() if info["tag"] in {"day", "service"}]
        model.AddBoolOr(wc_day_service_terms).OnlyEnforceIf(wc_day_service_hit)
        model.AddBoolAnd([b.Not() for b in wc_day_service_terms]).OnlyEnforceIf(wc_day_service_hit.Not())

        # Circulation proxy: direct or one-hop access to living.
        circulation_terms = []
        hubs = ["kitchen", "bathroom", "bedroom_1", "bedroom_2", "bedroom_3"]
        for spec in ROOMS:
            if spec.name == "living" or not spec.important_for_circulation:
                continue

            direct = pair_var(adjacency, spec.name, "living")
            one_hop_candidates = [direct]
            for hub in hubs:
                if hub == spec.name:
                    continue
                hop = model.NewBoolVar(f"hop_{spec.name}_via_{hub}")
                model.AddBoolAnd([pair_var(adjacency, spec.name, hub), pair_var(adjacency, hub, "living")]).OnlyEnforceIf(hop)
                model.AddBoolOr([pair_var(adjacency, spec.name, hub).Not(), pair_var(adjacency, hub, "living").Not()]).OnlyEnforceIf(hop.Not())
                one_hop_candidates.append(hop)

            access = model.NewBoolVar(f"access_to_living_{spec.name}")
            model.AddMaxEquality(access, one_hop_candidates)
            circulation_terms.append(access)

        circulation_access = model.NewIntVar(0, len(circulation_terms), "circulation_access")
        model.Add(circulation_access == sum(circulation_terms))

        connectivity_score = model.NewIntVar(0, 200, "connectivity_score")
        model.Add(
            connectivity_score
            == 12 * kitchen_connected_to_living
            + 4 * connected_bedrooms
            + 5 * bedroom_cluster_score
            + 4 * bathroom_near_bedrooms
            + 6 * circulation_access
            - 8 * isolated_bedrooms
        )

        # Diversity pressure: avoid overcrowded zones and enforce structural differences.
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

        diversity_score = model.NewIntVar(-20, 40, "diversity_score")
        model.Add(diversity_score == 20 - 5 * overcrowding_penalty - 2 * used_zone_count)

        for blocked in blocked_layouts:
            blocked_zones: Tuple[int, ...] = blocked["zones"]
            same_flags = []
            for i, room in enumerate(ROOMS):
                is_same = model.NewBoolVar(f"same_zone_block_{len(same_flags)}_{room.name}_{rank}")
                model.Add(zone[room.name] == blocked_zones[i]).OnlyEnforceIf(is_same)
                model.Add(zone[room.name] != blocked_zones[i]).OnlyEnforceIf(is_same.Not())
                same_flags.append(is_same)

            same_zone_count = model.NewIntVar(0, len(ROOMS), f"same_zone_count_{rank}_{len(blocked_layouts)}")
            model.Add(same_zone_count == sum(same_flags))
            model.Add(same_zone_count <= len(ROOMS) - 2)

        # Final score with readable sub-scores.
        score = model.NewIntVar(-2000, 4000, "score")
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
            + weights["bathroom_bedroom"] * bathroom_near_bedrooms
            + weights["wc_day_service"] * wc_day_service_hit
            + weights["circulation"] * circulation_access
            + weights["diversity"] * diversity_score
        )

        model.Maximize(score)
        solver = cp_model.CpSolver()
        solver.parameters.max_time_in_seconds = 12
        solver.parameters.num_search_workers = 8

        status = solver.Solve(model)
        if status not in (cp_model.OPTIMAL, cp_model.FEASIBLE):
            return None

        room_zones = {spec.name: solver.Value(zone[spec.name]) for spec in ROOMS}
        room_areas = {spec.name: solver.Value(area[spec.name]) for spec in ROOMS}
        room_rectangles = {
            spec.name: {
                "x": solver.Value(x[spec.name]),
                "y": solver.Value(y[spec.name]),
                "w": solver.Value(w[spec.name]),
                "h": solver.Value(h[spec.name]),
                "cx2": solver.Value(cx2[spec.name]),
                "cy2": solver.Value(cy2[spec.name]),
            }
            for spec in ROOMS
        }

        svg_path = self._export_svg(mode, rank, room_rectangles, room_areas)

        sub_scores = {
            "compactness": solver.Value(compactness_score),
            "zoning": solver.Value(zoning_score),
            "connectivity": solver.Value(connectivity_score),
            "diversity": solver.Value(diversity_score),
        }

        metrics = {
            "isolated_bedrooms": solver.Value(isolated_bedrooms),
            "connected_bedrooms": solver.Value(connected_bedrooms),
            "kitchen_connected_to_living": solver.Value(kitchen_connected_to_living),
            "bathroom_near_bedrooms": solver.Value(bathroom_near_bedrooms),
            "connectivity_score": solver.Value(connectivity_score),
            "zoning_score": solver.Value(zoning_score),
            "compactness_score": solver.Value(compactness_score),
            "circulation_access": solver.Value(circulation_access),
            "diversity_score": solver.Value(diversity_score),
            "sub_scores": sub_scores,
        }

        return {
            "mode": mode,
            "rank": rank,
            "score": solver.Value(score),
            "areas": room_areas,
            "zones": room_zones,
            "rectangles": room_rectangles,
            "metrics": metrics,
            "svg_path": str(svg_path),
        }

    def _export_svg(
        self,
        mode: str,
        rank: int,
        room_rectangles: Dict[str, Dict[str, int]],
        room_areas: Dict[str, int],
    ) -> Path:
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

        for zone_id, z in ZONES.items():
            zx, zy = int(z["x"] * scale), int(z["y"] * scale)
            zw, zh = int(z["w"] * scale), int(z["h"] * scale)
            svg_parts.append(
                f'<rect x="{zx}" y="{zy}" width="{zw}" height="{zh}" fill="none" stroke="#cbd5e1" stroke-width="1" stroke-dasharray="4 4"/>'
            )
            svg_parts.append(
                f'<text x="{zx + 6}" y="{zy + 16}" font-family="Arial" font-size="11" fill="#64748b">Z{zone_id} ({z["tag"]})</text>'
            )

        for room_name, rect in room_rectangles.items():
            rx = rect["x"] * scale
            ry = rect["y"] * scale
            rw = rect["w"] * scale
            rh = rect["h"] * scale
            svg_parts.append(
                f'<rect x="{rx}" y="{ry}" width="{rw}" height="{rh}" '
                f'fill="{colors.get(room_name, "#cbd5e1")}" stroke="#0f172a" stroke-width="2" opacity="0.92"/>'
            )
            svg_parts.append(
                f'<text x="{rx + 6}" y="{ry + 20}" font-family="Arial" font-size="12" fill="#111827">'
                f'{room_name} ({room_areas[room_name]}m²)</text>'
            )

        svg_parts.append("</svg>")
        path = self.output_dir / f"v5_{mode}_{rank}.svg"
        path.write_text("\n".join(svg_parts), encoding="utf-8")
        return path
