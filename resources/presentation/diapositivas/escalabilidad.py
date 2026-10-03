"""Escalabilidad: tres fases, del HGM a una red de intercambio regional."""

import numpy as np
from manim import (
    BOLD,
    DOWN,
    LEFT,
    NORMAL,
    RIGHT,
    UP,
    Arrow,
    Create,
    Dot,
    FadeIn,
    Flash,
    GrowFromCenter,
    Line,
    RoundedRectangle,
    VGroup,
)

from componentes import arbolito, imagen, tarjeta, texto
from componentes import titulo as hacer_titulo
from estilo import GRIS, ROJO


def _icono_datasets():
    """Pila de datasets."""
    return VGroup(*[
        RoundedRectangle(
            corner_radius=0.06, width=0.85, height=0.2,
            stroke_color=ROJO, stroke_width=3, fill_opacity=0,
        )
        for _ in range(3)
    ]).arrange(DOWN, buff=0.08)


def _icono_modelo():
    """Arbolito de decisión (el modelo se enriquece)."""
    grupo, _, _ = arbolito(ancho=1.6, alto=1.1)
    return grupo.scale(0.55)


def _icono_red():
    """Red de hemocentros conectados."""
    centro = np.array([0.0, 0.0, 0])
    alrededor = [
        np.array([-0.45, 0.25, 0]), np.array([0.45, 0.28, 0]),
        np.array([-0.3, -0.32, 0]), np.array([0.38, -0.28, 0]),
    ]
    aristas = VGroup(*[Line(centro, p) for p in alrededor]).set_stroke(GRIS, 3)
    nodos = VGroup(
        Dot(centro, radius=0.1, color=ROJO),
        *[Dot(p, radius=0.07, color=ROJO) for p in alrededor],
    )
    return VGroup(aristas, nodos)


def construir(scene):
    encabezado = hacer_titulo("Escalabilidad")

    largo = 11.4
    linea = Arrow(
        LEFT * largo / 2, RIGHT * largo / 2, color=GRIS, stroke_width=4,
        buff=0, max_tip_length_to_length_ratio=0.03,
    ).shift(UP * 0.1)

    fases = [
        (_icono_datasets(), "Fase 1", "Más datasets", [
            "accidentalidad, epidemiología",
            "y más centros de salud públicos",
        ]),
        (_icono_modelo(), "Fase 2", "Modelo enriquecido", [
            "más señales para predecir",
            "cada fenotipo con precisión",
        ]),
        (_icono_red(), "Fase 3", "Red de Intercambio", [
            "hemocentros conectados",
            "en el Valle de Aburrá",
        ]),
    ]

    radios = [0.09, 0.11, 0.13]
    puntos, iconos, rotulos, detalles = VGroup(), VGroup(), VGroup(), VGroup()
    for i, (icono, fase, nombre, lineas) in enumerate(fases):
        p = linea.point_from_proportion(0.08 + i * 0.42)
        puntos.add(Dot(p, color=ROJO, radius=radios[i]))
        rotulo = VGroup(
            texto(fase, 19, color=ROJO, weight=BOLD),
            texto(nombre, 26, weight=BOLD),
        ).arrange(DOWN, buff=0.12).next_to(p, UP, buff=0.35)
        rotulos.add(rotulo)
        iconos.add(icono.next_to(rotulo, UP, buff=0.28))
        detalles.add(
            VGroup(*[texto(t, 16, color=GRIS) for t in lineas])
            .arrange(DOWN, buff=0.1).next_to(p, DOWN, buff=0.35)
        )

    meta = tarjeta([
        ("Meta: reducir las crisis por desabastecimiento", 21, BOLD),
        ("optimizando los recursos de la región · ninguna bolsa de sangre se pierde", 15, NORMAL),
    ], escala=0.92).to_edge(DOWN, buff=0.65)

    hearthand = imagen("hearthand", 0.62).to_corner(DOWN + LEFT, buff=0.28).shift(UP * 0.1)
    blood = imagen("blood", 0.62).to_corner(DOWN + RIGHT, buff=0.28).shift(UP * 0.1)

    scene.play(FadeIn(encabezado, shift=DOWN * 0.2), run_time=0.7)
    scene.play(Create(linea), run_time=1.0)
    for punto, icono, rotulo, detalle in zip(puntos, iconos, rotulos, detalles):
        scene.play(
            GrowFromCenter(punto),
            FadeIn(rotulo, shift=UP * 0.15),
            FadeIn(icono, shift=UP * 0.1),
            FadeIn(detalle, shift=DOWN * 0.1),
            run_time=0.7,
        )
    scene.play(
        GrowFromCenter(meta),
        FadeIn(hearthand, shift=RIGHT * 0.2),
        FadeIn(blood, shift=LEFT * 0.2),
        run_time=0.7,
    )
    scene.play(Flash(puntos[-1], color=ROJO, line_length=0.3), run_time=0.5)
    scene.wait(0.5)

    scene.next_slide()
