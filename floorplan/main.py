from __future__ import annotations

try:
    from floorplan.generator import FloorplanGeneratorV5
except ModuleNotFoundError:
    from generator import FloorplanGeneratorV5


def _room_summary(areas: dict[str, int], zones: dict[str, int]) -> str:
    ordered = []
    for room in sorted(areas.keys()):
        ordered.append(f"{room}: {areas[room]}m²@Z{zones[room]}")
    return ", ".join(ordered)


def main() -> None:
    generator = FloorplanGeneratorV5()
    variants = generator.generate_variants(variants_per_mode=3)

    print("=== Floorplan V5 / OR-Tools CP-SAT layout ===")
    if not variants:
        print("Aucune variante trouvée.")
        return

    for item in variants:
        metrics = item["metrics"]
        sub_scores = metrics["sub_scores"]
        print(
            f"mode={item['mode']} | score={item['score']} | "
            f"compactness={sub_scores['compactness']} | "
            f"zoning={sub_scores['zoning']} | "
            f"connectivity={sub_scores['connectivity']} | "
            f"diversity={sub_scores['diversity']}"
        )
        print(
            f"  kitchen_connected_to_living={metrics['kitchen_connected_to_living']} | "
            f"connected_bedrooms={metrics['connected_bedrooms']} | "
            f"isolated_bedrooms={metrics['isolated_bedrooms']} | "
            f"bathroom_near_bedrooms={metrics['bathroom_near_bedrooms']} | "
            f"circulation_access={metrics['circulation_access']}"
        )
        print(f"  rooms: {_room_summary(item['areas'], item['zones'])}")
        print(f"  svg: {item['svg_path']}")


if __name__ == "__main__":
    main()
