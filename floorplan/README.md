# Floorplan Generator (V3)

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

- génère **plusieurs variantes** de plan (5 par défaut),
- affiche un résumé en console avec un **score** par variante,
- exporte un SVG par variante :
  - `floorplan/output_1.svg`
  - `floorplan/output_2.svg`
  - `floorplan/output_3.svg`
  - `floorplan/output_4.svg`
  - `floorplan/output_5.svg`

Les SVG incluent des labels lisibles (nom + surface + dimensions) et des couleurs par type de pièce.
