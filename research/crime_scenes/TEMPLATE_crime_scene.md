# Crime Scene #XXX — [SYMBOL] [SESSION] [DATE]

> **Objetivo**: Documentar un trade de forma reproducible.
> Si otro operador lee esto y llega a los mismos valores de Power 5, la definición es válida.

---

## 1. Identificación

| Campo       | Valor          |
|-------------|----------------|
| Trade ID    | XXX            |
| Fecha       | YYYY-MM-DD     |
| Símbolo     | US30 / NAS100  |
| Sesión      | NY / LON / ASIA|
| Régimen     | 1 / 2 / 3 / 4 / 5 |

---

## 2. Power 5 — Primera Medición

### 2.1 Gravity (0–100)
> ¿Cuánta estructura de precio está atrayendo el trade hacia un nivel clave?

**Niveles identificados:**
- PDH: ___
- Asian High/Low: ___
- Weekly High/Low: ___
- Monthly Open: ___

**Cluster density**: ___ niveles en ≤ ___ puntos de rango

**Gravity Score**: ___

**Razonamiento:**
> _Explicar por qué se asignó este número_

---

### 2.2 Velocity (0–100)
> ¿Con qué fuerza/rapidez se movió el precio hacia el setup?

**Candles previas al entry (últimas 3):**
| Candle | Tamaño (pts) | Dirección | Body % |
|--------|-------------|-----------|--------|
| -3     |             |           |        |
| -2     |             |           |        |
| -1     |             |           |        |

**ATR referencia**: ___ pts
**Momentum relativo**: ___ % del ATR en las últimas N candles

**Velocity Score**: ___

**Razonamiento:**
> _Explicar por qué se asignó este número_

---

### 2.3 HTF Bias (1 / 0 / -1)
> Dirección del bias en timeframe mayor (H4 / Daily)

**Estructura H4**: Alcista / Bajista / Lateral
**Estructura Daily**: Alcista / Bajista / Lateral

**HTF Bias**: `1` (alcista) / `0` (neutral) / `-1` (bajista)

---

### 2.4 Air Pocket (0–100)
> ¿Cuánto espacio libre tiene el precio para moverse sin obstrucciones?

**Niveles de resistencia/soporte entre entry y target:**
- Nivel 1: ___ (a ___ pts del entry)
- Nivel 2: ___ (a ___ pts del entry)

**Espacio libre hasta primer obstáculo**: ___ pts
**Espacio total hasta target**: ___ pts
**Ratio espacio libre / total**: ___ %

**Air Pocket Score**: ___

**Razonamiento:**
> _Explicar por qué se asignó este número_
> ⚠️ NOTA: Esta es la variable más subjetiva. Ser muy explícito.

---

### 2.5 Régimen (1–5)
> Condición de mercado general

| Régimen | Descripción                              |
|---------|------------------------------------------|
| 1       | Tendencia fuerte clara                   |
| 2       | Tendencia moderada                       |
| 3       | Rango con dirección sesgada              |
| 4       | Rango sin dirección clara                |
| 5       | Chop / alta incertidumbre               |

**Régimen asignado**: ___

---

## 3. Entry & Resultado

| Campo          | Valor    |
|----------------|----------|
| Entry Price    |          |
| Stop Loss      |          |
| Target         |          |
| MAE (pts)      |          |
| MFE (pts)      |          |
| Resultado (R)  |          |

---

## 4. Screenshot

> Adjuntar imagen en `research/screenshots/crime_scene_XXX.png`

![Crime Scene XXX](../screenshots/crime_scene_XXX.png)

---

## 5. Reproducibility Check

> Completar DESPUÉS de hacer la segunda medición con `feature_analysis.py`

| Variable   | M1  | M2  | Diff | Estado |
|------------|-----|-----|------|--------|
| gravity    |     |     |      | 🟢/🟡/🔴 |
| velocity   |     |     |      | 🟢/🟡/🔴 |
| air_pocket |     |     |      | 🟢/🟡/🔴 |

**¿Definición válida?** Sí / No

**Si No → ¿Qué cambiar?**
> _Notas sobre redefinición_

---

## 6. Lecciones

> Una o dos líneas máximo. ¿Qué aprendiste sobre la MEDICIÓN, no sobre el trade?

1.
2.
