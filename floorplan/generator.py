from __future__ import annotations

from dataclasses import replace
from collections import defaultdict
from pathlib import Path
from typing import Dict, List, Tuple

try:
    from floorplan.models import Floorplan, FloorplanVariant, RoomPlacement, RoomSpec
except ModuleNotFoundError:
    from models import Floorplan, FloorplanVariant, RoomPlacement, RoomSpec


BUILDING_WIDTH = 12
BUILDING_HEIGHT = 12

ROOMS: List[RoomSpec] = [
    RoomSpec("living", "living", 20, 46, "day", True, ("kitchen", "hall"), ()),
    RoomSpec("kitchen", "kitchen", 8, 18, "day", True, ("living",), ("bedroom_1", "bedroom_2", "bedroom_3")),
    RoomSpec("hall", "hall", 4, 10, "service", True, ("living", "bedroom_1", "bedroom_2", "bedroom_3"), ()),
    RoomSpec("bedroom_1", "bedroom", 9, 18, "night", True, ("hall", "living", "bathroom"), ("kitchen",)),
    RoomSpec("bedroom_2", "bedroom", 9, 18, "night", True, ("hall", "living", "bathroom"), ("kitchen",)),
    RoomSpec("bedroom_3", "bedroom", 9, 16, "night", True, ("hall", "living", "bathroom"), ("kitchen",)),
    RoomSpec("bathroom", "bathroom", 4, 10, "service", True, ("bedroom_1", "bedroom_2", "bedroom_3", "hall"), ()),
    RoomSpec("wc", "wc", 2, 6, "service", False, ("living", "hall"), ()),
]

ROOM_BY_NAME = {r.name: r for r in ROOMS}

# Inspiré des guides "slicing floorplan" + "adjacency graph" :
# 1) assignation topologique des pièces à des macro-zones,
# 2) découpage récursif (guillotine/slicing) à l'intérieur des zones.
ZONES: Dict[int, Dict[str, object]] = {
    0: {"x": 0, "y": 0, "w": 7, "h": 4, "tag": "day"},
    1: {"x": 7, "y": 0, "w": 5, "h": 4, "tag": "day"},
    2: {"x": 0, "y": 4, "w": 4, "h": 4, "tag": "service"},
    3: {"x": 4, "y": 4, "w": 8, "h": 4, "tag": "night"},
    4: {"x": 0, "y": 8, "w": 6, "h": 4, "tag": "night"},
    5: {"x": 6, "y": 8, "w": 6, "h": 4, "tag": "service"},
}

MODE_ZONE_TEMPLATES: Dict[str, List[Dict[str, int]]] = {
    "balanced": [
        {
            "living": 0,
            "kitchen": 1,
            "hall": 2,
            "bedroom_1": 3,
            "bedroom_2": 4,
            "bedroom_3": 4,
            "bathroom": 5,
            "wc": 2,
        },
        {
            "living": 1,
            "kitchen": 0,
            "hall": 2,
            "bedroom_1": 3,
            "bedroom_2": 3,
            "bedroom_3": 4,
            "bathroom": 5,
            "wc": 5,
        },
    ],
    "strict_connectivity": [
        {
            "living": 0,
            "kitchen": 1,
            "hall": 3,
            "bedroom_1": 4,
            "bedroom_2": 4,
            "bedroom_3": 3,
            "bathroom": 5,
            "wc": 2,
        },
        {
            "living": 1,
            "kitchen": 0,
            "hall": 3,
            "bedroom_1": 3,
            "bedroom_2": 4,
            "bedroom_3": 4,
            "bathroom": 5,
            "wc": 2,
        },
    ],
    "zoning_first": [
        {
            "living": 0,
            "kitchen": 1,
            "hall": 5,
            "bedroom_1": 3,
            "bedroom_2": 4,
            "bedroom_3": 4,
            "bathroom": 2,
            "wc": 5,
        },
        {
            "living": 1,
            "kitchen": 0,
            "hall": 2,
            "bedroom_1": 3,
            "bedroom_2": 4,
            "bedroom_3": 3,
            "bathroom": 5,
            "wc": 2,
        },
    ],
}

