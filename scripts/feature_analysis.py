"""
NBA Labs — feature_analysis.py
Reproducibility Test™

Propósito:
    Medir si Gravity, Velocity y AirPocket son ESTABLES entre mediciones.
    Si una variable cambia > DRIFT_THRESHOLD entre medición 1 y medición 2,
    la definición es mala → hay que redefinirla antes de escalar.

Uso:
    python scripts/feature_analysis.py

Flujo:
    1. Lee trades desde nba_labs.db
    2. Para cada trade, muestra sus valores actuales (Medición 1)
    3. Pide al operador que ingrese una segunda medición manual
    4. Calcula drift absoluto y marca variables problemáticas
    5. Genera reporte en docs/reproducibility_report.md
"""

import sqlite3
import json
from pathlib import Path
from datetime import datetime

# ─── Config ────────────────────────────────────────────────────────────────────
BASE_DIR         = Path(__file__).parent.parent
DB_PATH          = BASE_DIR / "data" / "nba_labs.db"
REPORT_PATH      = BASE_DIR / "docs" / "reproducibility_report.md"

DRIFT_THRESHOLD  = 15   # puntos sobre escala 0-100. Si diff > 15 → alerta roja
WARN_THRESHOLD   = 8    # diff > 8 → alerta amarilla

VARIABLES = ["gravity", "velocity", "air_pocket"]

# ─── Colores terminal ───────────────────────────────────────────────────────────
RED    = "\033[91m"
YELLOW = "\033[93m"
GREEN  = "\033[92m"
RESET  = "\033[0m"
BOLD   = "\033[1m"

# ─── Helpers ───────────────────────────────────────────────────────────────────
def drift_label(diff: float) -> str:
    if diff > DRIFT_THRESHOLD:
        return f"{RED}🔴 DRIFT ALTO ({diff:.0f}pt){RESET}"
    elif diff > WARN_THRESHOLD:
        return f"{YELLOW}🟡 DRIFT MEDIO ({diff:.0f}pt){RESET}"
    else:
        return f"{GREEN}🟢 ESTABLE ({diff:.0f}pt){RESET}"

def load_trades() -> list[dict]:
    conn   = sqlite3.connect(DB_PATH)
    conn.row_factory = sqlite3.Row
    cur    = conn.cursor()
    cur.execute("SELECT * FROM trades ORDER BY date, trade_id")
    trades = [dict(r) for r in cur.fetchall()]
    conn.close()
    return trades

def prompt_remeasure(trade: dict) -> dict:
    """Solicita al operador la segunda medición para un trade."""
    print(f"\n{'─'*55}")
    print(f"{BOLD}Trade {trade['trade_id']} — {trade['symbol']} {trade['session']} — {trade['date']}{RESET}")
    print(f"  Régimen      : {trade['regime']}")
    print(f"  Notas        : {trade.get('notes', '')}")
    print()
    print(f"  {'Variable':<14} {'Medición 1':>12}")
    for v in VARIABLES:
        print(f"  {v:<14} {trade[v]:>12}")
    print()
    print("Ingresa la SEGUNDA medición (Enter para conservar el mismo valor):")

    second = {}
    for v in VARIABLES:
        raw = input(f"  {v} [{trade[v]}]: ").strip()
        second[v] = int(raw) if raw else trade[v]

    return second

def analyze_drift(m1: dict, m2: dict) -> list[dict]:
    results = []
    for v in VARIABLES:
        diff = abs(m1[v] - m2[v])
        results.append({
            "variable" : v,
            "m1"       : m1[v],
            "m2"       : m2[v],
            "diff"     : diff,
            "status"   : "red" if diff > DRIFT_THRESHOLD else ("yellow" if diff > WARN_THRESHOLD else "green"),
        })
    return results

def print_drift_table(drift: list[dict]):
    print()
    print(f"  {'Variable':<14} {'M1':>6} {'M2':>6} {'Diff':>6}  Estado")
    print(f"  {'─'*14} {'─'*6} {'─'*6} {'─'*6}  {'─'*20}")
    for d in drift:
        print(f"  {d['variable']:<14} {d['m1']:>6} {d['m2']:>6} {d['diff']:>6}  {drift_label(d['diff'])}")

