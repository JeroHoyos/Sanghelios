<div align="center">

<img src="../presentation/assets/logo.png" alt="Sanghelios" width="300">

# Fuentes de datos

**Datos abiertos de datos.gov.co · Hospital General de Medellín**

[README](../README.md) · [Planteamiento](planteamiento_problema.md) · [Diccionario](data_dictionary.md) · [API](api_spec.md) · [Conclusiones](conclusiones.md)

</div>

---

## Datasets principales

| Dataset | Uso en el proyecto | Enlace |
|---|---|---|
| **Banco de sangre — HGM** | Donaciones 2020–2025 (fuente primaria del EDA y el modelo) | [datos.gov.co](https://www.datos.gov.co/Salud-y-Protecci-n-Social/Banco-de-sangre-Hospital-General-de-Medell-n/65is-zhxx/about_data) |
| **Población atendida — HGM** | Serie de hospitalizaciones (componente de demanda) | [datos.gov.co](https://www.datos.gov.co/Salud-y-Protecci-n-Social/Poblaci-n-atendida-en-el-Hospital-General-de-Medel/xm8g-qeac/about_data) |
| **Defunciones — HGM** | Muertes con causa asociada a sangre (componente de demanda) | [datos.gov.co](https://www.datos.gov.co/Salud-y-Protecci-n-Social/Defunciones-ocurridas-en-en-el-Hospital-General-de/hwwv-mhse/about_data) |

Los archivos crudos se guardan como
`data/raw/{banco_sangre, atenciones, defunciones}.csv`.

## Datasets de respaldo

Alternativas por año, disponibles si se requiere ampliar la cobertura:

| Dataset | Enlace |
|---|---|
| Población atendida (variante) | [datos.gov.co](https://www.datos.gov.co/dataset/Poblaci-n-atendida-en-el-Hospital-General-de-Medel/8xgb-m35u/about_data) |
| Defunciones HGM 2020 | [datos.gov.co](https://www.datos.gov.co/dataset/Defunciones-Hospital-General-de-Medell-n-2020/mden-2y89/about_data) |
| Población atendida HGM 2020 | [datos.gov.co](https://www.datos.gov.co/dataset/Poblaci-n-atendida-Hospital-General-de-Medell-n-20/qf6g-w9zn/about_data) |
| Población atendida HGM 2021 | [datos.gov.co](https://www.datos.gov.co/dataset/Poblaci-n-atendida-Hospital-General-de-Medell-n-20/2siy-h4f4/about_data) |
| Defunciones (variante) | [datos.gov.co](https://www.datos.gov.co/dataset/Defunciones-Ocurridas-en-el-Hospital-General-de-Me/gvai-eq3s/about_data) |
| Defunciones ene–ago 2021 | [datos.gov.co](https://www.datos.gov.co/dataset/Defunciones-Hospital-General-de-Medell-n-enero-a-a/kti7-ze8k/about_data) |

---

<div align="center"><sub>Sanghelios · Hospital General de Medellín · 2026</sub></div>
