"""Utilidades de entrada/salida de datos compartidas por los notebooks."""

from pathlib import Path

import pandas as pd


def project_root(start: Path | None = None) -> Path:
    """Devuelve la raíz del proyecto.

    Si se ejecuta desde la carpeta ``notebooks`` sube un nivel para que las
    rutas relativas a ``data`` funcionen igual desde el notebook o desde la raíz.
    """
    root = Path(start) if start is not None else Path.cwd()
    if root.name == "notebooks":
        root = root.parent
    return root


def cargar_csvs(paths: dict[str, str], *, low_memory: bool = False) -> dict[str, pd.DataFrame]:
    """Carga un conjunto de CSVs a partir de un diccionario ``{nombre: ruta}``.

    Reemplaza el bloque ``try/except`` que se repetía en varios notebooks.
    Informa el resultado de cada carga y deja en ``None`` los que fallan.

    Returns
    -------
    dict[str, pandas.DataFrame]
        Diccionario ``{nombre: DataFrame}`` (o ``None`` si la carga falló).
    """
    dataframes: dict[str, pd.DataFrame] = {}

    for nombre, ruta in paths.items():
        print(f"Loading data from: {ruta}")
        try:
            dataframes[nombre] = pd.read_csv(ruta, low_memory=low_memory)
            print(f"'{nombre}' loaded successfully. Shape: {dataframes[nombre].shape}")
        except FileNotFoundError:
            print(f"Error: File not found → {ruta}")
            dataframes[nombre] = None
        except pd.errors.EmptyDataError:
            print("Error: The file is empty.")
            dataframes[nombre] = None
        except pd.errors.ParserError:
            print("Error: The file content could not be parsed.")
            dataframes[nombre] = None
        except PermissionError:
            print("Error: Permission denied when accessing the file.")
            dataframes[nombre] = None
        except Exception as e:  # noqa: BLE001 - se reporta cualquier error inesperado
            print(f"An unexpected error occurred: {e}")
            dataframes[nombre] = None

    return dataframes


def cargar_procesado(nombre: str, *, carpeta: str = "processed", **kwargs) -> pd.DataFrame:
    """Carga un CSV desde ``data/<carpeta>`` resolviendo la raíz del proyecto.

    Útil en los notebooks de EDA/modelado que parten de datos ya procesados.
    """
    ruta = project_root() / "data" / carpeta / nombre
    return pd.read_csv(ruta, **kwargs)
