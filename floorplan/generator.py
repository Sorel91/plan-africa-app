from dataclasses import dataclass
from math import ceil, floor
from pathlib import Path
from typing import Dict, List, Tuple

from ortools.sat.python import cp_model

from models import Floorplan, RoomPlacement


@dataclass
class FloorplanVariant:
    index: int
    mode: str
    floorplan: Floorplan
    score: float
    metrics: Dict[str, int]


class FloorplanGenerator:
    def __init__(self, width, height, rooms, grid_step=0.5):
        self.grid_step = grid_step
        self.cell_area = grid_step * grid_step
        self.width = int(width / grid_step)
        self.height = int(height / grid_step)
        self.rooms = rooms

    def _area_to_cells(self, area_m2, mode):
        ratio = area_m2 / self.cell_area
        return int(ceil(ratio) if mode == "min" else floor(ratio))

    def _mode_for_index(self, variant_index):
        modes = [
            {
                "name": "A-grand-salon-horizontal",
                "living_horizontal": True,
                "living_on_top": True,
                "weights": {"kitchen_near": 7, "bed_cluster": 5, "bed_living_sep": 4, "compact": 9},
            },
            {
                "name": "B-grand-salon-vertical",
                "living_vertical": True,
                "living_on_left": True,
                "weights": {"kitchen_near": 8, "bed_cluster": 6, "bed_living_sep": 5, "compact": 9},
            },
            {
                "name": "C-chambres-regroupees",
                "bedrooms_same_half": "top",
                "weights": {"kitchen_near": 6, "bed_cluster": 10, "bed_living_sep": 5, "compact": 8},
            },
            {
                "name": "D-cuisine-compacte",
                "kitchen_compact": True,
                "weights": {"kitchen_near": 12, "bed_cluster": 5, "bed_living_sep": 4, "compact": 8},
            },
            {
                "name": "E-zonage-jour-nuit",
                "day_night_split": True,
                "weights": {"kitchen_near": 8, "bed_cluster": 8, "bed_living_sep": 9, "compact": 7},
            },
        ]
        return modes[variant_index % len(modes)]

    def _build_model(self, variant_index, mode, previous_signatures):
        model = cp_model.CpModel()
        room_vars = []

        for i, room in enumerate(self.rooms):
            min_area_cells = self._area_to_cells(room.min_area, "min")
            max_area_cells = self._area_to_cells(room.max_area, "max")

            min_side = 2
            if room.room_type == "living_room":
                min_side = 6
            elif room.room_type in ("kitchen", "bedroom"):
                min_side = 4

            x = model.NewIntVar(0, self.width - min_side, f"x{i}")
            y = model.NewIntVar(0, self.height - min_side, f"y{i}")
            w = model.NewIntVar(min_side, self.width, f"w{i}")
            h = model.NewIntVar(min_side, self.height, f"h{i}")
            area = model.NewIntVar(min_area_cells, max_area_cells, f"area{i}")
            diff = model.NewIntVar(0, self.width, f"diff{i}")

            model.Add(x + w <= self.width)
            model.Add(y + h <= self.height)
            model.AddMultiplicationEquality(area, [w, h])
            model.AddAbsEquality(diff, w - h)
            model.Add(diff <= 6)

            room_vars.append(
                {"room": room, "x": x, "y": y, "w": w, "h": h, "area": area, "diff": diff}
            )

        for i in range(len(room_vars)):
            for j in range(i + 1, len(room_vars)):
                r1 = room_vars[i]
                r2 = room_vars[j]

                left = model.NewBoolVar(f"left_{i}_{j}")
                right = model.NewBoolVar(f"right_{i}_{j}")
                above = model.NewBoolVar(f"above_{i}_{j}")
                below = model.NewBoolVar(f"below_{i}_{j}")

                model.Add(r1["x"] + r1["w"] <= r2["x"]).OnlyEnforceIf(left)
                model.Add(r2["x"] + r2["w"] <= r1["x"]).OnlyEnforceIf(right)
                model.Add(r1["y"] + r1["h"] <= r2["y"]).OnlyEnforceIf(above)
                model.Add(r2["y"] + r2["h"] <= r1["y"]).OnlyEnforceIf(below)
                model.AddBoolOr([left, right, above, below])

        living = next(rv for rv in room_vars if rv["room"].room_type == "living_room")
        kitchen = next(rv for rv in room_vars if rv["room"].room_type == "kitchen")
        bedrooms = [rv for rv in room_vars if rv["room"].room_type == "bedroom"]

        for rv in room_vars:
            if rv["room"].room_type != "living_room":
                model.Add(living["area"] >= rv["area"] + 4)

        if mode.get("living_horizontal"):
            model.Add(living["w"] >= living["h"] + 2)
        if mode.get("living_vertical"):
            model.Add(living["h"] >= living["w"] + 2)
        if mode.get("living_on_top"):
            model.Add(living["y"] + living["h"] <= self.height // 2 + 2)
        if mode.get("living_on_left"):
            model.Add(living["x"] + living["w"] <= self.width // 2 + 2)

        if mode.get("bedrooms_same_half") == "top":
            for bed in bedrooms:
                model.Add(bed["y"] + bed["h"] <= self.height // 2 + 3)

        if mode.get("day_night_split"):
            for bed in bedrooms:
                model.Add(bed["x"] >= self.width // 2 - 2)
            model.Add(living["x"] + living["w"] <= self.width // 2 + 2)

        if mode.get("kitchen_compact"):
            model.Add(kitchen["diff"] <= 2)

        bedroom_compact_bonus_terms = []
        thin_penalties = []
        bedroom_cluster_terms = []

        for i, rv in enumerate(room_vars):
            min_dim = model.NewIntVar(0, self.width, f"min_dim_{i}")
            model.AddMinEquality(min_dim, [rv["w"], rv["h"]])
            thin = model.NewBoolVar(f"thin_{i}")
            model.Add(min_dim <= 3).OnlyEnforceIf(thin)
            model.Add(min_dim >= 4).OnlyEnforceIf(thin.Not())
            thin_penalties.append(thin)

            if rv["room"].room_type == "bedroom":
                compact_bedroom = model.NewBoolVar(f"compact_bedroom_{i}")
                model.Add(rv["diff"] <= 2).OnlyEnforceIf(compact_bedroom)
                model.Add(rv["diff"] >= 3).OnlyEnforceIf(compact_bedroom.Not())
                bedroom_compact_bonus_terms.append(compact_bedroom)

        bed_pair_distances = []
        for i in range(len(bedrooms)):
            for j in range(i + 1, len(bedrooms)):
                dx = model.NewIntVar(0, self.width, f"bed_dx_{i}_{j}")
                dy = model.NewIntVar(0, self.height, f"bed_dy_{i}_{j}")
                model.AddAbsEquality(dx, bedrooms[i]["x"] - bedrooms[j]["x"])
                model.AddAbsEquality(dy, bedrooms[i]["y"] - bedrooms[j]["y"])
                dist = model.NewIntVar(0, self.width + self.height, f"bed_dist_{i}_{j}")
                model.Add(dist == dx + dy)
                bed_pair_distances.append(dist)

                close = model.NewBoolVar(f"bed_close_{i}_{j}")
                model.Add(dist <= 6).OnlyEnforceIf(close)
                model.Add(dist >= 7).OnlyEnforceIf(close.Not())
                bedroom_cluster_terms.append(close)

        kitchen_living_dx = model.NewIntVar(0, self.width, "kitchen_living_dx")
        kitchen_living_dy = model.NewIntVar(0, self.height, "kitchen_living_dy")
        model.AddAbsEquality(kitchen_living_dx, kitchen["x"] - living["x"])
        model.AddAbsEquality(kitchen_living_dy, kitchen["y"] - living["y"])
        kitchen_living_distance = model.NewIntVar(0, self.width + self.height, "kitchen_living_distance")
        model.Add(kitchen_living_distance == kitchen_living_dx + kitchen_living_dy)

        bedroom_living_distances = []
        for i, bed in enumerate(bedrooms):
            bdx = model.NewIntVar(0, self.width, f"bed_living_dx_{i}")
            bdy = model.NewIntVar(0, self.height, f"bed_living_dy_{i}")
            model.AddAbsEquality(bdx, bed["x"] - living["x"])
            model.AddAbsEquality(bdy, bed["y"] - living["y"])
            bdist = model.NewIntVar(0, self.width + self.height, f"bed_living_dist_{i}")
            model.Add(bdist == bdx + bdy)
            bedroom_living_distances.append(bdist)

        total_area = sum(rv["area"] for rv in room_vars)
        compactness_penalty = sum(rv["diff"] for rv in room_vars)
        bedroom_cluster_distance = sum(bed_pair_distances) if bed_pair_distances else 0
        bedroom_living_separation = sum(bedroom_living_distances)

        weights = mode["weights"]
        objective = (
            22 * total_area
            - weights["compact"] * compactness_penalty
            - 24 * sum(thin_penalties)
            + 7 * sum(bedroom_compact_bonus_terms)
            - weights["kitchen_near"] * kitchen_living_distance
            - weights["bed_cluster"] * bedroom_cluster_distance
            + weights["bed_living_sep"] * bedroom_living_separation
            + 4 * sum(bedroom_cluster_terms)
            + (variant_index + 1) * (living["x"] + 2 * living["y"])
        )
        model.Maximize(objective)

        for prev_idx, signature in enumerate(previous_signatures):
            diffs = []
            for i, (px, py, pw, ph) in enumerate(signature):
                for axis, value in (
                    ("x", px),
                    ("y", py),
                    ("w", pw),
                    ("h", ph),
                ):
                    d = model.NewIntVar(0, max(self.width, self.height), f"d_{prev_idx}_{i}_{axis}")
                    model.AddAbsEquality(d, room_vars[i][axis] - value)
                    diffs.append(d)

            total_diff = model.NewIntVar(0, 200, f"total_diff_{prev_idx}")
            model.Add(total_diff == sum(diffs))
            model.Add(total_diff >= 8)

        metrics = {
            "kitchen_living_distance": kitchen_living_distance,
            "bedroom_cluster_distance": bedroom_cluster_distance,
            "compactness_penalty": compactness_penalty,
            "bedroom_living_separation": bedroom_living_separation,
            "total_area": total_area,
        }

        return model, room_vars, metrics

    def generate_variants(self, count=5):
        variants: List[FloorplanVariant] = []
        previous_signatures: List[List[Tuple[int, int, int, int]]] = []

        for variant_index in range(count):
            mode = self._mode_for_index(variant_index)
            model, room_vars, metrics = self._build_model(variant_index, mode, previous_signatures)
            solver = cp_model.CpSolver()
            solver.parameters.max_time_in_seconds = 10
            status = solver.Solve(model)

            if status not in (cp_model.OPTIMAL, cp_model.FEASIBLE):
                continue

            placements = []
            signature = []
            for rv in room_vars:
                x = solver.Value(rv["x"])
                y = solver.Value(rv["y"])
                w = solver.Value(rv["w"])
                h = solver.Value(rv["h"])
                signature.append((x, y, w, h))
                placements.append(
                    RoomPlacement(
                        name=rv["room"].name,
                        room_type=rv["room"].room_type,
                        x=x * self.grid_step,
                        y=y * self.grid_step,
                        w=w * self.grid_step,
                        h=h * self.grid_step,
                    )
                )

            score = solver.ObjectiveValue()
            metric_values = {}
            for key, expr in metrics.items():
                metric_values[key] = solver.Value(expr) if hasattr(expr, "Index") else int(expr)

            variants.append(
                FloorplanVariant(
                    index=variant_index + 1,
                    mode=mode["name"],
                    floorplan=Floorplan(
                        width=self.width * self.grid_step,
                        height=self.height * self.grid_step,
                        rooms=placements,
                    ),
                    score=score,
                    metrics=metric_values,
                )
            )
            previous_signatures.append(signature)

        if not variants:
            raise RuntimeError("No feasible floorplan variant found")

        return variants


def export_floorplan_svg(floorplan, output_path, title=None, scale=52):
    colors = {
        "living_room": "#ffd166",
        "kitchen": "#8ecae6",
        "bedroom": "#bde0fe",
    }

    header_height = 46
    width_px = int(floorplan.width * scale)
    height_px = int(floorplan.height * scale) + header_height

    lines = [
        f'<svg xmlns="http://www.w3.org/2000/svg" width="{width_px}" height="{height_px}" viewBox="0 0 {width_px} {height_px}">',
        '<rect x="0" y="0" width="100%" height="100%" fill="#ffffff" stroke="#111" stroke-width="1"/>',
    ]

    if title:
        lines.append(
            f'<text x="10" y="30" font-size="18" font-family="Arial" font-weight="bold" fill="#111">{title}</text>'
        )

    for room in floorplan.rooms:
        x = room.x * scale
        y = room.y * scale + header_height
        w = room.w * scale
        h = room.h * scale
        fill = colors.get(room.room_type, "#dddddd")
        area = room.w * room.h

        lines.append(
            f'<rect x="{x:.1f}" y="{y:.1f}" width="{w:.1f}" height="{h:.1f}" fill="{fill}" stroke="#333" stroke-width="1.5"/>'
        )
        lines.append(
            f'<text x="{x + 8:.1f}" y="{y + 20:.1f}" font-size="14" font-family="Arial" fill="#111">{room.name}</text>'
        )
        lines.append(
            f'<text x="{x + 8:.1f}" y="{y + 38:.1f}" font-size="12" font-family="Arial" fill="#333">{area:.1f} m² | {room.w:.1f} x {room.h:.1f} m</text>'
        )

    lines.append("</svg>")

    output_file = Path(output_path)
    output_file.parent.mkdir(parents=True, exist_ok=True)
    output_file.write_text("\n".join(lines), encoding="utf-8")
