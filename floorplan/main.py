from generator import FloorplanGenerator
from models import RoomSpec

rooms = [
    RoomSpec("Salon", "living_room", 25, 35),
    RoomSpec("Cuisine", "kitchen", 10, 15),
    RoomSpec("Chambre 1", "bedroom", 10, 15),
    RoomSpec("Chambre 2", "bedroom", 10, 15),
]

generator = FloorplanGenerator(10, 10, rooms)
plan = generator.generate()

print(f"Building: {plan.width}m x {plan.height}m")
for room in plan.rooms:
    print(
        f"{room.name} | type={room.room_type} | "
        f"x={room.x}, y={room.y}, w={room.w}, h={room.h}"
    )
