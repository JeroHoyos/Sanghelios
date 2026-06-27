"""Exploración y estandarización de DataFrames."""

import re
import unicodedata

import pandas as pd


def explorar_df(df, nombre):
    """Imprime un resumen rápido del DataFrame: forma, duplicados y por columna
    su dtype, subniveles (si es categórica), nulos y tres ejemplos."""
    from IPython.display import display

    dupes = df.duplicated().sum()
    print(f"\n {nombre}  —  {df.shape[0]:,} filas × {df.shape[1]} columnas")
    print(f" Duplicados  {dupes:,} ({dupes/len(df)*100:.1f}%)")

    categoricas = df.select_dtypes(include="object").columns

    info = pd.DataFrame(
        {
            "dtype":      df.dtypes.astype(str),
            "subniveles": df.apply(lambda col: col.nunique() if col.name in categoricas else ""),
            "nulos":      df.isna().sum(),
            "% nulos":    (df.isna().mean() * 100).round(1),
            **{f"ej {i+1}": df.iloc[i] for i in range(min(3, len(df)))},
        }
    )
    display(info)


def estandarizar_columnas(df):
    """Normaliza los nombres de columnas a snake_case ascii e informa los cambios."""
    def limpiar(col):
        col = unicodedata.normalize("NFKD", col)
        col = col.encode("ascii", "ignore").decode()
        col = col.strip().lower()
        col = re.sub(r"[^a-z0-9\s]", " ", col)
        col = re.sub(r"\s+", "_", col).strip("_")
        return col

    nuevos = {col: limpiar(col) for col in df.columns}
    for viejo, nuevo in nuevos.items():
        if viejo != nuevo:
            print(f"  {viejo!r:35} → {nuevo!r}")

    return df.rename(columns=nuevos)


def estandarizar_etiquetas(etiqueta):
    """Normaliza una etiqueta categórica a minúsculas con ``_`` como separador."""
    if pd.isna(etiqueta):
        return etiqueta
    return (
        str(etiqueta)
        .strip()
        .lower()
        .replace("-", "_")
        .replace("/", "_")
        .replace(" ", "_")
    )
