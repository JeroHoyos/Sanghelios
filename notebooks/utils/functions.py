"""Módulo de compatibilidad.

El contenido se reorganizó en módulos enfocados:
- :mod:`utils.exploracion` — explorar_df, estandarizar_columnas, estandarizar_etiquetas
- :mod:`utils.plots`       — set_plot_style, boxplot_pro, distribucion_numericas, estilo global
- :mod:`utils.input_output` — cargar_csvs, project_root, cargar_procesado

Se mantiene este archivo para que ``from utils.functions import *`` siga funcionando.
"""

from .exploracion import (
    explorar_df,
    estandarizar_columnas,
    estandarizar_etiquetas,
)
from .plots import (
    set_plot_style,
    boxplot_pro,
    distribucion_numericas,
)

__all__ = [
    "explorar_df",
    "estandarizar_columnas",
    "estandarizar_etiquetas",
    "set_plot_style",
    "boxplot_pro",
    "distribucion_numericas",
]
