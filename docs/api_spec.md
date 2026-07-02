<div align="center">

<img src="../presentation/assets/logo.png" alt="Sanghelios" width="300">

# Especificación de la API

**FastAPI · base `http://localhost:8000` · OpenAPI interactivo en `/docs`**

[README](../README.md) · [Planteamiento](planteamiento_problema.md) · [Fuentes](fuentes_datos.md) · [Diccionario](data_dictionary.md) · [Conclusiones](conclusiones.md)

</div>

---

## Páginas (HTML)

| Ruta | Vista |
|---|---|
| `/` | Inicio (SPA: `#dashboard`, `#mapa`) |
| `/sanghelios-informe-eda` | Informe EDA editorial interactivo |
| `/donation` | Test "¿Puedo donar sangre?" |
| `/image_generation` | Estudio de campañas (asistente IA + flyers) |
| `/about` | Equipo y accesos |

## Datos (JSON)

| Método | Ruta | Descripción |
|---|---|---|
| `GET` | `/api/serie-diaria?desde&hasta` | Serie diaria con presión y `prob_escasez` del modelo |
| `GET` | `/api/stock` | Stock por grupo sanguíneo |
| `GET` | `/api/campanas` | Campañas registradas (con flyer) |
| `POST` | `/api/campanas` | Registra una campaña — body: `{comuna, titulo, fecha, tipo, estado, flyer}` |
| `GET` | `/api/meta` | τ, corte del modelo, horizonte y fecha de actualización |
| `POST` | `/api/asistente-campana` | Propuesta de publicidad (Gemini + fallback por reglas) — body: `{comuna, tipo, fecha, objetivo, tono}` |
| `GET` | `/api/flyer-templates` | Catálogo de plantillas de flyer y sus campos |
| `POST` | `/generate-flyer` | Rellena una plantilla — body: `{template, titular, mensaje, fecha, lugar, publico, nota}` → `{url}` |
| `POST` | `/generate-image` | Afiches clásicos evento/personal (form-data) → `{url, type}` |

## Flujo del asistente de campañas

```mermaid
sequenceDiagram
    participant U as Usuario
    participant A as Asistente (chat)
    participant G as Gemini 2.5
    participant F as /generate-flyer
    participant M as Mapa 3D

    U->>A: zona · grupo · fecha · objetivo
    A->>G: /api/asistente-campana
    G-->>A: titular, mensaje, canal, hashtags
    A->>F: textos sobre plantilla
    F-->>A: flyer.png
    U->>A: "Desplegar en el mapa"
    A->>M: POST /api/campanas (con flyer)
```

> Si `data/sanghelios.db` no existe, los `GET /api/*` devuelven **503** con la
> instrucción de ejecutar `scripts/build_db_and_model.py`.

---

<div align="center"><sub>Sanghelios · Hospital General de Medellín · 2026</sub></div>