MODE_WEIGHTS = {
    "balanced": {"zoning": 6, "connectivity": 6, "compactness": 4, "diversity": 3, "area": 2},
    "strict_connectivity": {"zoning": 4, "connectivity": 9, "compactness": 4, "diversity": 2, "area": 2},
    "zoning_first": {"zoning": 10, "connectivity": 4, "compactness": 4, "diversity": 2, "area": 2},
}


class FloorplanGeneratorV6:
    def __init__(self, output_dir: str = "floorplan/out") -> None:
        self.output_dir = Path(output_dir)
        self.output_dir.mkdir(parents=True, exist_ok=True)

    def generate_variants(self, variants_per_mode: int = 3) -> List[FloorplanVariant]:
        variants: List[FloorplanVariant] = []
        for mode in MODE_WEIGHTS:
            seen_signatures: set[Tuple[Tuple[str, int], ...]] = set()
            rank = 1
            attempts = 0
            while rank <= variants_per_mode and attempts < variants_per_mode * 5:
                attempts += 1
                candidate = self._build_variant(mode, rank + attempts - 1)
                signature = tuple(sorted(candidate.metrics["zones"].items()))
                if signature in seen_signatures:
                    continue
                seen_signatures.add(signature)
                metrics = dict(candidate.metrics)
                metrics["rank"] = rank
                svg_path = str(self._export_svg(mode, rank, metrics["rectangles"], metrics["areas"]))
                variants.append(replace(candidate, metrics=metrics, svg_path=svg_path))
                rank += 1
        return variants

    def _build_variant(self, mode: str, seed: int) -> FloorplanVariant:
        template = MODE_ZONE_TEMPLATES[mode][seed % len(MODE_ZONE_TEMPLATES[mode])].copy()

        if seed % 3 == 0:
            template["bedroom_2"], template["bedroom_3"] = template["bedroom_3"], template["bedroom_2"]
        if seed % 4 == 0:
            template["wc"], template["hall"] = template["hall"], template["wc"]

        zone_rooms: Dict[int, List[str]] = defaultdict(list)
        for room_name, z in template.items():
            zone_rooms[z].append(room_name)

        rectangles: Dict[str, Dict[str, int]] = {}
        for z, room_names in zone_rooms.items():
            info = ZONES[z]
            self._slice_zone(
                room_names=room_names,
                x=int(info["x"]),
                y=int(info["y"]),
                w=int(info["w"]),
                h=int(info["h"]),
                depth=0,
                out=rectangles,
            )

        self._enforce_room_area_bounds(rectangles)

        placements = [
            RoomPlacement(
                name=spec.name,
                room_type=spec.room_type,
                x=rectangles[spec.name]["x"],
                y=rectangles[spec.name]["y"],
                w=rectangles[spec.name]["w"],
                h=rectangles[spec.name]["h"],
                zone_id=template[spec.name],
            )
            for spec in ROOMS
        ]

        metrics = self._compute_metrics(mode, placements, template, rectangles)
        floorplan = Floorplan(width=BUILDING_WIDTH, height=BUILDING_HEIGHT, rooms=placements)
        score = metrics["score"]
        return FloorplanVariant(mode=mode, score=score, floorplan=floorplan, metrics=metrics)

    def _slice_zone(
        self,
        room_names: List[str],
        x: int,
        y: int,
        w: int,
        h: int,
        depth: int,
        out: Dict[str, Dict[str, int]],
    ) -> None:
        if len(room_names) == 1:
            out[room_names[0]] = {"x": x, "y": y, "w": max(1, w), "h": max(1, h)}
            return

        room_names = sorted(room_names, key=lambda name: (ROOM_BY_NAME[name].min_area + ROOM_BY_NAME[name].max_area) / 2, reverse=True)
        left = room_names[: len(room_names) // 2]
        right = room_names[len(room_names) // 2 :]

        left_target = sum((ROOM_BY_NAME[name].min_area + ROOM_BY_NAME[name].max_area) / 2 for name in left)
        right_target = sum((ROOM_BY_NAME[name].min_area + ROOM_BY_NAME[name].max_area) / 2 for name in right)
        ratio = left_target / max(1.0, left_target + right_target)

        vertical_cut = w >= h if depth % 2 == 0 else w > 3
        if vertical_cut and w >= 2:
            cut = max(1, min(w - 1, int(round(w * ratio))))
            self._slice_zone(left, x, y, cut, h, depth + 1, out)
            self._slice_zone(right, x + cut, y, w - cut, h, depth + 1, out)
        else:
            cut = max(1, min(h - 1, int(round(h * ratio))))
            self._slice_zone(left, x, y, w, cut, depth + 1, out)
            self._slice_zone(right, x, y + cut, w, h - cut, depth + 1, out)

    def _enforce_room_area_bounds(self, rectangles: Dict[str, Dict[str, int]]) -> None:
        for room_name, rect in rectangles.items():
            spec = ROOM_BY_NAME[room_name]
            target_max = int(spec.max_area)
            while rect["w"] * rect["h"] > target_max and rect["w"] > 1 and rect["h"] > 1:
                if rect["w"] >= rect["h"]:
                    rect["w"] -= 1
                else:
                    rect["h"] -= 1




    def _compute_metrics(
        self,
        mode: str,
        placements: List[RoomPlacement],
        template: Dict[str, int],
        rectangles: Dict[str, Dict[str, int]],
    ) -> Dict[str, object]:
        areas = {p.name: int(p.area) for p in placements}
        total_area = sum(areas.values())
        empty_area = BUILDING_WIDTH * BUILDING_HEIGHT - total_area

        room_tag_hits = 0
        for p in placements:
            if ZONES[p.zone_id]["tag"] == ROOM_BY_NAME[p.name].zone_tag:
                room_tag_hits += 1

        adjacency = self._build_adjacency(placements)

        kitchen_connected = int("living" in adjacency["kitchen"])
        hall_connected = int("living" in adjacency["hall"])
        independent_bedrooms = sum(int("hall" in adjacency[b] or "living" in adjacency[b]) for b in ["bedroom_1", "bedroom_2", "bedroom_3"])
        isolated_bedrooms = 3 - independent_bedrooms
        bathroom_near = sum(int(b in adjacency["bathroom"]) for b in ["bedroom_1", "bedroom_2", "bedroom_3"])

        circulation_access = kitchen_connected + hall_connected + independent_bedrooms + bathroom_near
        if mode == "strict_connectivity":
            circulation_access += 2 * int(kitchen_connected and hall_connected)

        used_zones = len(set(template.values()))
        compactness = total_area + (len(ZONES) - used_zones) * 4
        diversity = 24 - used_zones * 2 - max(0, 4 - len([z for z in set(template.values()) if list(template.values()).count(z) <= 2]))

        area_fit = 0
        for p in placements:
            spec = ROOM_BY_NAME[p.name]
            area_fit += int(spec.min_area <= p.area <= spec.max_area)

        connectivity_score = 8 * kitchen_connected + 6 * hall_connected + 6 * independent_bedrooms + 3 * bathroom_near - 5 * isolated_bedrooms + 4 * circulation_access

        weights = MODE_WEIGHTS[mode]
        score = (
            weights["zoning"] * room_tag_hits
            + weights["connectivity"] * connectivity_score
            + weights["compactness"] * compactness
            + weights["diversity"] * diversity
            + weights["area"] * area_fit
            - 3 * max(0, empty_area)
        )

        centers = {name: (2 * r["x"] + r["w"], 2 * r["y"] + r["h"]) for name, r in rectangles.items()}
        return {
            "score": score,
            "occupied_area": total_area,
            "empty_area": empty_area,
            "entry_access_ok": int(rectangles["living"]["y"] == 0 or rectangles["hall"]["y"] == 0),
            "entry_into_living": int(rectangles["living"]["y"] == 0),
            "entry_into_hall": int(rectangles["hall"]["y"] == 0),
            "isolated_bedrooms": isolated_bedrooms,
            "independent_bedrooms": independent_bedrooms,
            "hall_connected_to_living": hall_connected,
            "kitchen_connected_to_living": kitchen_connected,
            "bathroom_near_bedrooms": bathroom_near,
            "connectivity_score": connectivity_score,
            "zoning_score": room_tag_hits,
            "compactness_score": compactness,
            "circulation_access": circulation_access,
            "diversity_score": diversity,
            "sub_scores": {
                "fill": total_area,
                "compactness": compactness,
                "zoning": room_tag_hits,
                "connectivity": connectivity_score,
                "diversity": diversity,
            },
            "areas": areas,
            "zones": template,
            "centers": centers,
            "rectangles": rectangles,
        }

    def _build_adjacency(self, placements: List[RoomPlacement]) -> Dict[str, set[str]]:
        adjacency: Dict[str, set[str]] = {p.name: set() for p in placements}
        for i, a in enumerate(placements):
            for b in placements[i + 1 :]:
                if self._touch(a, b):
                    adjacency[a.name].add(b.name)
                    adjacency[b.name].add(a.name)
        return adjacency

    def _touch(self, a: RoomPlacement, b: RoomPlacement) -> bool:
        ax1, ay1, ax2, ay2 = a.x, a.y, a.x + a.w, a.y + a.h
        bx1, by1, bx2, by2 = b.x, b.y, b.x + b.w, b.y + b.h

        x_overlap = max(0, min(ax2, bx2) - max(ax1, bx1))
        y_overlap = max(0, min(ay2, by2) - max(ay1, by1))

        share_vertical_edge = (ax2 == bx1 or bx2 == ax1) and y_overlap > 0
        share_horizontal_edge = (ay2 == by1 or by2 == ay1) and x_overlap > 0
        return share_vertical_edge or share_horizontal_edge

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
        svg_width = BUILDING_WIDTH * scale + margin * 2
        svg_height = BUILDING_HEIGHT * scale + header_height + margin * 2

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

        svg_parts = [
            f'<svg xmlns="http://www.w3.org/2000/svg" width="{svg_width}" height="{svg_height}" viewBox="0 0 {svg_width} {svg_height}">',
            '<rect x="0" y="0" width="100%" height="100%" fill="#f8fafc"/>',
            f'<rect x="{margin}" y="{margin + header_height}" width="{BUILDING_WIDTH * scale}" height="{BUILDING_HEIGHT * scale}" rx="4" fill="#ffffff" stroke="#cbd5e1" stroke-width="1.5"/>',
            f'<text x="{margin}" y="{margin + 18}" font-family="Arial" font-size="18" font-weight="bold" fill="#0f172a">Floorplan V6</text>',
            f'<text x="{margin + 126}" y="{margin + 18}" font-family="Arial" font-size="14" fill="#475569">{mode} #{rank}</text>',
        ]

        zone_offset_y = margin + header_height
        zone_offset_x = margin

        for zone_id, z in ZONES.items():
            zx, zy = int(z["x"] * scale) + zone_offset_x, int(z["y"] * scale) + zone_offset_y
            zw, zh = int(z["w"] * scale), int(z["h"] * scale)
            svg_parts.append(
                f'<rect x="{zx}" y="{zy}" width="{zw}" height="{zh}" fill="none" stroke="#cbd5e1" stroke-width="1" stroke-dasharray="6 5" opacity="0.45"/>'
            )
            svg_parts.append(
                f'<text x="{zx + 8}" y="{zy + 18}" font-family="Arial" font-size="11" fill="#94a3b8" opacity="0.6">Z{zone_id} ({z["tag"]})</text>'
            )

        for room_name, rect in room_rectangles.items():
            rx = rect["x"] * scale + zone_offset_x
            ry = rect["y"] * scale + zone_offset_y
            rw = rect["w"] * scale
            rh = rect["h"] * scale
            fill = colors.get(room_name, "#cbd5e1")

            svg_parts.append(
                f'<rect x="{rx}" y="{ry}" width="{rw}" height="{rh}" fill="{fill}" stroke="#1f2937" stroke-width="2.5" opacity="1"/>'
            )
            label = f'{room_name} ({room_areas[room_name]}m²)'
            svg_parts.append(
                f'<text x="{rx + 8}" y="{ry + 20}" font-family="Arial" font-size="12" font-weight="600" fill="#111827">{label}</text>'
            )

        svg_parts.append("</svg>")
        path = self.output_dir / f"v6_{mode}_{rank}.svg"
        path.write_text("\n".join(svg_parts), encoding="utf-8")
        return path
