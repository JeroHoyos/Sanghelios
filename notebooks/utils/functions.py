import pandas as pd
import matplotlib.pyplot as plt
import seaborn as sns
import unicodedata
import re
from IPython.display import display

def explorar_df(df, nombre):
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

def distribucion_numericas(df, columnas, cols=3, ancho=6, alto=4,
                           titulo="Distribución de Variables Numéricas",
                           modo="ambos"):
    """
    modo: "ambos"      -> histograma + boxplot
          "histograma" -> solo histograma
          "boxplot"    -> solo boxplot
    """
    color = "#5b7fa6"
    n_rows = -(-len(columnas) // cols)

    filas_por_var  = 2 if modo == "ambos" else 1
    height_ratios  = ([3, 1] * n_rows) if modo == "ambos" else ([1] * n_rows)

    fig, axes = plt.subplots(
        n_rows * filas_por_var, cols,
        figsize=(cols * ancho, n_rows * alto),
        gridspec_kw={"height_ratios": height_ratios},
        squeeze=False
    )

    for i, col in enumerate(columnas):
        fila    = (i // cols) * filas_por_var
        col_idx = i % cols

        # Rango con margen
        rango  = df[col].max() - df[col].min()
        margen = rango * 0.05
        xlim   = (df[col].min() - margen, df[col].max() + margen)

        media, std, mediana = df[col].mean(), df[col].std(), df[col].median()

        # ── Histograma ──────────────────────────────────────────────────
        if modo in ("ambos", "histograma"):
            ax_hist = axes[fila, col_idx]
            sns.histplot(df[col], kde=True, ax=ax_hist, color=color,
                         alpha=0.6, edgecolor="white", linewidth=0.5)
            ax_hist.set(xlabel="", ylabel="", xlim=xlim)
            ax_hist.set_title(f"{col}\n$\\mu$={media:.1f}  $\\sigma$={std:.1f}",
                              fontsize=10, fontweight="bold")
            bottom = modo == "ambos"
            ax_hist.tick_params(labelsize=8, bottom=not bottom, labelbottom=not bottom)
            sns.despine(ax=ax_hist, bottom=bottom)

        # ── Boxplot ──────────────────────────────────────────────────────
        if modo in ("ambos", "boxplot"):
            ax_box = axes[fila + 1, col_idx] if modo == "ambos" else axes[fila, col_idx]

            sns.boxplot(
                x=df[col], ax=ax_box, color=color,
                width=0.18,         # caja más delgada
                linewidth=0.8,      # líneas más finas
                flierprops=dict(marker="o", markerfacecolor=color, markersize=3),
            )
            for patch in ax_box.patches:
                patch.set_alpha(0.6)

            ax_box.text(
                mediana, 0, f"{mediana:,.0f}",
                ha="center", va="center", fontsize=9, fontweight="bold", color="white",
                bbox=dict(facecolor=color, edgecolor="none", boxstyle="round,pad=0.35"),
            )

            if modo == "boxplot":
                ax_box.set_title(f"{col}\n$\\mu$={media:.1f}  $\\sigma$={std:.1f}",
                                 fontsize=10, fontweight="bold")

            ax_box.set(
                xlim=xlim,
                ylim=(-0.5, 0.5),   # centra y pega la caja
                yticks=[],
                xlabel="",
            )
            ax_box.tick_params(labelsize=8)
            sns.despine(ax=ax_box, left=True)

    # ── Ocultar celdas sobrantes ─────────────────────────────────────────
    for j in range(len(columnas), n_rows * cols):
        fila    = (j // cols) * filas_por_var
        col_idx = j % cols
        for r in range(filas_por_var):
            axes[fila + r, col_idx].set_visible(False)

    fig.suptitle(titulo, fontsize=15, fontweight="bold", y=1.01)
    plt.tight_layout(w_pad=-3, h_pad=0)
    plt.show()

# Estilo global para graficas y helpers
def set_plot_style():
    plt.style.use("seaborn-v0_8-whitegrid")
    sns.set_context("notebook", font_scale=1.05)
    sns.set_palette(["#2E86AB", "#1B4F72", "#C0392B", "#27AE60", "#F39C12"])


def boxplot_pro(series, title, xlabel):
    data = series.dropna()
    fig, ax = plt.subplots(figsize=(9, 4))
    fig.patch.set_facecolor("#F7F9FB")
    ax.boxplot(
        data,
        vert=False,
        widths=0.5,
        patch_artist=True,
        boxprops={"facecolor": "#2E86AB", "alpha": 0.6, "edgecolor": "#1B4F72"},
        medianprops={"color": "#C0392B", "linewidth": 2},
        whiskerprops={"color": "#1B4F72", "linewidth": 1.5},
        capprops={"color": "#1B4F72", "linewidth": 1.5},
        flierprops={
            "marker": "o",
            "markersize": 4,
            "markerfacecolor": "#F39C12",
            "markeredgecolor": "#B9770E",
            "alpha": 0.5,
        },
        showmeans=True,
        meanprops={
            "marker": "D",
            "markerfacecolor": "#27AE60",
            "markeredgecolor": "#1E8449",
        },
    )
    ax.set_title(title, pad=12, fontsize=12, fontweight="bold")
    ax.set_xlabel(xlabel)
    ax.set_yticks([])

    q1, q2, q3 = data.quantile([0.25, 0.5, 0.75])
    iqr = q3 - q1
    ax.text(
        0.99,
        0.85,
        f"n={len(data):,}\nmediana={q2:.1f}\nIQR={iqr:.1f}",
        transform=ax.transAxes,
        ha="right",
        va="top",
        fontsize=9,
        bbox={
            "boxstyle": "round",
            "facecolor": "white",
            "alpha": 0.9,
            "edgecolor": "#D5D8DC",
        },
    )

    plt.tight_layout()
    plt.show()