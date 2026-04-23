from __future__ import annotations

from pathlib import Path
from typing import Dict, List, Tuple

from ortools.sat.python import cp_model

try:
    from floorplan.models import Floorplan, FloorplanVariant, RoomPlacement, RoomSpec
except ModuleNotFoundError:
    from models import Floorplan, FloorplanVariant, RoomPlacement, RoomSpec


ROOMS: List[RoomSpec] = [
    RoomSpec("living", "living", 20, 46, "day", True, ("kitchen", "hall"), ()),
    RoomSpec("kitchen", "kitchen", 8, 18, "day", True, ("living",), ("bedroom_1", "bedroom_2", "bedroom_3")),
    RoomSpec("hall", "hall", 4, 8, "service", True, ("living", "bedroom_1", "bedroom_2", "bedroom_3"), ()),
    RoomSpec("bedroom_1", "bedroom", 9, 18, "night", True, ("hall", "living", "bathroom"), ("kitchen",)),
    RoomSpec("bedroom_2", "bedroom", 9, 18, "night", True, ("hall", "living", "bathroom"), ("kitchen",)),
    RoomSpec("bedroom_3", "bedroom", 9, 16, "night", True, ("hall", "living", "bathroom"), ("kitchen",)),
    RoomSpec("bathroom", "bathroom", 4, 10, "service", True, ("bedroom_1", "bedroom_2", "bedroom_3", "hall"), ()),
    RoomSpec("wc", "wc", 2, 5, "service", False, ("living", "hall"), ()),
]

ZONES: Dict[int, Dict[str, object]] = {
    0: {"x": 0, "y": 0, "w": 7, "h": 4, "tag": "day"},
    1: {"x": 7, "y": 0, "w": 5, "h": 4, "tag": "day"},
    2: {"x": 0, "y": 4, "w": 4, "h": 4, "tag": "service"},
    3: {"x": 4, "y": 4, "w": 8, "h": 4, "tag": "night"},
    4: {"x": 0, "y": 8, "w": 6, "h": 4, "tag": "night"},
    5: {"x": 6, "y": 8, "w": 6, "h": 4, "tag": "service"},
}

ZONE_NEIGHBORS: Dict[int, List[int]] = {
    0: [1, 2, 3],
    1: [0, 3],
    2: [0, 3, 4],
    3: [0, 1, 2, 4, 5],
    4: [2, 3, 5],
    5: [3, 4],
}

MODE_WEIGHTS = {
    "balanced": {
        "fill": 22,
        "empty_area": -60,
        "compactness": 4,
        "zoning": 4,
        "living_dominance": 4,
        "kitchen_living": 16,
        "kitchen_isolation_malus": -24,
        "independent_bedrooms": 18,
        "bedroom_cluster": 4,
        "isolated_bedrooms": -18,
        "bathroom_bedroom": 9,
        "wc_day_service": 4,
        "circulation": 14,
        "diversity": 6,
        "hall_bonus": 10,
        "entry_bonus": 12,
    },
    "strict_connectivity": {
        "fill": 20,
        "empty_area": -55,
        "compactness": 3,
        "zoning": 3,
        "living_dominance": 4,
        "kitchen_living": 26,
        "kitchen_isolation_malus": -40,
        "independent_bedrooms": 22,
        "bedroom_cluster": 3,
        "isolated_bedrooms": -24,
        "bathroom_bedroom": 10,
        "wc_day_service": 4,
        "circulation": 18,
        "diversity": 5,
        "hall_bonus": 14,
        "entry_bonus": 14,
    },
    "zoning_first": {
        "fill": 21,
        "empty_area": -58,
        "compactness": 4,
        "zoning": 10,
        "living_dominance": 5,
        "kitchen_living": 12,
        "kitchen_isolation_malus": -20,
        "independent_bedrooms": 18,
        "bedroom_cluster": 3,
        "isolated_bedrooms": -18,
        "bathroom_bedroom": 11,
        "wc_day_service": 5,
        "circulation": 14,
        "diversity": 5,
        "hall_bonus": 12,
        "entry_bonus": 13,
    },
}


