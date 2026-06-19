"""
NBA Labs — fetch_us30.py
Descarga datos de US30 (Dow Jones Futures YM=F) y detecta setups del NY Open.
Calcula Power 5: Gravity, Velocity, HTF Bias, Air Pocket, Regime.

Requisito: pip install yfinance pandas openpyxl

Uso:
    python scripts/fetch_us30.py              # Últimos 5 días
    python scripts/fetch_us30.py --days 10    # Últimos 10 días
"""

import argparse
import csv
import json
from datetime import datetime, timedelta
from pathlib import Path
from zoneinfo import ZoneInfo

import pandas as pd
import yfinance as yf

# ─── Config ────────────────────────────────────────────────────────────────────
BASE_DIR   = Path(__file__).parent.parent
CSV_PATH   = BASE_DIR / "data" / "trades.csv"
SCENE_DIR  = BASE_DIR / "research" / "crime_scenes"
ET         = ZoneInfo("America/New_York")

NY_OPEN_HOUR   = 9
NY_OPEN_MINUTE = 30
NY_WINDOW_MINS = 90  # analizar 90 min tras el open

# Power 5 thresholds
GRAVITY_CLUSTER_PTS   = 50   # puntos: si 2+ niveles en este rango → cluster
VELOCITY_ATR_PERIODS  = 14
AIR_POCKET_LOOKFORWARD= 10   # velas adelante para calcular espacio libre

# ─── Descargar datos ────────────────────────────────────────────────────────────
def fetch_data(days: int = 5) -> tuple[pd.DataFrame, pd.DataFrame]:
    """Retorna (df_5min, df_daily) para YM=F (Dow Jones Futures)."""
    ticker = yf.Ticker("YM=F")

    df_5m = ticker.history(period=f"{days}d", interval="5m")
    df_5m.index = pd.to_datetime(df_5m.index).tz_convert(ET)

    df_daily = ticker.history(period="60d", interval="1d")
    df_daily.index = pd.to_datetime(df_daily.index).tz_localize("UTC").tz_convert(ET) \
        if df_daily.index.tzinfo is None else pd.to_datetime(df_daily.index).tz_convert(ET)

    print(f"✅ Datos descargados: {len(df_5m)} velas 5min | {len(df_daily)} días")
    return df_5m, df_daily

# ─── Calcular ATR ───────────────────────────────────────────────────────────────
def atr(df: pd.DataFrame, n: int = 14) -> pd.Series:
    hl  = df["High"] - df["Low"]
    hcp = (df["High"] - df["Close"].shift()).abs()
    lcp = (df["Low"]  - df["Close"].shift()).abs()
    tr  = pd.concat([hl, hcp, lcp], axis=1).max(axis=1)
    return tr.rolling(n).mean()

# ─── GRAVITY ───────────────────────────────────────────────────────────────────
def calc_gravity(df_daily: pd.DataFrame, entry_date: datetime) -> tuple[int, dict]:
    """Cluster density de niveles clave alrededor del precio de apertura."""
    day_df = df_daily[df_daily.index.date < entry_date.date()]
    if len(day_df) < 2:
        return 50, {}

    prev_day  = day_df.iloc[-1]
    week_ago  = day_df.iloc[max(-5, -len(day_df)):]

    pdh = prev_day["High"]
    pdl = prev_day["Low"]
    asian_h = day_df.iloc[-1]["High"]   # aproximación: high del día anterior como proxy Asian
    asian_l = day_df.iloc[-1]["Low"]
    weekly_h = week_ago["High"].max()
    weekly_l = week_ago["Low"].min()

    levels = {
        "PDH": pdh, "PDL": pdl,
        "Asian_H": asian_h, "Asian_L": asian_l,
        "Weekly_H": weekly_h, "Weekly_L": weekly_l,
    }

    ref_price = prev_day["Close"]
    # Contar cuántos niveles están dentro de GRAVITY_CLUSTER_PTS del precio de referencia
    close_levels = [v for v in levels.values() if abs(v - ref_price) <= GRAVITY_CLUSTER_PTS]
    cluster_density = len(close_levels)

    # Score: 0–100 basado en densidad (máx 6 niveles = 100)
    gravity_score = min(100, int((cluster_density / 6) * 100))
    # Bonus si hay stack triple (PDH + Asian + Weekly en cluster)
    if cluster_density >= 3:
        gravity_score = min(100, gravity_score + 20)

    return gravity_score, levels

