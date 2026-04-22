from ortools.sat.python import cp_model
from models import RoomSpec, RoomPlacement, Floorplan

class FloorplanGenerator:
    def __init__(self, width, height, rooms):
        self.width = int(width * 2)   # grille de 0.5 m
        self.height = int(height * 2)
        self.rooms = rooms

    def generate(self):
        model = cp_model.CpModel()
        vars = []

        for i, room in enumerate(self.rooms):
            x = model.NewIntVar(0, self.width, f"x{i}")
            y = model.NewIntVar(0, self.height, f"y{i}")
            w = model.NewIntVar(2, self.width, f"w{i}")
            h = model.NewIntVar(2, self.height, f"h{i}")

            model.Add(x + w <= self.width)
            model.Add(y + h <= self.height)

            vars.append((room, x, y, w, h))

        # séparation simplifiée entre pièces
        for i in range(len(vars)):
            for j in range(i + 1, len(vars)):
                _, x1, y1, w1, h1 = vars[i]
                _, x2, y2, w2, h2 = vars[j]

                left = model.NewBoolVar(f"left_{i}_{j}")
                right = model.NewBoolVar(f"right_{i}_{j}")
                above = model.NewBoolVar(f"above_{i}_{j}")
                below = model.NewBoolVar(f"below_{i}_{j}")

                model.Add(x1 + w1 <= x2).OnlyEnforceIf(left)
                model.Add(x2 + w2 <= x1).OnlyEnforceIf(right)
                model.Add(y1 + h1 <= y2).OnlyEnforceIf(above)
                model.Add(y2 + h2 <= y1).OnlyEnforceIf(below)

                model.AddBoolOr([left, right, above, below])

        model.Maximize(1)

        solver = cp_model.CpSolver()
        status = solver.Solve(model)

        if status not in (cp_model.OPTIMAL, cp_model.FEASIBLE):
            raise RuntimeError("No feasible floorplan found")

        placements = []
        for room, x, y, w, h in vars:
            placements.append(
                RoomPlacement(
                    name=room.name,
                    room_type=room.room_type,
                    x=solver.Value(x) / 2,
                    y=solver.Value(y) / 2,
                    w=solver.Value(w) / 2,
                    h=solver.Value(h) / 2,
                )
            )

        return Floorplan(
            width=self.width / 2,
            height=self.height / 2,
            rooms=placements,
        )
