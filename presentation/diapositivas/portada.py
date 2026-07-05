"""Portada: logo y la curva de presión cruzando el umbral de escasez."""

import numpy as np
from manim import (
    BOLD,
    DOWN,
    LEFT,
    RIGHT,
    UP,
    Axes,
    Create,
    DashedLine,
    Dot,
    FadeIn,
    Flash,
    GrowFromCenter,
    Line,
    ValueTracker,
    VGroup,
    always_redraw,
    linear,
)

from componentes import imagen, texto
from estilo import GRIS, ROJO, UMBRAL


def _datos_presion():
    rng = np.random.default_rng(7)
    x = np.linspace(0, 12, 60)
    y = 20 + 4.8 * x + 6 * np.sin(x * 0.8 + 0.3) + rng.normal(0, 2.2, x.size)
    return x, y


def construir(scene):
    logo = imagen("logo-blanco").scale_to_fit_width(7.2).to_edge(UP, buff=0.2)
    subtitulo = texto(
        "Inteligencia predictiva para bancos de sangre", 21, color=GRIS,
    ).next_to(logo, DOWN, buff=0.05)
    hearthand = imagen("hearthand", 0.8).to_corner(DOWN + LEFT, buff=0.25).shift(UP * 0.35)
    blood = imagen("blood", 0.8).to_corner(DOWN + RIGHT, buff=0.25).shift(UP * 0.35)

    axes = Axes(
        x_range=[0, 12, 1],
        y_range=[0, 100, 20],
        x_length=9.0,
        y_length=3.2,
        axis_config={"stroke_width": 0, "include_tip": False, "include_ticks": False},
    ).shift(DOWN * 0.85)

    eje_x = Line(axes.c2p(0, 0), axes.c2p(12, 0), color=GRIS, stroke_width=2)
    eje_y = Line(axes.c2p(0, 0), axes.c2p(0, 100), color=GRIS, stroke_width=2)

    x_nodes, y_nodes = _datos_presion()
    presion = lambda x: float(np.interp(x, x_nodes, y_nodes))
    primer_cruce = x_nodes[np.argmax(y_nodes > UMBRAL)] if (y_nodes > UMBRAL).any() else 12.0

    umbral_graph = axes.plot(lambda x: UMBRAL, x_range=[0, 12])
    umbral_line = DashedLine(
        axes.c2p(0, UMBRAL), axes.c2p(12, UMBRAL),
        color=ROJO, dash_length=0.14, stroke_width=2.0,
    )
    umbral_lbl = texto("Umbral de escasez", 15, color=ROJO)
    umbral_lbl.move_to(axes.c2p(2.4, UMBRAL) + UP * 0.24)

    # Zonas como en el dashboard real (a la izquierda de la gráfica)
    zona_crit = texto("ZONA CRÍTICA", 14, color=ROJO, weight=BOLD)
    zona_crit.move_to(axes.c2p(1.15, UMBRAL + 34))
    zona_est = texto("ZONA ESTABLE", 14, color=GRIS, weight=BOLD)
    zona_est.move_to(axes.c2p(1.15, UMBRAL - 34))
    presion_lbl = texto("Presión (demanda − oferta)", 15, color=ROJO, weight=BOLD)

    x_tracker = ValueTracker(0.0)

    def linea(x0, x1, stroke):
        if x1 <= x0 + 0.02:
            return VGroup()
        return axes.plot(presion, x_range=[x0, x1, 0.02], color=ROJO, stroke_width=stroke)

    def area(x0, x1, opacity):
        if x1 <= x0 + 0.02:
            return VGroup()
        curva = axes.plot(presion, x_range=[x0, x1, 0.02])
        return axes.get_area(
            curva, x_range=[x0, x1], color=ROJO,
            opacity=opacity, bounded_graph=umbral_graph,
        )

    def segmento(x0_fn, x1_fn, opacity, stroke):
        fill = always_redraw(lambda: area(x0_fn(), x1_fn(), opacity))
        curva = always_redraw(lambda: linea(x0_fn(), x1_fn(), stroke))
        return fill, curva

    zona_segura = segmento(lambda: 0, lambda: min(x_tracker.get_value(), primer_cruce), 0.15, 3.0)
    zona_escasez = segmento(lambda: primer_cruce, lambda: x_tracker.get_value(), 0.28, 3.8)

    cruce_dot = Dot(axes.c2p(primer_cruce, UMBRAL), color=ROJO, radius=0.07)
    excl = texto("!", 80, color=ROJO, weight=BOLD).next_to(cruce_dot, UP, buff=0.15)

    scene.play(FadeIn(logo, scale=0.92), run_time=0.9)
    scene.play(
        FadeIn(subtitulo, shift=DOWN * 0.1),
        FadeIn(hearthand, shift=RIGHT * 0.2),
        FadeIn(blood, shift=LEFT * 0.2),
        Create(eje_x),
        Create(eje_y),
        Create(umbral_line),
        FadeIn(umbral_lbl),
        FadeIn(zona_crit),
        FadeIn(zona_est),
        run_time=1.2,
    )
    scene.add(*zona_segura, *zona_escasez)

    scene.play(x_tracker.animate.set_value(primer_cruce), run_time=2.0, rate_func=linear)
    scene.play(
        FadeIn(cruce_dot, scale=0.4),
        GrowFromCenter(excl),
        Flash(excl, color=ROJO, line_length=0.3),
        run_time=0.6,
    )
    scene.play(x_tracker.animate.set_value(12), run_time=1.8, rate_func=linear)
    presion_lbl.move_to(axes.c2p(9.6, 92))
    scene.play(FadeIn(presion_lbl, shift=UP * 0.1), run_time=0.5)
    scene.wait(0.5)

    scene.next_slide()