# ─── VELOCITY ──────────────────────────────────────────────────────────────────
def calc_velocity(df_5m: pd.DataFrame, entry_idx: int) -> int:
    """Momentum de las 3 velas previas relativo al ATR."""
    if entry_idx < VELOCITY_ATR_PERIODS + 3:
        return 50

    window    = df_5m.iloc[max(0, entry_idx-20):entry_idx]
    atr_val   = atr(window).iloc[-1]
    last3     = df_5m.iloc[entry_idx-3:entry_idx]

    if atr_val == 0:
        return 50

    moves = (last3["Close"] - last3["Open"]).abs()
    avg_move = moves.mean()
    ratio = avg_move / atr_val   # >1 = velas más grandes que ATR promedio

    score = min(100, int(ratio * 60))
    # Bonus si todas van en la misma dirección
    directions = (last3["Close"] - last3["Open"]) > 0
    if directions.all() or (~directions).all():
        score = min(100, score + 20)

    return score

# ─── HTF BIAS ──────────────────────────────────────────────────────────────────
def calc_htf_bias(df_daily: pd.DataFrame, entry_date: datetime) -> int:
    """1 = alcista, -1 = bajista, 0 = neutral. Basado en estructura diaria."""
    past = df_daily[df_daily.index.date < entry_date.date()].tail(10)
    if len(past) < 4:
        return 0

    highs  = past["High"].values
    lows   = past["Low"].values

    hh = highs[-1] > highs[-3]    # Higher High
    hl = lows[-1]  > lows[-3]     # Higher Low
    lh = highs[-1] < highs[-3]    # Lower High
    ll = lows[-1]  < lows[-3]     # Lower Low

    if hh and hl:
        return 1
    elif lh and ll:
        return -1
    return 0

# ─── AIR POCKET ────────────────────────────────────────────────────────────────
def calc_air_pocket(df_5m: pd.DataFrame, entry_idx: int) -> int:
    """Espacio libre: ausencia de consolidación en las velas siguientes."""
    forward = df_5m.iloc[entry_idx:entry_idx + AIR_POCKET_LOOKFORWARD]
    if len(forward) < 3:
        return 50

    # Medir cuerpos de velas (cuerpo pequeño = obstáculo/consolidación)
    body_sizes = (forward["Close"] - forward["Open"]).abs()
    hl_sizes   = forward["High"] - forward["Low"]

    body_ratio = (body_sizes / hl_sizes.replace(0, 1)).mean()
    # body_ratio alto = velas con cuerpo grande = momentum limpio = air pocket alto
    score = min(100, int(body_ratio * 100))
    return score

# ─── REGIME ────────────────────────────────────────────────────────────────────
def calc_regime(df_daily: pd.DataFrame, entry_date: datetime) -> int:
    """1–5: Tendencia fuerte → Chop."""
    past = df_daily[df_daily.index.date < entry_date.date()].tail(20)
    if len(past) < 5:
        return 3

    closes    = past["Close"]
    direction = closes.iloc[-1] - closes.iloc[0]
    volatility= closes.std() / closes.mean()

    if abs(direction) > closes.std() * 2:
        return 1 if direction > 0 else 1
    elif abs(direction) > closes.std():
        return 2
    elif volatility < 0.005:
        return 4
    elif volatility > 0.015:
        return 5
    return 3

