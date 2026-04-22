from dataclasses import dataclass
from math import ceil, floor
from pathlib import Path
from typing import List, Tuple

from ortools.sat.python import cp_model

from models import Floorplan, RoomPlacement


@dataclass
class FloorplanVariant:
    index: int
    floorplan: Floorplan
    score: float


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

    def _build_model(self, variant_index, previous_signatures):
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

            # Hard compactness guard to avoid extreme rectangles such as 3.5 x 10.
            model.Add(diff <= 7)

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

        living_rooms = [rv for rv in room_vars if rv["room"].room_type == "living_room"]
        if living_rooms:
            living_area = living_rooms[0]["area"]
            for rv in room_vars:
                if rv["room"].room_type != "living_room":
                    model.Add(living_area >= rv["area"] + 4)

        bedroom_compact_bonus_terms = []
        thin_penalties = []
        for i, rv in enumerate(room_vars):
            room = rv["room"]

            min_dim = model.NewIntVar(0, self.width, f"min_dim_{i}")
            model.AddMinEquality(min_dim, [rv["w"], rv["h"]])
            thin = model.NewBoolVar(f"thin_{i}")
            model.Add(min_dim <= 3).OnlyEnforceIf(thin)
            model.Add(min_dim >= 4).OnlyEnforceIf(thin.Not())
            thin_penalties.append(thin)

            if room.room_type == "bedroom":
                compact_bedroom = model.NewBoolVar(f"compact_bedroom_{i}")
                model.Add(rv["diff"] <= 3).OnlyEnforceIf(compact_bedroom)
                model.Add(rv["diff"] >= 4).OnlyEnforceIf(compact_bedroom.Not())
                bedroom_compact_bonus_terms.append(compact_bedroom)

        total_area = sum(rv["area"] for rv in room_vars)
        total_compactness_penalty = sum(rv["diff"] for rv in room_vars)

        # Variant bias to spread solutions across the building and get distinct proposals.
        variant_bias = []
        for i, rv in enumerate(room_vars):
            if variant_index % 2 == 0:
                variant_bias.append((i + 1) * rv["x"])
            else:
                variant_bias.append((i + 1) * rv["y"])

        # Exclude exact duplicates from previous variants.
        for prev_idx, signature in enumerate(previous_signatures):
            equals = []
            for i, (px, py, pw, ph) in enumerate(signature):
                eq_x = model.NewBoolVar(f"eq_x_{prev_idx}_{i}")
                eq_y = model.NewBoolVar(f"eq_y_{prev_idx}_{i}")
                eq_w = model.NewBoolVar(f"eq_w_{prev_idx}_{i}")
                eq_h = model.NewBoolVar(f"eq_h_{prev_idx}_{i}")

                model.Add(room_vars[i]["x"] == px).OnlyEnforceIf(eq_x)
                model.Add(room_vars[i]["x"] != px).OnlyEnforceIf(eq_x.Not())
                model.Add(room_vars[i]["y"] == py).OnlyEnforceIf(eq_y)
                model.Add(room_vars[i]["y"] != py).OnlyEnforceIf(eq_y.Not())
                model.Add(room_vars[i]["w"] == pw).OnlyEnforceIf(eq_w)
                model.Add(room_vars[i]["w"] != pw).OnlyEnforceIf(eq_w.Not())
                model.Add(room_vars[i]["h"] == ph).OnlyEnforceIf(eq_h)
                model.Add(room_vars[i]["h"] != ph).OnlyEnforceIf(eq_h.Not())

                equals.extend([eq_x, eq_y, eq_w, eq_h])

            model.AddBoolOr([flag.Not() for flag in equals])

        objective = (
            25 * total_area
            - 6 * total_compactness_penalty
            - 20 * sum(thin_penalties)
            + 5 * sum(bedroom_compact_bonus_terms)
            + sum(variant_bias)
        )
        model.Maximize(objective)

        return model, room_vars

    def generate_variants(self, count=5):
        variants: List[FloorplanVariant] = []
        previous_signatures: List[List[Tuple[int, int, int, int]]] = []

        for variant_index in range(count):
            model, room_vars = self._build_model(variant_index, previous_signatures)
            solver = cp_model.CpSolver()
            solver.parameters.max_time_in_seconds = 10
            status = solver.Solve(model)

            if status not in (cp_model.OPTIMAL, cp_model.FEASIBLE):
                break

            placements = []
            signature = []
            area_score = 0
            compactness_penalty = 0
            thin_count = 0
            bedroom_bonus = 0

            for rv in room_vars:
                x = solver.Value(rv["x"])
                y = solver.Value(rv["y"])
                w = solver.Value(rv["w"])
                h = solver.Value(rv["h"])
                area = solver.Value(rv["area"])
                diff = solver.Value(rv["diff"])

                area_score += area
                compactness_penalty += diff
                if min(w, h) <= 3:
                    thin_count += 1
                if rv["room"].room_type == "bedroom" and diff <= 3:
                    bedroom_bonus += 1

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

            score = (
                25 * area_score
                - 6 * compactness_penalty
                - 20 * thin_count
                + 5 * bedroom_bonus
            )

            variants.append(
                FloorplanVariant(
                    index=variant_index + 1,
                    floorplan=Floorplan(
                        width=self.width * self.grid_step,
                        height=self.height * self.grid_step,
                        rooms=placements,
                    ),
                    score=score,
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

    header_height = 40
    width_px = int(floorplan.width * scale)
    height_px = int(floorplan.height * scale) + header_height

    lines = [
        f'<svg xmlns="http://www.w3.org/2000/svg" width="{width_px}" height="{height_px}" viewBox="0 0 {width_px} {height_px}">',
        '<rect x="0" y="0" width="100%" height="100%" fill="#ffffff" stroke="#111" stroke-width="1"/>',
    ]

    if title:
        lines.append(
            f'<text x="10" y="26" font-size="18" font-family="Arial" font-weight="bold" fill="#111">{title}</text>'
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
