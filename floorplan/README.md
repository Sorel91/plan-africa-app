# Floorplan V6 (Slicing layout + adjacency graph)

Cette version remplace l'ancien solveur CP-SAT par une approche **constructive + heuristique** plus lisible et plus rapide à itérer.

## Principes de conception (inspirés des guides de floorplanning)

- **Slicing floorplan / guillotine partition** : découpage récursif d'une zone rectangulaire en sous-rectangles.
- **Adjacency graph** : vérification des connexions clés (cuisine-salon, chambres-hall/salon, etc.) via contacts d'arêtes.
- **Macro-zoning** : affectation initiale des pièces dans des zones jour / nuit / service pour conserver une logique architecturale.

## Pipeline V6

1. Choisir un template de zones selon le mode (`balanced`, `strict_connectivity`, `zoning_first`).
2. Découper chaque macro-zone en rectangles de pièces via un slicing récursif.
3. Calculer les métriques (zoning, connectivité, compacité, diversité, respect des surfaces).
4. Exporter les variantes SVG dans `floorplan/out/`.

## Pourquoi c'est moins laborieux

- Plus besoin de maintenir un grand modèle CP-SAT avec des centaines de contraintes booléennes.
- Les règles sont localisées dans des fonctions courtes (`_slice_zone`, `_build_adjacency`, `_compute_metrics`).
- L'exploration de variantes est simple à enrichir via les templates de zones.

## Exécution

```bash
pip install -r floorplan/requirements.txt
python floorplan/main.py
```

Les variantes SVG sont générées dans `floorplan/out/`.
