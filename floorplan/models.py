from __future__ import annotations

from dataclasses import dataclass, field
from typing import Dict, List, Tuple


@dataclass(frozen=True)
class RoomSpec:
    """Canonical room definition used across the floorplan package.

    The additional fields are optional by default so older code can still
    instantiate the model with only the basic geometric information.
    """

    name: str
    room_type: str
    min_area: float
    max_area: float
    zone_tag: str = "generic"
    important_for_circulation: bool = False
    preferred_adjacent_to: Tuple[str, ...] = ()
    avoid_adjacent_to: Tuple[str, ...] = ()


@dataclass(frozen=True)
class RoomPlacement:
    name: str
    room_type: str
    x: float
    y: float
    w: float
    h: float
    zone_id: int | None = None

    @property
    def area(self) -> float:
        return self.w * self.h


@dataclass(frozen=True)
class Floorplan:
    width: float
    height: float
    rooms: List[RoomPlacement]


@dataclass(frozen=True)
class FloorplanVariant:
    mode: str
    score: float
    floorplan: Floorplan
    metrics: Dict[str, int] = field(default_factory=dict)
    svg_path: str = ""
