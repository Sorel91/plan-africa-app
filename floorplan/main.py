from __future__ import annotations

from floorplan.generator import FloorplanGeneratorV5


def room_summary(areas: dict[str, int], zones: dict[str, int]) -> str:
    return ", ".join(
        f"{room}: {areas[room]}m²@Z{zones[room]}"
        for room in sorted(areas.keys())
    )


def main() -> None:
    generator = FloorplanGeneratorV5()
    variants = generator.generate_variants(variants_per_mode=3)

    print("=== Floorplan V5 (connectivité / habitabilité) ===")
    if not variants:
        print("Aucune variante générée.")
        return

    for variant in variants:
        metrics = variant["metrics"]
        print(
            f"mode={variant['mode']} | score={variant['score']} | "
            f"connectivity_score={metrics['connectivity_score']} | "
            f"kitchen_connected_to_living={metrics['kitchen_connected_to_living']} | "
            f"connected_bedrooms={metrics['connected_bedrooms']} | "
            f"isolated_bedrooms={metrics['isolated_bedrooms']}"
        )
        print(f"  rooms: {room_summary(variant['areas'], variant['zones'])}")
        print(f"  svg: {variant['svg_path']}")


if __name__ == "__main__":
    main()
