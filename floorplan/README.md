# Floorplan V5 (CP-SAT layout + zoning + circulation)

Cette version applique une modélisation OR-Tools plus proche d'un problème de **2D layout optimization**.

## Ce qui a changé

- Ajout d'un vrai placement géométrique avec variables `(x, y, w, h)`.
- `area = w * h` via `AddMultiplicationEquality`.
- Non-chevauchement robuste avec `AddNoOverlap2D`.
- Les centres des pièces sont ancrés dans des zones fonctionnelles (jour / nuit / service).
- Scoring structuré en sous-scores :
  - `compactness`
  - `zoning`
  - `connectivity`
  - `diversity`
- Diversité renforcée entre variantes (au moins 2 affectations de zones différentes par variante bloquée).
- Connectivité améliorée via accès direct ou à un saut vers le salon.

## Exécution

```bash
pip install -r floorplan/requirements.txt
python floorplan/main.py
```

Les variantes SVG sont générées dans `floorplan/out/`.
