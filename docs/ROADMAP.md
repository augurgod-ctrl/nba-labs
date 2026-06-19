# NBA Labs — Roadmap

## Filosofía de construcción

> No Data = No Edge
> El objetivo de los primeros 10 trades NO es validar el Power 5.
> Es validar que PODEMOS MEDIR el Power 5 de forma objetiva.

---

## Hitos

### Hito 1 — Crime Scenes #001–#010
- [ ] Crime Scene #001
- [ ] Crime Scene #002
- [ ] Crime Scene #003
- [ ] Crime Scene #004
- [ ] Crime Scene #005
- [ ] Crime Scene #006
- [ ] Crime Scene #007
- [ ] Crime Scene #008
- [ ] Crime Scene #009
- [ ] Crime Scene #010

**Criterio de éxito**: Reproducibility Test™ con drift < 15pt en gravity, velocity y air_pocket.

---

### Hito 2 — Schema Audit
Después de los 10 Crime Scenes:
- [ ] Revisar si alguna definición necesita ajuste
- [ ] Documentar cambios en `docs/schema_changes.md`
- [ ] Re-medir trades afectados

---

### Hito 3 — 100 Trade Dataset
Solo se llega aquí si el Schema Audit pasa.
- [ ] Importar 100 trades al CSV
- [ ] Correr `import_csv.py`
- [ ] Análisis estadístico de Power 5

---

## Lo que NO construimos todavía

- ❌ Telegram bot
- ❌ Dashboard
- ❌ TradingView Alerts
- ❌ Machine Learning
- ❌ AI

**Razón**: Sin datos validados, cualquier automatización amplifica ruido, no señal.

---

## Variables bajo vigilancia

| Variable   | Sospecha | Razón                                    |
|------------|----------|------------------------------------------|
| air_pocket | 🔴 Alta  | Definición parcialmente subjetiva        |
| gravity    | 🟢 Baja  | Matemáticamente definible (cluster density) |
| velocity   | 🟡 Media | Depende de ATR referencia elegido        |

---

## Flujo de trabajo por Crime Scene

```
1. Identificar trade en chart
2. Copiar TEMPLATE_crime_scene.md → crime_scene_XXX.md
3. Llenar Power 5 (Primera Medición)
4. Agregar fila al trades.csv
5. Correr: python scripts/import_csv.py
6. 24h después: correr python scripts/feature_analysis.py
7. Si drift OK → siguiente crime scene
8. Si drift ALTO → redefinir variable antes de continuar
```
