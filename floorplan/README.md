# Floorplan V5 (connectivité / habitabilité)

Cette version V5 met l'accent sur la connectivité implicite via OR-Tools CP-SAT.

## Nouveautés principales

- Connexion cuisine ↔ salon fortement pondérée dans le scoring.
- En mode `strict_connectivity`, la cuisine connectée au salon est imposée.
- Gestion de l'isolement des chambres via booléens d'adjacence.
- Bonus de groupe des chambres (cluster) et malus chambres isolées.
- Première logique de circulation implicite via accès plausible à la zone de vie.
- Ajout de métriques explicites :
  - `isolated_bedrooms`
  - `connected_bedrooms`
  - `kitchen_connected_to_living`
  - `connectivity_score`

## Robustesse OR-Tools

Les sommes destinées aux métriques sont stockées dans des `IntVar` agrégées via `model.Add(...)`.
Aucune conversion risquée du type `int(expr)` n'est utilisée sur des expressions OR-Tools.

## Exécution

```bash
python -m floorplan.main
```

Les variantes SVG sont générées dans `floorplan/out/`.
