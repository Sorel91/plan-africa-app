from dataclasses import dataclass
from typing import List

@dataclass
class RoomSpec:
    name: str
    room_type: str
    min_area: float
    max_area: float

@dataclass
class RoomPlacement:
    name: str
    room_type: str
    x: float
    y: float
    w: float
    h: float

@dataclass
class Floorplan:
    width: float
    height: float
    rooms: List[RoomPlacement]
