"""Distribución ABO/Rh: casi el 60% es grupo O y solo puede recibir O− u O+."""

import numpy as np
from manim import (
    BOLD,
    DOWN,
    NORMAL,
    UP,
    BLACK,
    Create,
    FadeIn,
    Flash,
    GrowFromEdge,
    Indicate,
    LaggedStart,
    Line,
    Rectangle,
    VGroup,
)

from componentes import parrafo, texto, titulo
from estilo import GRIS, ROJO


def construir(scene):
    encabezado = titulo("Casi el 60% solo puede recibir 2 de los 8 tipos")

    # Distribución ABO/Rh en 87.481 donantes (Hospital Pablo Tobón Uribe)
    datos = [
        ("O+", 52.1, True), ("A+", 28.0, False), ("O−", 7.0, True),
        ("B+", 6.7, False), ("A−", 3.5, False), ("AB+", 1.7, False),
        ("B−", 0.8, False), ("AB−", 0.3, False),
    ]
    base_y = -1.75
    escala_h = 3.1 / 52.1
    ancho_b, paso, x0 = 0.62, 0.985, -6.1

    barras, etiquetas, pcts = VGroup(), VGroup(), VGroup()
    barras_gris, pcts_gris = [], []
    for i, (nombre, pct, es_o) in enumerate(datos):
        alto = max(pct * escala_h, 0.07)
        x = x0 + i * paso
        barra = Rectangle(
            width=ancho_b, height=alto,
            fill_color=ROJO if es_o else GRIS,
            fill_opacity=0.95 if es_o else 0.55,
            stroke_width=0,
        ).move_to(np.array([x, base_y + alto / 2, 0]))
        lbl = texto(nombre, 15, color=ROJO if es_o else BLACK, weight=BOLD)
        lbl.move_to(np.array([x, base_y - 0.3, 0]))
        pt = texto(f"{pct:.1f}".replace(".", ",") + " %", 13,
                   color=ROJO if es_o else GRIS)
        pt.move_to(np.array([x, base_y + alto + 0.22, 0]))
        barras.add(barra)
        etiquetas.add(lbl)
        pcts.add(pt)
        if not es_o:
            barras_gris.append(barra)
            pcts_gris.append(pt)
    eje = Line(
        np.array([x0 - 0.55, base_y, 0]),
        np.array([x0 + 7 * paso + 0.55, base_y, 0]),
        color=GRIS, stroke_width=2.5,
    )

    tarjeta_o = parrafo([
        ("≈ 60 %", 58, ROJO, BOLD),
        ("de la población es grupo O:", 21, BLACK, NORMAL),
        ("solo puede recibir O− u O+", 24, ROJO, BOLD),
    ], buff=0.18).move_to(np.array([4.35, 0.75, 0]))
    nota_o = texto("52,1 % (O+)  +  7,0 % (O−)  =  59,1 %", 17, color=GRIS)
    nota_o.next_to(tarjeta_o, DOWN, buff=0.3)

    fuente = texto(
        "Fuente: Banco de sangre · Hospital Pablo Tobón Uribe · 87.481 donantes",
        16, color=GRIS,
    ).to_edge(DOWN, buff=0.35)

    scene.play(FadeIn(encabezado, shift=DOWN * 0.2), run_time=0.8)
    scene.play(Create(eje), run_time=0.5)
    scene.play(
        LaggedStart(*[GrowFromEdge(b, DOWN) for b in barras], lag_ratio=0.12),
        LaggedStart(*[FadeIn(e) for e in etiquetas], lag_ratio=0.12),
        run_time=1.8,
    )
    scene.play(
        LaggedStart(*[FadeIn(p, shift=UP * 0.1) for p in pcts], lag_ratio=0.1),
        run_time=1.0,
    )
    scene.wait(0.3)
    scene.play(
        *[b.animate.set_opacity(0.22) for b in barras_gris],
        *[p.animate.set_opacity(0.35) for p in pcts_gris],
        run_time=0.7,
    )
    scene.play(
        Indicate(barras[0], scale_factor=1.05, color=ROJO),
        Indicate(barras[2], scale_factor=1.15, color=ROJO),
        run_time=0.8,
    )
    scene.play(FadeIn(tarjeta_o, shift=UP * 0.2), run_time=0.7)
    scene.play(
        FadeIn(nota_o),
        Flash(tarjeta_o[0], color=ROJO, line_length=0.3),
        run_time=0.6,
    )
    scene.play(FadeIn(fuente), run_time=0.4)
    scene.wait(0.5)
    scene.next_slide()
