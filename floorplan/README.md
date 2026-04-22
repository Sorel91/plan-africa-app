# Floorplan Generator (V4)

Base Python d’un générateur de plans 2D avec OR-Tools, en grille discrète de 0.5 m.

## Installation

```bash
pip install -r floorplan/requirements.txt
```

## Exécution

```bash
python floorplan/main.py
```

## Résultat

Le script :

- génère plusieurs variantes de plan (5 par défaut),
- applique des **modes de layout** différents pour augmenter la diversité,
- calcule un score avec compacité + zoning simple,
- affiche un résumé console par variante (score, mode, métriques),
- exporte un SVG par variante : `floorplan/output_1.svg` à `floorplan/output_5.svg`.

Le zoning simple inclut :

- chambres regroupées selon le mode,
- salon dominant,
- cuisine encouragée proche du salon,
- séparation chambre/salon favorisée.
