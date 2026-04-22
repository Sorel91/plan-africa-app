# Floorplan V5

Refonte complète de la V5 orientée **connectivité** et **habitabilité**.

## Principes

- Génération de variantes CP-SAT par mode (`balanced`, `strict_connectivity`, `zoning_first`).
- Renforcement fort de la liaison **cuisine ↔ salon**.
- Connectivité explicite des chambres (adjacence entre chambres, non-isolement).
- Logique de circulation implicite (accès plausible à la zone de vie sans couloir dessiné).
- Scoring global qui conserve aussi compacité, zoning et dominance du salon.

## Métriques V5

- `isolated_bedrooms`
- `connected_bedrooms`
- `kitchen_connected_to_living`
- `connectivity_score`

Toutes les métriques agrégées sont matérialisées dans des `IntVar` dédiées avant lecture via `solver.Value(...)`.

## Exécution

```bash
python -m floorplan.main
```

Les SVG sont exportés dans `floorplan/out/`.
