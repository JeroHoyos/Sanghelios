<div align="center">

<img src="presentation/assets/logo.png" alt="Sanghelios" width="600">

**Inteligencia predictiva para bancos de sangre**

Anticipa la escasez de sangre del Hospital General de Medellín con 14 días de
anticipación y convierte esa señal en campañas de donación diseñadas con IA.

![Python](https://img.shields.io/badge/Python-3.13-1F2937?logo=python&logoColor=white)
![FastAPI](https://img.shields.io/badge/FastAPI-0.136-BF1212)
![XGBoost](https://img.shields.io/badge/XGBoost-escasez__t14-BF1212)
![Gemini](https://img.shields.io/badge/Gemini-2.5_Flash-1F2937)
![MapLibre](https://img.shields.io/badge/MapLibre-mapa_3D-1F2937)
![uv](https://img.shields.io/badge/deps-uv-4c0707)

</div>

---

## Cómo funciona

```mermaid
flowchart LR
    A[Datos abiertos<br>datos.gov.co · HGM]:::dato --> B[Notebooks<br>preprocesamiento + EDA]:::proceso
    B --> C[Modelo XGBoost<br>escasez a 14 dias]:::proceso
    C --> D[(SQLite<br>sanghelios.db)]:::dato
    D --> E[API FastAPI]:::api
    E --> F[Dashboard<br>presion vs umbral]:::producto
    E --> G[Mapa 3D<br>campanas y demanda]:::producto
    E --> H[Estudio de campanas<br>asistente IA + flyers]:::producto

    classDef dato fill:#F6EFE4,stroke:#BF1212,color:#1a1714
    classDef proceso fill:#ffffff,stroke:#8a837a,color:#1a1714
    classDef api fill:#1F2937,stroke:#1F2937,color:#ffffff
    classDef producto fill:#BF1212,stroke:#BF1212,color:#ffffff
```

La **presión** del sistema (demanda − oferta, media móvil de 7 días) se compara
contra un umbral τ. El modelo predice si habrá escasez dentro de 14 días; cuando
la señal se enciende, el asistente de IA diseña la campaña, genera el flyer y la
despliega en el mapa.

## Módulos

| Módulo | Qué hace |
|---|---|
| **Dashboard** | Stock vigente (caducidad 40 días), autonomía, presión vs τ y riesgo del modelo, con ventanas didácticas interactivas por indicador |
| **Mapa 3D** | Campañas vigentes de los últimos 7 días con su flyer, origen de hospitalizados y el HGM como nodo central, con capas activables |
| **Estudio de campañas** | Asistente conversacional: zona, lugar exacto (resuelve descripciones informales al lugar real con su dirección), uno o varios grupos prioritarios, propuesta con Gemini y flyer con foto opcional, editable en vivo |
| **Flyer personal** | Pieza para ayudar a una persona concreta: nombre, foto, tipo de sangre y los grupos compatibles que pueden donarle |
| **¿Puedo donar?** | Test de aptitud con mensajes para compartir y puntos de donación cercanos |
| **Informe EDA** | Reporte editorial interactivo de 26.107 donaciones (2020–2025) |

## Datos abiertos

Tres conjuntos publicados por el Hospital General de Medellín en
[datos.gov.co](https://www.datos.gov.co):

| Conjunto | Registros | Rol en el sistema |
|---|--:|---|
| [Banco de sangre](https://www.datos.gov.co/Salud-y-Protecci-n-Social/Banco-de-sangre-Hospital-General-de-Medell-n/65is-zhxx/about_data) | 35.840 | Oferta: 26.107 donaciones válidas (2020–2025) tras limpieza |
| [Población atendida](https://www.datos.gov.co/Salud-y-Protecci-n-Social/Poblaci-n-atendida-en-el-Hospital-General-de-Medel/xm8g-qeac/about_data) | 221.203 | Demanda: hospitalizaciones diarias |
| [Defunciones](https://www.datos.gov.co/Salud-y-Protecci-n-Social/Defunciones-ocurridas-en-en-el-Hospital-General-de/hwwv-mhse/about_data) | 5.094 | Demanda: muertes con causa asociada a sangre |

## Hallazgos que guían el producto

> **El riesgo no es la rareza sino la estructura.** El O− dona a los 8 tipos pero
> es solo el 9 % de los donantes: se vigila aparte del volumen total. Diciembre es
> el mes más crítico, así que las campañas se activan en noviembre. Y como la edad
> es lo único que separa a los donantes, se segmenta por canal, no por mensaje.

## Ejecutar

```bash
uv sync                                       # dependencias
uv run python scripts/build_db_and_model.py   # (una vez) modelo + base de datos
uv run uvicorn src.app:app --port 8000        # http://localhost:8000
```

Variables de entorno en `.env` (no versionado): `GEMINI_API_KEY` para el
asistente de campañas y la búsqueda de lugares.

## Estructura

```
Sanghelios/
├── src/            aplicación web (FastAPI + Jinja2 + JS)
│   ├── app.py          rutas HTML y /api/*
│   ├── campaign_ai.py  asistente de campañas y búsqueda de lugares (Gemini + reglas)
│   └── tools/          relleno de plantillas de flyers (PIL)
├── notebooks/      1_preprocessing → 2_eda → 3_modeling
├── scripts/        build_db_and_model.py (entrena y puebla la BD)
├── data/           raw · processed · sanghelios.db
├── models/         escasez_model.pkl
├── docs/           planteamiento · diccionario · API · conclusiones
├── tests/          pruebas unitarias
└── presentation/   diapositivas Manim
```

Documentación ampliada en [`docs/`](docs/) — [API](docs/api_spec.md) ·
[Diccionario de datos](docs/data_dictionary.md) · [Conclusiones](docs/conclusiones.md).

## Equipo

| | Rol | Formación |
|---|---|---|
| **Jerónimo Hoyos** | Ingeniero en IA | Ing. de Sistemas e Informática · UNAL Medellín |
| **Daniel Arango** | Ingeniero de Software | Ing. de Sistemas · EAFIT |
| **Jose Miguel García** | Data Scientist | Estadística · UNAL Medellín |
| **Valentina Muñoz** | Diseñadora | Ing. Administrativa · UNAL Medellín |

<div align="center">
<sub>Hospital General de Medellín · Banco de sangre · 2026</sub>
</div>