# ─── DETECTAR NY OPEN SETUPS ───────────────────────────────────────────────────
def find_ny_open_setups(df_5m: pd.DataFrame, df_daily: pd.DataFrame) -> list[dict]:
    setups = []
    dates  = df_5m.index.date
    unique_dates = sorted(set(dates))

    for trade_date in unique_dates:
        day_mask = dates == trade_date
        day_5m   = df_5m[day_mask]

        # Encontrar vela del NY Open (9:30 ET)
        open_candles = day_5m[
            (day_5m.index.hour == NY_OPEN_HOUR) &
            (day_5m.index.minute == NY_OPEN_MINUTE)
        ]
        if open_candles.empty:
            continue

        entry_time = open_candles.index[0]
        entry_idx  = df_5m.index.get_loc(entry_time)
        entry_price= open_candles.iloc[0]["Open"]

        # Power 5
        gravity,  levels = calc_gravity(df_daily, entry_time)
        velocity          = calc_velocity(df_5m, entry_idx)
        htf_bias          = calc_htf_bias(df_daily, entry_time)
        air_pocket        = calc_air_pocket(df_5m, entry_idx)
        regime            = calc_regime(df_daily, entry_time)

        # MAE / MFE en las siguientes 12 velas (1 hora)
        future = df_5m.iloc[entry_idx:entry_idx+12]
        mae    = round(abs(future["Low"].min()  - entry_price), 1)
        mfe    = round(abs(future["High"].max() - entry_price), 1)

        setups.append({
            "date"       : trade_date.isoformat(),
            "entry_time" : entry_time.strftime("%H:%M ET"),
            "symbol"     : "US30",
            "session"    : "NY",
            "entry_price": round(entry_price, 0),
            "regime"     : regime,
            "gravity"    : gravity,
            "velocity"   : velocity,
            "htf_bias"   : htf_bias,
            "air_pocket" : air_pocket,
            "mae"        : mae,
            "mfe"        : mfe,
            "levels"     : levels,
        })

    return setups

# ─── EXPORTAR A CSV ─────────────────────────────────────────────────────────────
def export_to_csv(setups: list[dict], max_trades: int = 3):
    existing = []
    if CSV_PATH.exists():
        with open(CSV_PATH, newline="") as f:
            existing = list(csv.DictReader(f))

    existing_ids = {r["trade_id"] for r in existing}
    next_id = max((int(r["trade_id"]) for r in existing if r["trade_id"].isdigit()), default=0) + 1

    new_rows = []
    for i, s in enumerate(setups[:max_trades]):
        tid = f"{next_id + i:03d}"
        if tid in existing_ids:
            continue
        new_rows.append({
            "trade_id"  : tid,
            "date"      : s["date"],
            "symbol"    : s["symbol"],
            "session"   : s["session"],
            "regime"    : s["regime"],
            "gravity"   : s["gravity"],
            "velocity"  : s["velocity"],
            "htf_bias"  : s["htf_bias"],
            "air_pocket": s["air_pocket"],
            "mae"       : s["mae"],
            "mfe"       : s["mfe"],
            "result_r"  : "",
            "notes"     : f"Crime Scene #{tid} - NY Open auto",
        })

    all_rows = existing + new_rows
    fieldnames = ["trade_id","date","symbol","session","regime","gravity","velocity",
                  "htf_bias","air_pocket","mae","mfe","result_r","notes"]
    with open(CSV_PATH, "w", newline="") as f:
        w = csv.DictWriter(f, fieldnames=fieldnames)
        w.writeheader()
        w.writerows(all_rows)

    print(f"\n✅ {len(new_rows)} trade(s) nuevos agregados a {CSV_PATH}")
    return new_rows

# ─── GENERAR CRIME SCENES ───────────────────────────────────────────────────────
TEMPLATE = Path(__file__).parent.parent / "research" / "crime_scenes" / "TEMPLATE_crime_scene.md"

