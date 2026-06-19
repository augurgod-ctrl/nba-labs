# NBA Labs 🔬

> Sistema de investigación cuantitativa para trades en US30 (Dow Jones).

## Power 5 — Variables de Medición

| Variable  | Escala | Descripción |
|-----------|--------|-------------|
| Gravity   | 0–100  | Densidad de niveles clave cerca del precio |
| Velocity  | 0–100  | Momentum de las 3 velas previas vs ATR |
| HTF Bias  | -1/0/1 | Estructura diaria (alcista/neutral/bajista) |
| Air Pocket| 0–100  | Espacio libre para moverse sin obstrucciones |
| Regime    | 1–5    | Condición de mercado (tendencia fuerte → chop) |

## Estructura

```
nba_labs/
├── data/
│   ├── trades.csv          # Dataset principal
│   └── nba_labs.db         # SQLite (auto-generado)
├── scripts/
│   ├── fetch_us30.py       # Descarga datos YM=F y calcula Power 5
│   ├── import_csv.py       # Importa CSV → SQLite
│   └── feature_analysis.py # Reproducibility Test™
├── research/
│   └── crime_scenes/       # Documentación por trade
├── docs/
│   └── ROADMAP.md
└── .github/workflows/
    └── daily_fetch.yml     # Auto-fetch diario (GitHub Actions)
```

## Setup rápido

```bash
pip install yfinance pandas openpyxl

# Descargar últimos 5 días de US30
python scripts/fetch_us30.py --days 5 --trades 3

# Importar a DB
python scripts/import_csv.py

# Correr Reproducibility Test™
python scripts/feature_analysis.py
```

## Automatización (GitHub Actions)

El workflow `.github/workflows/daily_fetch.yml` corre automáticamente:
- **7:30 AM ET** (pre-market, Lun–Vie)
- **11:00 AM ET** (post NY Open, Lun–Vie)

Requiere que el repo sea **público** o tener GitHub Actions habilitado. No requiere tokens adicionales.

## Roadmap

Ver [`docs/ROADMAP.md`](docs/ROADMAP.md)

- **Hito 1**: Crime Scenes #001–#010 (validar medición)
- **Hito 2**: Schema Audit
- **Hito 3**: 100 Trade Dataset (solo si Schema Audit pasa)
