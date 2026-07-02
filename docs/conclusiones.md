<div align="center">

<img src="../presentation/assets/logo.png" alt="Sanghelios" width="300">

# Conclusiones

**Hallazgos, límites del modelo y ruta de mejora**

[README](../README.md) · [Planteamiento](planteamiento_problema.md) · [Fuentes](fuentes_datos.md) · [Diccionario](data_dictionary.md) · [API](api_spec.md)

</div>

---

## Hallazgos del análisis

| Hallazgo | Implicación operativa |
|---|---|
| **El riesgo no es la rareza sino la estructura**: el O− (donante universal) dona a los 8 tipos pero es solo el 9 % de los donantes; el AB, aunque escaso, es receptor universal | Monitorear O− y AB− con alertas propias, independientes del volumen total |
| **Estacionalidad marcada**: diciembre es el mes más crítico y enero el más alto | Activar campañas en **noviembre**, no cuando ya falta la sangre |
| **La edad es el único eje de segmentación** (K-Prototypes, k=3): RH, IMC y comuna salen casi idénticos entre grupos | Cambiar el **canal** por grupo etario (redes/universidades 18–32, empresas 32–47, llamadas 47–65), no el mensaje |
| Concentración geográfica en pocos puntos (Robledo, Bello) | Oportunidad en comunas subrepresentadas frente a su población |

## Modelo `escasez_t14`

XGBoost con 50 features (presión y sus rezagos, medias móviles, estacionalidad
cíclica), validación temporal y umbral out-of-fold optimizado con F2 (prioriza
recall: perder una alerta cuesta más que una falsa alarma).

> Desempeño **modesto pero honesto**: tres series diarias limitan el techo de la
> señal; el calendario de festivos aporta poco como exógena.

## Limitaciones

- Hueco de datos enero–mayo 2024 imputado; 2023 con registros muy bajos.
- Sin variables exógenas ricas (clima, eventos masivos, epidemiología INS).
- El stock por tipo se estima con proporciones del EDA, no con inventario FIFO real.

## Próximos pasos

1. Integrar fuentes exógenas (accidentalidad, INS) para mejorar el ranking del modelo.
2. Inventario real entrada−salida con caducidad de 40 días por unidad.
3. Reentrenamiento programado (`scripts/build_db_and_model.py` como tarea recurrente).

---

<div align="center"><sub>Sanghelios · Hospital General de Medellín · 2026</sub></div>
