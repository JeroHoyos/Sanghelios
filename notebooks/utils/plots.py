"""Estilo global y helpers de visualización compartidos por los notebooks."""

import matplotlib.pyplot as plt
import seaborn as sns

# ── Paleta y constantes compartidas ─────────────────────────────────────────
PALETA = ["#185FA5", "#A32D2D", "#3B6D11", "#D49A3A", "#8E5BA3"]
MESES = ["Ene", "Feb", "Mar", "Abr", "May", "Jun",
         "Jul", "Ago", "Sep", "Oct", "Nov", "Dic"]
C_SEXO = {"f": "#A32D2D", "m": "#185FA5"}
C_CLUSTER = {0: "#A32D2D", 1: "#185FA5", 2: "#3B6D11"}

# Parámetros del estilo global (un único lugar para tocar la estética)
_RCPARAMS = {
    "figure.facecolor": "#FAFAFA",
    "axes.facecolor": "#FAFAFA",
    "axes.edgecolor": "#DDDDDD",
    "axes.labelcolor": "#333333",
    "xtick.color": "#444444",
    "ytick.color": "#444444",
    "grid.color": "#E6E6E6",
    "grid.linewidth": 0.8,
    "axes.titleweight": "600",
    "axes.titlesize": 12,
    "axes.labelsize": 9,
    "xtick.labelsize": 8,
    "ytick.labelsize": 8,
}


def aplicar_estilo_global():
    """Aplica el tema seaborn + rcParams usados en los notebooks de EDA/clustering."""
    sns.set_theme(style="whitegrid")
    plt.rcParams.update(_RCPARAMS)


def style_axes(ax, title=None, xlabel=None, ylabel=None, grid_axis="y"):
    """Aplica el estilo estándar a un eje: grid suave, sin spines superfluas."""
    if grid_axis:
        ax.grid(axis=grid_axis, linewidth=0.6, alpha=0.6)
        ax.set_axisbelow(True)
    if title:
        ax.set_title(title, loc="left")
    if xlabel is not None:
        ax.set_xlabel(xlabel)
    if ylabel is not None:
        ax.set_ylabel(ylabel)
    for spine in ["top", "right", "left"]:
        ax.spines[spine].set_visible(False)
    ax.spines["bottom"].set_color("#ddd")


def label_bars(ax, bars, labels=None, orientation="v",
               offset_ratio=0.03, fontsize=8, color="#444"):
    """Etiqueta barras de un gráfico (vertical u horizontal) con su valor."""
    if not len(bars):
        return
    if orientation == "v":
        heights = [b.get_height() for b in bars]
        offset = max(heights) * offset_ratio if heights else 0
        if labels is None:
            labels = [f"{h:,.0f}" for h in heights]
        for bar, lbl in zip(bars, labels):
            ax.text(
                bar.get_x() + bar.get_width() / 2,
                bar.get_height() + offset,
                lbl,
                ha="center",
                va="bottom",
                fontsize=fontsize,
                color=color,
            )
    else:
        widths = [b.get_width() for b in bars]
        offset = max(widths) * offset_ratio if widths else 0
        if labels is None:
            labels = [f"{w:,.0f}" for w in widths]
        for bar, lbl in zip(bars, labels):
            ax.text(
                bar.get_width() + offset,
                bar.get_y() + bar.get_height() / 2,
                lbl,
                ha="left",
                va="center",
                fontsize=fontsize,
                color=color,
            )


def set_plot_style():
    """Estilo alternativo (notebook 1): seaborn whitegrid con paleta cálida."""
    plt.style.use("seaborn-v0_8-whitegrid")
    sns.set_context("notebook", font_scale=1.05)
    sns.set_palette(["#2E86AB", "#1B4F72", "#C0392B", "#27AE60", "#F39C12"])


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


def boxplot_pro(series, title, xlabel):
    """Boxplot horizontal estilizado con caja de estadísticas (n, mediana, IQR)."""
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
