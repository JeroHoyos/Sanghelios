# Changelog

## 2026-07-01
- Reorganización del proyecto: `core/` → `src/`, nueva carpeta `docs/`
  (planteamiento, diccionario de datos, API, conclusiones, fuentes), `tests/unit`,
  `requirements.txt` exportado desde uv y este changelog.
- Eliminado el venv redundante `.venv-sanghelios/`; imágenes sueltas movidas a
  `src/static/img/`.

## 2026-06-30
- Modelo `escasez_t14` exportado a `models/escasez_model.pkl`; BD operativa
  `data/sanghelios.db` generada desde los CSV (script `scripts/build_db_and_model.py`).
- API de datos: `/api/serie-diaria`, `/api/stock`, `/api/campanas`, `/api/meta`.
- Dashboard conectado a datos reales (τ fijo p75) con caducidad de donaciones a 40 días.
- Estudio de campañas unificado (Campaña + Genera imágenes) con asistente IA
  (`/api/asistente-campana`, Gemini 2.5 Flash + fallback por reglas); generador de
  afiches multiplataforma (fuentes Windows/Linux/matplotlib).
- Navegación del sitio unificada (pestañas con delegación de eventos, estáticos no-cache).

## 2026-06-29
- Rework editorial del reporte EDA (`/sanghelios-informe-eda`): nota periodística,
  grafo interactivo de compatibilidad, matriz ABO/Rh, índice y conclusiones.