def generate_crime_scenes(setups: list[dict], new_rows: list[dict]):
    scene_ids = {r["trade_id"]: s for r, s in zip(new_rows, setups)}

    for row in new_rows:
        tid = row["trade_id"]
        s   = setups[list({r["trade_id"] for r in new_rows}).index(tid)] if tid in scene_ids else None
        if not s:
            continue

        out = SCENE_DIR / f"crime_scene_{tid}.md"
        lvl = s.get("levels", {})

        content = f"""# Crime Scene #{tid} — {s["symbol"]} {s["session"]} {s["date"]}

> **Auto-generado por fetch_us30.py — verificar en chart antes de usar**

---

## 1. Identificación

| Campo       | Valor          |
|-------------|----------------|
| Trade ID    | {tid}          |
| Fecha       | {s["date"]}    |
| Símbolo     | US30           |
| Sesión      | NY             |
| Entry Time  | {s["entry_time"]} |
| Entry Price | {s["entry_price"]} |
| Régimen     | {s["regime"]}  |

---

## 2. Power 5 — Medición Automática (M1)

### Gravity Score: {s["gravity"]}
Niveles identificados:
- PDH: {lvl.get("PDH", "N/A"):.0f}
- PDL: {lvl.get("PDL", "N/A"):.0f}
- Asian High: {lvl.get("Asian_H", "N/A"):.0f}
- Asian Low: {lvl.get("Asian_L", "N/A"):.0f}
- Weekly High: {lvl.get("Weekly_H", "N/A"):.0f}
- Weekly Low: {lvl.get("Weekly_L", "N/A"):.0f}

### Velocity Score: {s["velocity"]}
Basado en momentum de 3 velas 5min previas al open vs ATR(14).

### HTF Bias: {s["htf_bias"]} (1=alcista | 0=neutral | -1=bajista)
Estructura diaria de los últimos 10 días.

### Air Pocket Score: {s["air_pocket"]}
Body ratio de las siguientes 10 velas 5min (auto-calculado).

---

## 3. Entry & Resultado

| Campo          | Valor    |
|----------------|----------|
| Entry Price    | {s["entry_price"]} |
| Stop Loss      | ⚠️ Completar manualmente |
| Target         | ⚠️ Completar manualmente |
| MAE (pts)      | {s["mae"]} |
| MFE (pts)      | {s["mfe"]} |
| Resultado (R)  | ⚠️ Completar manualmente |

---

## 4. Screenshot

> Agregar captura en `research/screenshots/crime_scene_{tid}.png`

---

## 5. Reproducibility Check

| Variable   | M1  | M2  | Diff | Estado |
|------------|-----|-----|------|--------|
| gravity    | {s["gravity"]} |     |      |        |
| velocity   | {s["velocity"]} |     |      |        |
| air_pocket | {s["air_pocket"]} |     |      |        |

---

## 6. Lecciones

> Completar después de la segunda medición.

1.
2.
"""
        out.write_text(content, encoding="utf-8")
        print(f"  📄 {out.name}")

# ─── Main ───────────────────────────────────────────────────────────────────────
def main():
    parser = argparse.ArgumentParser()
    parser.add_argument("--days",   type=int, default=5,  help="Días de historia")
    parser.add_argument("--trades", type=int, default=3,  help="Máx trades a procesar")
    args = parser.parse_args()

    print(f"\n{'='*55}")
    print("  NBA Labs — US30 NY Open Fetcher")
    print(f"{'='*55}\n")

    df_5m, df_daily = fetch_data(args.days)
    setups = find_ny_open_setups(df_5m, df_daily)

    print(f"\nSetups encontrados: {len(setups)}")
    for i, s in enumerate(setups[:args.trades]):
        print(f"  [{i+1}] {s['date']} | G:{s['gravity']} V:{s['velocity']} "
              f"HTF:{s['htf_bias']} AP:{s['air_pocket']} R:{s['regime']} "
              f"| MAE:{s['mae']} MFE:{s['mfe']}")

    new_rows = export_to_csv(setups, max_trades=args.trades)

    print("\nGenerando Crime Scenes...")
    generate_crime_scenes(setups, new_rows)

    print(f"\n{'─'*55}")
    print("Siguiente paso: python scripts/import_csv.py")
    print(f"{'─'*55}\n")

if __name__ == "__main__":
    main()
