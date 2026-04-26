# Floorplan V6 (Treemap hiérarchique + proxy corridor)

Cette version applique une approche inspirée de l'article :
**Mirahmadi & Shami, “A Novel Algorithm for Real-time Procedural Generation of Building Floor Plans” (arXiv:1211.5842)**.

## Ce qui a changé

- Placement basé sur **squarified treemap** (rectangles plus “naturels”, moins allongés).
- Organisation **hiérarchique** des pièces : `day` (living), `service` (kitchen/hall/wc), `night` (bedrooms/bathroom).
- **Scoring de connectivité** via graphe d'adjacence (contacts d'arêtes entre pièces).
- Ajout d'un **proxy de coût corridor** (distance de Manhattan au living pour les pièces non adjacentes).
- Génération multi-modes conservée : `balanced`, `strict_connectivity`, `zoning_first`.

## Pipeline

1. Échantillonnage des surfaces cibles par pièce (dans min/max).
2. Découpage niveau 1 (day/service/night) avec squarified treemap.
3. Découpage niveau 2 (pièces de chaque catégorie) avec squarified treemap.
4. Évaluation (zoning, connectivité, compacité, forme, coût corridor).
5. Export des variantes SVG.

## Exécution

```bash
pip install -r floorplan/requirements.txt
python floorplan/main.py
```

Sortie : `floorplan/out/v6_*.svg`.
