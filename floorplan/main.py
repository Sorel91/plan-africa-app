from generator import FloorplanGenerator, export_floorplan_svg
from models import RoomSpec

rooms = [
    RoomSpec("Salon", "living_room", 25, 35),
    RoomSpec("Cuisine", "kitchen", 10, 15),
    RoomSpec("Chambre 1", "bedroom", 10, 15),
    RoomSpec("Chambre 2", "bedroom", 10, 15),
]

generator = FloorplanGenerator(10, 10, rooms, grid_step=0.5)
variants = generator.generate_variants(count=5)

for variant in variants:
    print(f"\nVariant {variant.index} | score={variant.score:.1f}")
    print(f"Building: {variant.floorplan.width}m x {variant.floorplan.height}m")

    for room in variant.floorplan.rooms:
        area = room.w * room.h
        print(
            f"- {room.name} | type={room.room_type} | "
            f"x={room.x:.1f}, y={room.y:.1f}, w={room.w:.1f}, h={room.h:.1f}, area={area:.1f}m²"
        )

    output_svg = f"floorplan/output_{variant.index}.svg"
    export_floorplan_svg(
        variant.floorplan,
        output_svg,
        title=f"Variant {variant.index} - score {variant.score:.1f}",
    )
    print(f"SVG exported: {output_svg}")
