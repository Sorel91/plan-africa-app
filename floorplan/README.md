# Floorplan V6 (CP-SAT layout + zoning + circulation)

Refonte V6 : retour à une base **CP-SAT robuste** (OR-Tools), pour privilégier la qualité des plans 2D et éviter les artefacts de l'approche purement heuristique.

## Principes appliqués

- **2D rectangle packing** avec `AddNoOverlap2D` pour garantir l'absence de chevauchement.
- **Area-driven sizing** avec `area = w * h` (`AddMultiplicationEquality`) pour des surfaces cohérentes.
- **Macro-zoning guidé** (jour / nuit / service) via contraintes sur les centres des pièces.
- **Adjacency/proximity scoring** inspiré des pratiques de space-planning (proximité fonctionnelle et circulation).
- **Diversity blocking** entre variantes pour éviter les plans quasi identiques.

## Pipeline

1. Créer les variables géométriques `(x, y, w, h)` et surfaces.
2. Appliquer contraintes dures (non-overlap, limites, accès, connectivité minimale).
3. Scorer les critères (zoning, circulation, compacité, connectivité, diversité).
4. Extraire plusieurs variantes par mode et exporter en SVG.

## Exécution

```bash
pip install -r floorplan/requirements.txt
python floorplan/main.py
```

Sortie : variantes SVG dans `floorplan/out/`.
