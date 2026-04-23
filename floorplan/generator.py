from __future__ import annotations

import random
from dataclasses import replace
from pathlib import Path
from typing import Dict, List, Tuple

try:
    from floorplan.models import Floorplan, FloorplanVariant, RoomPlacement, RoomSpec
except ModuleNotFoundError:
    from models import Floorplan, FloorplanVariant, RoomPlacement, RoomSpec


WIDTH = 12
HEIGHT = 12
BUILDING_AREA = WIDTH * HEIGHT

ROOMS: List[RoomSpec] = [
    RoomSpec("living", "living", 20, 46, "day", True, ("kitchen", "hall"), ()),
    RoomSpec("kitchen", "kitchen", 8, 18, "service", True, ("living",), ("bedroom_1", "bedroom_2", "bedroom_3")),
    RoomSpec("hall", "hall", 4, 8, "service", True, ("living", "bedroom_1", "bedroom_2", "bedroom_3"), ()),
    RoomSpec("bedroom_1", "bedroom", 9, 18, "night", True, ("hall", "living", "bathroom"), ("kitchen",)),
    RoomSpec("bedroom_2", "bedroom", 9, 18, "night", True, ("hall", "living", "bathroom"), ("kitchen",)),
    RoomSpec("bedroom_3", "bedroom", 9, 16, "night", True, ("hall", "living", "bathroom"), ("kitchen",)),
    RoomSpec("bathroom", "bathroom", 4, 10, "night", True, ("bedroom_1", "bedroom_2", "bedroom_3", "hall"), ()),
    RoomSpec("wc", "wc", 2, 5, "service", False, ("living", "hall"), ()),
]

ROOM_BY_NAME = {r.name: r for r in ROOMS}

MODE_AREA_BIAS = {
    "balanced": 0.50,
    "strict_connectivity": 0.55,
    "zoning_first": 0.50,
}

MODE_WEIGHTS = {
    "balanced": {"zoning": 6, "connectivity": 7, "compactness": 4, "shape": 5, "corridor": -4},
    "strict_connectivity": {"zoning": 4, "connectivity": 10, "compactness": 3, "shape": 4, "corridor": -5},
    "zoning_first": {"zoning": 10, "connectivity": 5, "compactness": 4, "shape": 4, "corridor": -4},
}


def _normalize_sizes(sizes: List[float], total: float) -> List[float]:
    factor = total / max(sum(sizes), 1e-6)
    return [s * factor for s in sizes]


def _worst_ratio(row: List[float], w: float) -> float:
    if not row:
        return float("inf")
    s = sum(row)
    mx = max(row)
    mn = min(row)
    return max((w * w * mx) / (s * s), (s * s) / (w * w * mn))


def _layout_row(row: List[Tuple[str, float]], x: float, y: float, w: float, h: float, horizontal: bool) -> Tuple[List[Tuple[str, float, float, float, float]], float, float, float, float]:
    rects = []
    s = sum(v for _, v in row)
    if horizontal:
        row_h = s / max(w, 1e-6)
        cx = x
        for name, area in row:
            rw = area / max(row_h, 1e-6)
            rects.append((name, cx, y, rw, row_h))
            cx += rw
        return rects, x, y + row_h, w, h - row_h
    row_w = s / max(h, 1e-6)
    cy = y
    for name, area in row:
        rh = area / max(row_w, 1e-6)
        rects.append((name, x, cy, row_w, rh))
        cy += rh
    return rects, x + row_w, y, w - row_w, h


def squarify(named_sizes: List[Tuple[str, float]], x: float, y: float, w: float, h: float) -> List[Tuple[str, float, float, float, float]]:
    items = sorted(named_sizes, key=lambda kv: kv[1], reverse=True)
    rects: List[Tuple[str, float, float, float, float]] = []
    row: List[Tuple[str, float]] = []
    free_x, free_y, free_w, free_h = x, y, w, h

    while items:
        item = items[0]
        row_candidate = row + [item]
        short_side = min(free_w, free_h)

        if not row or _worst_ratio([v for _, v in row_candidate], short_side) <= _worst_ratio([v for _, v in row], short_side):
            row = row_candidate
            items.pop(0)
        else:
            row_rects, free_x, free_y, free_w, free_h = _layout_row(row, free_x, free_y, free_w, free_h, horizontal=free_w >= free_h)
            rects.extend(row_rects)
            row = []

    if row:
        row_rects, free_x, free_y, free_w, free_h = _layout_row(row, free_x, free_y, free_w, free_h, horizontal=free_w >= free_h)
        rects.extend(row_rects)
    return rects


