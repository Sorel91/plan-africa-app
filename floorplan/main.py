from generator import FloorplanGenerator, export_floorplan_svg
from models import RoomSpec

rooms = [
    RoomSpec("Salon", "living_room", 25, 35),
    RoomSpec("Cuisine", "kitchen", 10, 15),
    RoomSpec("Chambre 1", "bedroom", 10, 15),
    RoomSpec("Chambre 2", "bedroom", 10, 15),
]

generator = FloorplanGenerator(10, 10, rooms, grid_step=0.5)
plan = generator.generate()

print(f"Building: {plan.width}m x {plan.height}m")
for room in plan.rooms:
    print(
        f"{room.name} | type={room.room_type} | "
        f"x={room.x:.1f}, y={room.y:.1f}, w={room.w:.1f}, h={room.h:.1f}, area={room.w * room.h:.1f}m²"
    )

output_svg = "floorplan/output.svg"
export_floorplan_svg(plan, output_svg)
print(f"SVG exported: {output_svg}")