class FloorplanGeneratorV6:
    def __init__(self, output_dir: str = "floorplan/out") -> None:
        self.output_dir = Path(output_dir)
        self.output_dir.mkdir(parents=True, exist_ok=True)

    def generate_variants(self, variants_per_mode: int = 2) -> List[FloorplanVariant]:
        results: List[FloorplanVariant] = []
        for mode in MODE_WEIGHTS:
            blocked_layouts: List[Dict[str, object]] = []
            for rank in range(1, variants_per_mode + 1):
                variant = self._solve_one(mode=mode, blocked_layouts=blocked_layouts, rank=rank)
                if variant is None:
                    break
                blocked_layouts.append(
                    {
                        "zones": tuple(variant.metrics["zones"][room.name] for room in ROOMS),
                        "centers": tuple(variant.metrics["centers"][room.name] for room in ROOMS),
                    }
                )
                results.append(variant)
        return results

    def _solve_one(self, mode: str, blocked_layouts: List[Dict[str, object]], rank: int) -> FloorplanVariant | None:
        model = cp_model.CpModel()
        weights = MODE_WEIGHTS[mode]

        width_limit = 12
        height_limit = 12
        building_area = width_limit * height_limit

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
            area[room_name] = model.NewIntVar(int(spec.min_area), int(spec.max_area), f"area_{room_name}")
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

        total_area = model.NewIntVar(63, building_area, "total_area")
        model.Add(total_area == sum(area.values()))
        empty_area = model.NewIntVar(0, building_area, "empty_area")
        model.Add(empty_area == building_area - total_area)
        model.Add(empty_area <= 12)
        model.Add(total_area >= building_area - 12)

        model.Add(area["living"] >= area["kitchen"] + 6)
        model.Add(area["living"] >= area["hall"] + 8)
        for bedroom in ["bedroom_1", "bedroom_2", "bedroom_3"]:
            model.Add(area["living"] >= area[bedroom] + 2)

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

        zone_used: Dict[int, cp_model.BoolVar] = {}
        for z in ZONES:
            used = model.NewBoolVar(f"zone_used_{z}")
            zone_used[z] = used
            model.AddBoolOr([in_zone[(r.name, z)] for r in ROOMS]).OnlyEnforceIf(used)
            model.AddBoolAnd([in_zone[(r.name, z)].Not() for r in ROOMS]).OnlyEnforceIf(used.Not())

        used_zone_count = model.NewIntVar(1, len(ZONES), "used_zone_count")
        model.Add(used_zone_count == sum(zone_used.values()))
        compactness_score = model.NewIntVar(0, building_area + len(ZONES), "compactness_score")
        model.Add(compactness_score == total_area + (len(ZONES) - used_zone_count) * 4)

        kitchen_living_adj = pair_var(adjacency, "kitchen", "living")
        kitchen_living_prox = pair_var(proximity, "kitchen", "living")
        kitchen_connected_to_living = model.NewBoolVar("kitchen_connected_to_living")
        model.AddMaxEquality(kitchen_connected_to_living, [kitchen_living_adj, kitchen_living_prox])

        hall_living_adj = pair_var(adjacency, "hall", "living")
        hall_connected_to_living = model.NewBoolVar("hall_connected_to_living")
        model.AddMaxEquality(hall_connected_to_living, [hall_living_adj, pair_var(proximity, "hall", "living")])

        entry_into_living = model.NewBoolVar("entry_into_living")
        entry_into_hall = model.NewBoolVar("entry_into_hall")
        model.Add(y["living"] == 0).OnlyEnforceIf(entry_into_living)
        model.Add(y["living"] >= 1).OnlyEnforceIf(entry_into_living.Not())
        model.Add(y["hall"] == 0).OnlyEnforceIf(entry_into_hall)
        model.Add(y["hall"] >= 1).OnlyEnforceIf(entry_into_hall.Not())

        entry_access_ok = model.NewBoolVar("entry_access_ok")
        entry_via_hall = model.NewBoolVar("entry_via_hall")
        model.AddBoolAnd([entry_into_hall, hall_connected_to_living]).OnlyEnforceIf(entry_via_hall)
        model.AddBoolOr([entry_into_hall.Not(), hall_connected_to_living.Not()]).OnlyEnforceIf(entry_via_hall.Not())
        model.AddMaxEquality(entry_access_ok, [entry_into_living, entry_via_hall])
        model.Add(entry_access_ok == 1)

        kitchen_isolated = model.NewIntVar(0, 1, "kitchen_isolated")
        model.Add(kitchen_isolated == 1 - kitchen_connected_to_living)

        if mode == "strict_connectivity":
            model.Add(kitchen_connected_to_living == 1)
            model.Add(hall_connected_to_living == 1)

        bedroom_names = ["bedroom_1", "bedroom_2", "bedroom_3"]
        independent_bedroom_vars: Dict[str, cp_model.BoolVar] = {}
        isolated_bedroom_vars: Dict[str, cp_model.IntVar] = {}

        for bedroom in bedroom_names:
            access_living = pair_var(adjacency, bedroom, "living")
            access_hall = pair_var(adjacency, bedroom, "hall")
            independent_access = model.NewBoolVar(f"{bedroom}_independent_access")
            model.AddMaxEquality(independent_access, [access_living, access_hall])
            independent_bedroom_vars[bedroom] = independent_access

            isolated = model.NewIntVar(0, 1, f"{bedroom}_isolated")
            model.Add(isolated == 1 - independent_access)
            isolated_bedroom_vars[bedroom] = isolated

            if mode == "strict_connectivity":
                model.Add(independent_access == 1)

        independent_bedrooms = model.NewIntVar(0, len(bedroom_names), "independent_bedrooms")
        model.Add(independent_bedrooms == sum(independent_bedroom_vars.values()))

        isolated_bedrooms = model.NewIntVar(0, len(bedroom_names), "isolated_bedrooms")
        model.Add(isolated_bedrooms == sum(isolated_bedroom_vars.values()))

        bedroom_hall_adjacency = []
        for bedroom in bedroom_names:
            bedroom_hall_adjacency.append(pair_var(adjacency, bedroom, "hall"))

        bedroom_cluster_score = model.NewIntVar(0, len(bedroom_hall_adjacency), "bedroom_cluster_score")
        model.Add(bedroom_cluster_score == sum(bedroom_hall_adjacency))

        bathroom_near_bedrooms_terms = [pair_var(adjacency, "bathroom", b) for b in bedroom_names]
        bathroom_near_bedrooms = model.NewIntVar(0, len(bedroom_names), "bathroom_near_bedrooms")
        model.Add(bathroom_near_bedrooms == sum(bathroom_near_bedrooms_terms))

        wc_day_service_hit = model.NewBoolVar("wc_day_service_hit")
        wc_day_service_terms = [in_zone[("wc", z)] for z, info in ZONES.items() if info["tag"] in {"day", "service"}]
        model.AddBoolOr(wc_day_service_terms).OnlyEnforceIf(wc_day_service_hit)
        model.AddBoolAnd([b.Not() for b in wc_day_service_terms]).OnlyEnforceIf(wc_day_service_hit.Not())

        circulation_terms = []
        for spec in ROOMS:
            if spec.name in {"living", "hall"} or not spec.important_for_circulation:
                continue

            direct = pair_var(adjacency, spec.name, "living")
            via_hall = model.NewBoolVar(f"hop_{spec.name}_via_hall")
            model.AddBoolAnd([pair_var(adjacency, spec.name, "hall"), hall_connected_to_living]).OnlyEnforceIf(via_hall)
            model.AddBoolOr([pair_var(adjacency, spec.name, "hall").Not(), hall_connected_to_living.Not()]).OnlyEnforceIf(via_hall.Not())

            access = model.NewBoolVar(f"access_to_living_{spec.name}")
            model.AddMaxEquality(access, [direct, via_hall])
            circulation_terms.append(access)

        circulation_access = model.NewIntVar(0, len(circulation_terms) + 2, "circulation_access")
        model.Add(circulation_access == sum(circulation_terms) + hall_connected_to_living + entry_access_ok)

        connectivity_score = model.NewIntVar(0, 320, "connectivity_score")
        model.Add(
            connectivity_score
            == 12 * kitchen_connected_to_living
            + 8 * hall_connected_to_living
            + 8 * independent_bedrooms
            + 3 * bedroom_cluster_score
            + 4 * bathroom_near_bedrooms
            + 6 * circulation_access
            + 8 * entry_access_ok
            - 10 * isolated_bedrooms
        )

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

        score = model.NewIntVar(-20000, 20000, "score")
        model.Add(
            score
            == weights["fill"] * total_area
            + weights["empty_area"] * empty_area
            + weights["compactness"] * compactness_score
            + weights["zoning"] * zoning_score
            + weights["living_dominance"] * area["living"]
            + weights["hall_bonus"] * hall_connected_to_living
            + weights["entry_bonus"] * entry_access_ok
            + weights["kitchen_living"] * kitchen_living_adj
            + weights["kitchen_isolation_malus"] * kitchen_isolated
            + weights["independent_bedrooms"] * independent_bedrooms
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

        placements = [
            RoomPlacement(
                name=spec.name,
                room_type=spec.room_type,
                x=room_rectangles[spec.name]["x"],
                y=room_rectangles[spec.name]["y"],
                w=room_rectangles[spec.name]["w"],
                h=room_rectangles[spec.name]["h"],
                zone_id=room_zones[spec.name],
            )
            for spec in ROOMS
        ]

        svg_path = self._export_svg(mode, rank, room_rectangles, room_areas)

        sub_scores = {
            "fill": solver.Value(total_area),
            "compactness": solver.Value(compactness_score),
            "zoning": solver.Value(zoning_score),
            "connectivity": solver.Value(connectivity_score),
            "diversity": solver.Value(diversity_score),
        }

        metrics = {
            "occupied_area": solver.Value(total_area),
            "empty_area": solver.Value(empty_area),
            "entry_access_ok": solver.Value(entry_access_ok),
            "entry_into_living": solver.Value(entry_into_living),
            "entry_into_hall": solver.Value(entry_into_hall),
            "isolated_bedrooms": solver.Value(isolated_bedrooms),
            "independent_bedrooms": solver.Value(independent_bedrooms),
            "hall_connected_to_living": solver.Value(hall_connected_to_living),
            "kitchen_connected_to_living": solver.Value(kitchen_connected_to_living),
            "bathroom_near_bedrooms": solver.Value(bathroom_near_bedrooms),
            "connectivity_score": solver.Value(connectivity_score),
            "zoning_score": solver.Value(zoning_score),
            "compactness_score": solver.Value(compactness_score),
            "circulation_access": solver.Value(circulation_access),
            "diversity_score": solver.Value(diversity_score),
            "sub_scores": sub_scores,
            "areas": room_areas,
            "zones": room_zones,
            "centers": {spec.name: (room_rectangles[spec.name]["cx2"], room_rectangles[spec.name]["cy2"]) for spec in ROOMS},
            "rectangles": room_rectangles,
            "rank": rank,
        }

        floorplan = Floorplan(width=width_limit, height=height_limit, rooms=placements)
        return FloorplanVariant(mode=mode, score=solver.Value(score), floorplan=floorplan, metrics=metrics, svg_path=str(svg_path))

    def _export_svg(
        self,
        mode: str,
        rank: int,
        room_rectangles: Dict[str, Dict[str, int]],
        room_areas: Dict[str, int],
    ) -> Path:
        scale = 45
        margin = 16
        header_height = 52
        svg_width = 12 * scale + margin * 2
        svg_height = 12 * scale + header_height + margin * 2

        colors = {
            "living": "#fca5a5",
            "kitchen": "#fdba74",
            "hall": "#e9d5ff",
            "bedroom_1": "#86efac",
            "bedroom_2": "#4ade80",
            "bedroom_3": "#22c55e",
            "bathroom": "#93c5fd",
            "wc": "#60a5fa",
        }

        zone_stroke = "#cbd5e1"
        zone_label = "#94a3b8"
        room_stroke = "#1f2937"
        text_color = "#111827"
        subtitle_color = "#475569"

        svg_parts = [
            f'<svg xmlns="http://www.w3.org/2000/svg" width="{svg_width}" height="{svg_height}" viewBox="0 0 {svg_width} {svg_height}">',
            '<rect x="0" y="0" width="100%" height="100%" fill="#f8fafc"/>',
            f'<rect x="{margin}" y="{margin + header_height}" width="{12 * scale}" height="{12 * scale}" rx="4" fill="#ffffff" stroke="#cbd5e1" stroke-width="1.5"/>',
            f'<text x="{margin}" y="{margin + 18}" font-family="Arial" font-size="18" font-weight="bold" fill="#0f172a">Floorplan V6</text>',
            f'<text x="{margin + 126}" y="{margin + 18}" font-family="Arial" font-size="14" fill="#475569">{mode} #{rank}</text>',
        ]

        zone_offset_y = margin + header_height
        zone_offset_x = margin

        for zone_id, z in ZONES.items():
            zx, zy = int(z["x"] * scale) + zone_offset_x, int(z["y"] * scale) + zone_offset_y
            zw, zh = int(z["w"] * scale), int(z["h"] * scale)
            svg_parts.append(
                f'<rect x="{zx}" y="{zy}" width="{zw}" height="{zh}" fill="none" stroke="{zone_stroke}" stroke-width="1" stroke-dasharray="6 5" opacity="0.45"/>'
            )
            svg_parts.append(
                f'<text x="{zx + 8}" y="{zy + 18}" font-family="Arial" font-size="11" fill="{zone_label}" opacity="0.6">Z{zone_id} ({z["tag"]})</text>'
            )

        for room_name, rect in room_rectangles.items():
            rx = rect["x"] * scale + zone_offset_x
            ry = rect["y"] * scale + zone_offset_y
            rw = rect["w"] * scale
            rh = rect["h"] * scale
            fill = colors.get(room_name, "#cbd5e1")

            svg_parts.append(
                f'<rect x="{rx}" y="{ry}" width="{rw}" height="{rh}" fill="{fill}" stroke="{room_stroke}" stroke-width="2.5" opacity="1"/>'
            )

            label = f'{room_name} ({room_areas[room_name]}m²)'
            font_size = 13 if rw >= 100 and rh >= 55 else 11
            badge_width = min(max(len(label) * 7 + 14, 72), max(int(rw) - 12, 72))
            badge_height = 24
            badge_x = rx + 6
            badge_y = ry + 6

            svg_parts.append(
                f'<rect x="{badge_x}" y="{badge_y}" width="{badge_width}" height="{badge_height}" rx="4" fill="#ffffff" fill-opacity="0.82" stroke="none"/>'
            )
            svg_parts.append(
                f'<text x="{badge_x + 8}" y="{badge_y + 16}" font-family="Arial" font-size="{font_size}" font-weight="600" fill="{text_color}">{label}</text>'
            )

            dims = f'{rect["w"]} x {rect["h"]}'
            if rh >= 70:
                svg_parts.append(
                    f'<text x="{badge_x + 8}" y="{badge_y + 32}" font-family="Arial" font-size="10" fill="{subtitle_color}">{dims}</text>'
                )

        svg_parts.append("</svg>")
        path = self.output_dir / f"v6_{mode}_{rank}.svg"
        path.write_text("\n".join(svg_parts), encoding="utf-8")
        return path
