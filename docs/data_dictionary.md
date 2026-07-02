<div align="center">

<img src="../presentation/assets/logo.png" alt="Sanghelios" width="300">

# Diccionario de datos

**Variables de los datasets procesados y de la base operativa**

[README](../README.md) · [Planteamiento](planteamiento_problema.md) · [Fuentes](fuentes_datos.md) · [API](api_spec.md) · [Conclusiones](conclusiones.md)

</div>

---

## Donaciones — `data/processed/df_banco_sangre_preprocessed.csv`

26.107 filas · una por donación (2020–2025).

| Variable | Tipo | Descripción |
|---|---|---|
| `fecha_extraccion` | fecha | Día de la donación |
| `edad` | numérica | Edad del donante (18–65) |
| `imc` | numérica | Índice de masa corporal |
| `sexo` | categórica | `f` / `m` |
| `rh` | categórica | Grupo sanguíneo ABO/Rh (O+, O−, A+, …) |
| `barrio`, `comuna_o_municipio` | categórica | Ubicación del donante |
| `cobertura` | numérica | % de tipos a los que puede donar (constante por `rh`) |
| `pct_poblacion` | numérica | % de la población que puede recibirlo (constante por `rh`) |

## Series diarias — `data/processed/*_time_series.csv`

| Archivo | Columnas |
|---|---|
| `df_banco_sangre_times_series.csv` | `fecha_extraccion` · `donaciones_diarias` |
| `df_hospitalizados_time_series.csv` | `fecha_atencion` · `hospitalizaciones_diarias` |
| `df_defunciones_sangre_time_series.csv` | `fecha_defuncion` · `defunciones_diarias` |

## Base operativa — `data/sanghelios.db`

SQLite generada por `scripts/build_db_and_model.py`; es la que consume la API.

| Tabla | Contenido |
|---|---|
| `serie_diaria` | fecha, donaciones, hospitalizados, muertes_sangre, medias 7d, `presion`, `prob_escasez` (XGBoost), `escasez_pred`, `escasez_real` |
| `stock` | tipo, unidades, min_unidades (proporciones del EDA) |
| `campanas` | fecha, comuna, titulo, estado, tipo, flyer |
| `meta` | `tau` (umbral p75) · `threshold` (corte OOF F2) · `horizonte_dias` (14) · `actualizado` |

> **Variable objetivo del modelo:** `escasez_t14` = ¿la presión (demanda − oferta,
> media móvil 7d) superará el umbral τ dentro de 14 días?

---

<div align="center"><sub>Sanghelios · Hospital General de Medellín · 2026</sub></div>