class FloorplanGeneratorV6:
    """V6 inspired by Mirahmadi & Shami (2012):
    hierarchical room placement + squarified treemap + corridor minimization proxy.
    """

    def __init__(self, output_dir: str = "floorplan/out") -> None:
        self.output_dir = Path(output_dir)
        self.output_dir.mkdir(parents=True, exist_ok=True)

    def generate_variants(self, variants_per_mode: int = 3) -> List[FloorplanVariant]:
        variants: List[FloorplanVariant] = []
        for mode in MODE_WEIGHTS:
            seen_signatures: set[Tuple[Tuple[str, int, int, int, int], ...]] = set()
            for rank in range(1, variants_per_mode + 1):
                variant = self._build_variant(mode, rank)
                sig = tuple(sorted((r.name, int(r.x), int(r.y), int(r.w), int(r.h)) for r in variant.floorplan.rooms))
                if sig in seen_signatures:
                    continue
                seen_signatures.add(sig)
                svg_path = str(self._export_svg(mode, rank, variant.metrics["rectangles"], variant.metrics["areas"]))
                variants.append(replace(variant, svg_path=svg_path))
        return variants

    def _sample_room_area(self, spec: RoomSpec, rng: random.Random, mode: str) -> float:
        bias = MODE_AREA_BIAS[mode]
        a = spec.min_area + bias * (spec.max_area - spec.min_area)
        noise = rng.uniform(-0.15, 0.15) * (spec.max_area - spec.min_area)
        return max(spec.min_area, min(spec.max_area, a + noise))

    def _build_variant(self, mode: str, rank: int) -> FloorplanVariant:
        rng = random.Random(hash((mode, rank, "mirahmadi2012")) & 0xFFFFFFFF)

        room_targets = {r.name: self._sample_room_area(r, rng, mode) for r in ROOMS}
        category_targets = {
            "day": room_targets["living"],
            "service": room_targets["kitchen"] + room_targets["hall"] + room_targets["wc"],
            "night": room_targets["bedroom_1"] + room_targets["bedroom_2"] + room_targets["bedroom_3"] + room_targets["bathroom"],
        }
        category_sizes = _normalize_sizes(list(category_targets.values()), BUILDING_AREA)

        level1 = squarify(
            [
                ("day", category_sizes[0]),
                ("service", category_sizes[1]),
                ("night", category_sizes[2]),
            ],
            0,
            0,
            WIDTH,
            HEIGHT,
        )
        blocks = {name: (x, y, w, h) for name, x, y, w, h in level1}

        by_cat = {
            "day": ["living"],
            "service": ["hall", "kitchen", "wc"],
            "night": ["bedroom_1", "bedroom_2", "bedroom_3", "bathroom"],
        }

        rectangles_f: Dict[str, Tuple[float, float, float, float]] = {}
        for cat, room_names in by_cat.items():
            x, y, w, h = blocks[cat]
            local_sizes = _normalize_sizes([room_targets[n] for n in room_names], w * h)
            local = squarify(list(zip(room_names, local_sizes)), x, y, w, h)
            for room_name, rx, ry, rw, rh in local:
                rectangles_f[room_name] = (rx, ry, rw, rh)

        rectangles = {k: {"x": v[0], "y": v[1], "w": v[2], "h": v[3]} for k, v in rectangles_f.items()}

        placements = []
        for spec in ROOMS:
            r = rectangles[spec.name]
            zone_id = {"day": 0, "service": 2, "night": 4}[spec.zone_tag]
            placements.append(RoomPlacement(spec.name, spec.room_type, r["x"], r["y"], r["w"], r["h"], zone_id=zone_id))

        metrics = self._compute_metrics(mode, placements, rectangles)
        floorplan = Floorplan(width=WIDTH, height=HEIGHT, rooms=placements)
        return FloorplanVariant(mode=mode, score=metrics["score"], floorplan=floorplan, metrics=metrics)

    def _adjacency(self, a: RoomPlacement, b: RoomPlacement) -> bool:
        ax1, ay1, ax2, ay2 = a.x, a.y, a.x + a.w, a.y + a.h
        bx1, by1, bx2, by2 = b.x, b.y, b.x + b.w, b.y + b.h
        x_overlap = max(0, min(ax2, bx2) - max(ax1, bx1))
        y_overlap = max(0, min(ay2, by2) - max(ay1, by1))
        eps = 1e-6
        return (((abs(ax2 - bx1) < eps) or (abs(bx2 - ax1) < eps)) and y_overlap > eps) or (((abs(ay2 - by1) < eps) or (abs(by2 - ay1) < eps)) and x_overlap > eps)

    def _compute_metrics(self, mode: str, placements: List[RoomPlacement], rectangles: Dict[str, Dict[str, float]]) -> Dict[str, object]:
        areas = {p.name: int(round(p.area)) for p in placements}
        total_area = sum(p.area for p in placements)
        empty_area = BUILDING_AREA - total_area

        by_name = {p.name: p for p in placements}
        graph: Dict[str, set[str]] = {p.name: set() for p in placements}
        for i, a in enumerate(placements):
            for b in placements[i + 1 :]:
                if self._adjacency(a, b):
                    graph[a.name].add(b.name)
                    graph[b.name].add(a.name)

        stack = ["living"]
        visited = {"living"}
        while stack:
            cur = stack.pop()
            for nxt in graph[cur]:
                if nxt not in visited:
                    visited.add(nxt)
                    stack.append(nxt)

        kitchen_connected = int("kitchen" in visited)
        hall_connected = int("hall" in visited)
        independent_bedrooms = sum(int(b in visited) for b in ["bedroom_1", "bedroom_2", "bedroom_3"])
        isolated_bedrooms = 3 - independent_bedrooms
        bathroom_near = sum(int(b in graph["bathroom"]) for b in ["bedroom_1", "bedroom_2", "bedroom_3"])

        # Corridor minimization proxy inspired by the paper: shortest Manhattan path from disconnected rooms to living.
        living_c = (by_name["living"].x + by_name["living"].w / 2.0, by_name["living"].y + by_name["living"].h / 2.0)
        corridor_cost = 0
        for room in ["kitchen", "hall", "bedroom_1", "bedroom_2", "bedroom_3", "bathroom", "wc"]:
            if room in graph["living"]:
                continue
            c = (by_name[room].x + by_name[room].w / 2.0, by_name[room].y + by_name[room].h / 2.0)
            corridor_cost += int(abs(c[0] - living_c[0]) + abs(c[1] - living_c[1]))

        zoning_score = sum(int(by_name[r.name].zone_id in (0, 2, 4) and ({"day": 0, "service": 2, "night": 4}[r.zone_tag] == by_name[r.name].zone_id)) for r in ROOMS)
        compactness = total_area - empty_area

        shape_score = 0
        for p in placements:
            ratio = max(p.w / max(p.h, 1), p.h / max(p.w, 1))
            shape_score += int(ratio <= 2.5)

        connectivity_score = 9 * kitchen_connected + 7 * hall_connected + 7 * independent_bedrooms + 4 * bathroom_near - 8 * isolated_bedrooms
        score = (
            MODE_WEIGHTS[mode]["zoning"] * zoning_score
            + MODE_WEIGHTS[mode]["connectivity"] * connectivity_score
            + MODE_WEIGHTS[mode]["compactness"] * compactness
            + MODE_WEIGHTS[mode]["shape"] * shape_score
            + MODE_WEIGHTS[mode]["corridor"] * corridor_cost
        )

        centers = {name: (2 * r["x"] + r["w"], 2 * r["y"] + r["h"]) for name, r in rectangles.items()}
        return {
            "score": int(score),
            "occupied_area": int(round(total_area)),
            "empty_area": int(round(empty_area)),
            "entry_access_ok": int(by_name["living"].y == 0 or by_name["hall"].y == 0),
            "entry_into_living": int(by_name["living"].y == 0),
            "entry_into_hall": int(by_name["hall"].y == 0),
            "isolated_bedrooms": isolated_bedrooms,
            "independent_bedrooms": independent_bedrooms,
            "hall_connected_to_living": hall_connected,
            "kitchen_connected_to_living": kitchen_connected,
            "bathroom_near_bedrooms": bathroom_near,
            "connectivity_score": connectivity_score,
            "zoning_score": zoning_score,
            "compactness_score": compactness,
            "circulation_access": independent_bedrooms + kitchen_connected + hall_connected,
            "diversity_score": shape_score,
            "corridor_cost": corridor_cost,
            "sub_scores": {
                "fill": total_area,
                "compactness": compactness,
                "zoning": zoning_score,
                "connectivity": connectivity_score,
                "diversity": shape_score,
            },
            "areas": areas,
            "zones": {p.name: p.zone_id for p in placements},
            "centers": centers,
            "rectangles": rectangles,
        }

    def _export_svg(self, mode: str, rank: int, room_rectangles: Dict[str, Dict[str, float]], room_areas: Dict[str, int]) -> Path:
        scale = 45
        margin = 16
        header_height = 52
        svg_width = WIDTH * scale + margin * 2
        svg_height = HEIGHT * scale + header_height + margin * 2

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
            f'<rect x="{margin}" y="{margin + header_height}" width="{WIDTH * scale}" height="{HEIGHT * scale}" rx="4" fill="#ffffff" stroke="#cbd5e1" stroke-width="1.5"/>',
            f'<text x="{margin}" y="{margin + 18}" font-family="Arial" font-size="18" font-weight="bold" fill="#0f172a">Floorplan V6 (Treemap)</text>',
            f'<text x="{margin + 192}" y="{margin + 18}" font-family="Arial" font-size="14" fill="#475569">{mode} #{rank}</text>',
        ]

        zone_offset_y = margin + header_height
        zone_offset_x = margin

        for room_name, rect in room_rectangles.items():
            rx = rect["x"] * scale + zone_offset_x
            ry = rect["y"] * scale + zone_offset_y
            rw = rect["w"] * scale
            rh = rect["h"] * scale
            fill = colors.get(room_name, "#cbd5e1")
            svg_parts.append(f'<rect x="{rx}" y="{ry}" width="{rw}" height="{rh}" fill="{fill}" stroke="#1f2937" stroke-width="2.5" opacity="1"/>')
            label = f'{room_name} ({room_areas[room_name]}m²)'
            svg_parts.append(f'<text x="{rx + 8}" y="{ry + 18}" font-family="Arial" font-size="11" font-weight="600" fill="#111827">{label}</text>')

        svg_parts.append("</svg>")
        path = self.output_dir / f"v6_{mode}_{rank}.svg"
        path.write_text("\n".join(svg_parts), encoding="utf-8")
        return path