def generate_report(all_results: list[dict]) -> str:
    lines = [
        "# NBA Labs — Reproducibility Report™",
        f"Generado: {datetime.now().strftime('%Y-%m-%d %H:%M')}",
        f"Threshold rojo: >{DRIFT_THRESHOLD}pt | Threshold amarillo: >{WARN_THRESHOLD}pt",
        "",
        "---",
        "",
    ]

    red_vars    = {}
    yellow_vars = {}

    for entry in all_results:
        tid   = entry["trade_id"]
        lines.append(f"## Trade {tid} — {entry['symbol']} {entry['session']} {entry['date']}")
        lines.append("")
        lines.append("| Variable | M1 | M2 | Diff | Estado |")
        lines.append("|---|---|---|---|---|")
        for d in entry["drift"]:
            emoji = "🔴" if d["status"] == "red" else ("🟡" if d["status"] == "yellow" else "🟢")
            lines.append(f"| {d['variable']} | {d['m1']} | {d['m2']} | {d['diff']} | {emoji} |")
            if d["status"] == "red":
                red_vars[d["variable"]] = red_vars.get(d["variable"], 0) + 1
            elif d["status"] == "yellow":
                yellow_vars[d["variable"]] = yellow_vars.get(d["variable"], 0) + 1
        lines.append("")

    lines.append("---")
    lines.append("")
    lines.append("## Resumen de Variables Problemáticas")
    lines.append("")
    if red_vars:
        lines.append("### 🔴 Drift Alto (requiere redefinición)")
        for v, count in sorted(red_vars.items(), key=lambda x: -x[1]):
            lines.append(f"- **{v}**: {count} trade(s) con drift crítico")
        lines.append("")
    if yellow_vars:
        lines.append("### 🟡 Drift Medio (vigilar)")
        for v, count in sorted(yellow_vars.items(), key=lambda x: -x[1]):
            lines.append(f"- **{v}**: {count} trade(s) con drift moderado")
        lines.append("")
    if not red_vars and not yellow_vars:
        lines.append("✅ Todas las variables son estables. Definiciones aptas para escalar.")
        lines.append("")

    lines.append("---")
    lines.append("")
    lines.append("## Decisión")
    lines.append("")
    if red_vars:
        lines.append("❌ **NO escalar a 100 trades todavía.**")
        lines.append(f"Redefinir: {', '.join(red_vars.keys())}")
    else:
        lines.append("✅ **Proceder al siguiente bloque de Crime Scenes.**")

    return "\n".join(lines)

# ─── Main ───────────────────────────────────────────────────────────────────────
def main():
    print(f"\n{BOLD}{'='*55}")
    print("  NBA Labs — Reproducibility Test™")
    print(f"{'='*55}{RESET}\n")

    trades = load_trades()
    if not trades:
        print("⚠️  No hay trades en la base de datos.")
        print(f"   Ejecuta primero: python scripts/import_csv.py")
        return

    print(f"Trades cargados: {len(trades)}")
    print("Se medirán las variables: gravity, velocity, air_pocket\n")

    all_results = []

    for trade in trades:
        m1     = {v: trade[v] for v in VARIABLES}
        m2     = prompt_remeasure(trade)
        drift  = analyze_drift(m1, m2)
        print_drift_table(drift)

        all_results.append({
            "trade_id" : trade["trade_id"],
            "symbol"   : trade["symbol"],
            "session"  : trade["session"],
            "date"     : trade["date"],
            "drift"    : drift,
        })

    # Reporte
    report = generate_report(all_results)
    REPORT_PATH.parent.mkdir(parents=True, exist_ok=True)
    REPORT_PATH.write_text(report, encoding="utf-8")

    print(f"\n{'─'*55}")
    print(f"✅  Reporte guardado en: {REPORT_PATH}")
    print(f"{'─'*55}\n")

if __name__ == "__main__":
    main()
