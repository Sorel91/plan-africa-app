from math import ceil, floor
from pathlib import Path

from ortools.sat.python import cp_model

from models import Floorplan, RoomPlacement


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

    def generate(self):
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

            model.Add(x + w <= self.width)
            model.Add(y + h <= self.height)
            model.AddMultiplicationEquality(area, [w, h])

            room_vars.append({
                "room": room,
                "x": x,
                "y": y,
                "w": w,
                "h": h,
                "area": area,
            })

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

        model.Maximize(sum(rv["area"] for rv in room_vars))

        solver = cp_model.CpSolver()
        solver.parameters.max_time_in_seconds = 10
        status = solver.Solve(model)

        if status not in (cp_model.OPTIMAL, cp_model.FEASIBLE):
            raise RuntimeError("No feasible floorplan found")

        placements = []
        for rv in room_vars:
            room = rv["room"]
            placements.append(
                RoomPlacement(
                    name=room.name,
                    room_type=room.room_type,
                    x=solver.Value(rv["x"]) * self.grid_step,
                    y=solver.Value(rv["y"]) * self.grid_step,
                    w=solver.Value(rv["w"]) * self.grid_step,
                    h=solver.Value(rv["h"]) * self.grid_step,
                )
            )

        return Floorplan(
            width=self.width * self.grid_step,
            height=self.height * self.grid_step,
            rooms=placements,
        )


def export_floorplan_svg(floorplan, output_path, scale=40):
    colors = {
        "living_room": "#ffd166",
        "kitchen": "#8ecae6",
        "bedroom": "#bde0fe",
    }

    width_px = int(floorplan.width * scale)
    height_px = int(floorplan.height * scale)
    lines = [
        f'<svg xmlns="http://www.w3.org/2000/svg" width="{width_px}" height="{height_px}" viewBox="0 0 {width_px} {height_px}">',
        '<rect x="0" y="0" width="100%" height="100%" fill="#ffffff" stroke="#111" stroke-width="2"/>',
    ]

    for room in floorplan.rooms:
        x = room.x * scale
        y = room.y * scale
        w = room.w * scale
        h = room.h * scale
        fill = colors.get(room.room_type, "#dddddd")
        label = f"{room.name} ({room.w:.1f}x{room.h:.1f}m)"

        lines.append(
            f'<rect x="{x}" y="{y}" width="{w}" height="{h}" fill="{fill}" stroke="#333" stroke-width="1"/>'
        )
        lines.append(
            f'<text x="{x + 6}" y="{y + 18}" font-size="14" font-family="Arial" fill="#111">{label}</text>'
        )

    lines.append("</svg>")

    output_file = Path(output_path)
    output_file.parent.mkdir(parents=True, exist_ok=True)
    output_file.write_text("\n".join(lines), encoding="utf-8")
