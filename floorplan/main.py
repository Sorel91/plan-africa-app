from __future__ import annotations

try:
    from floorplan.generator import FloorplanGeneratorV5
except ModuleNotFoundError:
    from generator import FloorplanGeneratorV5


def main() -> None:
    generator = FloorplanGeneratorV5()
    variants = generator.generate_variants(variants_per_mode=3)

    print("=== Floorplan V5 / OR-Tools CP-SAT layout ===")

    if not variants:
        print("Aucune variante trouvée.")
        return

    for v in variants:
        m = v.metrics
        sub = m["sub_scores"]

        print(
            f"mode={v.mode} | score={v.score} | "
            f"compactness={sub['compactness']} | "
            f"zoning={sub['zoning']} | "
            f"connectivity={sub['connectivity']} | "
            f"diversity={sub['diversity']}"
        )

        print(
            f"  occupied_area={m['occupied_area']} | "
            f"empty_area={m['empty_area']} | "
            f"kitchen_connected_to_living={m['kitchen_connected_to_living']} | "
            f"hall_connected_to_living={m['hall_connected_to_living']} | "
            f"independent_bedrooms={m['independent_bedrooms']} | "
            f"isolated_bedrooms={m['isolated_bedrooms']} | "
            f"bathroom_near_bedrooms={m['bathroom_near_bedrooms']} | "
            f"circulation_access={m['circulation_access']}"
        )

        room_summary = ", ".join(
            f"{r.name}: {r.area:.0f}m²@Z{r.zone_id}" for r in v.floorplan.rooms
        )
        print(f"  rooms: {room_summary}")
        print(f"  svg: {v.svg_path}")


if __name__ == "__main__":
    main()
