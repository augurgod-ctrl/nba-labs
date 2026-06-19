#!/bin/bash
# NBA Labs — GitHub Setup Script
# Corre esto en Terminal UNA SOLA VEZ
# ---------------------------------------------------------
# ANTES de correr:
#   1. Ve a https://github.com/new
#   2. Crea repo llamado "nba-labs" (público, SIN readme/gitignore)
#   3. Copia la URL SSH o HTTPS que te da GitHub
#   4. Pégala abajo en REPO_URL

REPO_URL="https://github.com/TU_USUARIO/nba-labs.git"   # ← CAMBIAR

# ---------------------------------------------------------
set -e

# Ir a la carpeta del proyecto
SCRIPT_DIR="$(cd "$(dirname "$0")" && pwd)"
cd "$SCRIPT_DIR"

echo "📁 Directorio: $SCRIPT_DIR"

# Limpiar git anterior (del sandbox)
rm -rf .git

# Inicializar limpio
git init
git branch -M main
git config user.name "Carlos"
git config user.email "augurgod@gmail.com"

# Agregar todo
git add -A
git status

# Primer commit
git commit -m "🔬 NBA Labs v1.0 — Power 5 research system for US30

- Power 5: Gravity, Velocity, HTF Bias, Air Pocket, Regime
- fetch_us30.py: auto-fetch YM=F + calcula Power 5
- import_csv.py: trades.csv → SQLite
- feature_analysis.py: Reproducibility Test™
- Crime Scene templates y ROADMAP
- GitHub Actions: daily_fetch.yml (7:30 AM + 11:00 AM ET, Mon-Fri)"

# Push
git remote add origin "$REPO_URL"
git push -u origin main

echo ""
echo "✅ ¡Listo! NBA Labs subido a GitHub."
echo "🤖 GitHub Actions se activa automáticamente en el próximo horario."
