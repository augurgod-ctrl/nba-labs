#!/bin/bash
# NBA Labs — GitHub Push
# Doble clic para ejecutar

REPO_URL="https://github.com/augurgod-ctrl/nba-labs.git"
SCRIPT_DIR="$(cd "$(dirname "$0")" && pwd)"

cd "$SCRIPT_DIR"
echo "📁 Carpeta: $SCRIPT_DIR"
echo ""

# Limpiar git del sandbox (si existe)
rm -rf .git

# Inicializar
git init
git branch -M main
git config user.name "Carlos"
git config user.email "augurgod@gmail.com"

# Agregar todo
git add -A

# Commit
git commit -m "🔬 NBA Labs v1.0 — Power 5 research system for US30"

# Remote + Push
git remote add origin "$REPO_URL"
git push -u origin main

echo ""
echo "✅ ¡Subido! https://github.com/augurgod-ctrl/nba-labs"
echo ""
read -p "Presiona Enter para cerrar..."
