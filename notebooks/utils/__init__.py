"""Utilidades compartidas por los notebooks de Sanghelios.

Permite ``from utils import *`` para acceder a todo el API público:
carga de datos, exploración, estilo de gráficas y diccionarios de dominio.
"""

from .input_output import cargar_csvs, project_root, cargar_procesado
from .exploracion import (
    explorar_df,
    estandarizar_columnas,
    estandarizar_etiquetas,
)
from .plots import (
    PALETA,
    MESES,
    C_SEXO,
    C_CLUSTER,
    aplicar_estilo_global,
    style_axes,
    label_bars,
    set_plot_style,
    boxplot_pro,
    distribucion_numericas,
)
from .barrios import get_comuna
from .defunciones import (
    CAUSA_DIRECTA_SANGRE,
    CAUSA_ANTECEDENTES_B_SANGRE,
    CAUSA_ANTECEDENTES_C_SANGRE,
    CAUSA_ANTECEDENTES_D_SANGRE,
    ESTADOS_PATOLOGICOS_SANGRE,
)

__all__ = [
    # io
    "cargar_csvs", "project_root", "cargar_procesado",
    # exploracion
    "explorar_df", "estandarizar_columnas", "estandarizar_etiquetas",
    # plots
    "PALETA", "MESES", "C_SEXO", "C_CLUSTER",
    "aplicar_estilo_global", "style_axes", "label_bars",
    "set_plot_style", "boxplot_pro", "distribucion_numericas",
    # dominio
    "get_comuna",
    "CAUSA_DIRECTA_SANGRE", "CAUSA_ANTECEDENTES_B_SANGRE",
    "CAUSA_ANTECEDENTES_C_SANGRE", "CAUSA_ANTECEDENTES_D_SANGRE",
    "ESTADOS_PATOLOGICOS_SANGRE",
]
