from __future__ import annotations

from floorplan.generator import FloorplanGeneratorV5


def _room_summary(areas: dict[str, int], zones: dict[str, int]) -> str:
    ordered = []
    for room in sorted(areas.keys()):
        ordered.append(f"{room}: {areas[room]}m²@Z{zones[room]}")
    return ", ".join(ordered)


def main() -> None:
    generator = FloorplanGeneratorV5()
    variants = generator.generate_variants(variants_per_mode=3)

    print("=== Floorplan V5 / Connectivité-Habitabilité ===")
    if not variants:
        print("Aucune variante trouvée.")
        return

    for item in variants:
        metrics = item["metrics"]
        print(
            f"mode={item['mode']} | score={item['score']} | "
            f"connectivity_score={metrics['connectivity_score']} | "
            f"kitchen_connected_to_living={metrics['kitchen_connected_to_living']} | "
            f"connected_bedrooms={metrics['connected_bedrooms']} | "
            f"isolated_bedrooms={metrics['isolated_bedrooms']}"
        )
        print(f"  rooms: {_room_summary(item['areas'], item['zones'])}")
        print(f"  svg: {item['svg_path']}")


if __name__ == "__main__":
    main()
