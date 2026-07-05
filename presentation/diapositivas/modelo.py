"""¿Cómo pronostica el modelo? La presión del sistema y el camino del dato a la alerta."""

import numpy as np
from manim import (
    BOLD,
    DOWN,
    LEFT,
    NORMAL,
    RIGHT,
    UP,
    Arrow,
    Axes,
    Create,
    DashedVMobject,
    FadeIn,
    Flash,
    GrowArrow,
    GrowFromCenter,
    Line,
    RoundedRectangle,
    VGroup,
    VMobject,
    WHITE,
)

from componentes import tarjeta, texto
from componentes import titulo as hacer_titulo
from estilo import GRIS, ROJO


def _chip(nombre, sub):
    """Tarjeta blanca con borde rojo: concepto + aclaración."""
    lineas = VGroup(
        texto(nombre, 26, color=ROJO, weight=BOLD),
        texto(sub, 14, color=GRIS),
    ).arrange(DOWN, buff=0.12)
    fondo = RoundedRectangle(
        corner_radius=0.14,
        width=lineas.width + 0.6, height=lineas.height + 0.45,
        stroke_color=ROJO, stroke_width=4, fill_color=WHITE, fill_opacity=1.0,
    )
    return VGroup(fondo, lineas.move_to(fondo))


def _seccion(nombre):
    return VGroup(
        Line(LEFT * 0.55, RIGHT * 0.0, color=ROJO, stroke_width=3),
        texto(nombre, 20, color=ROJO, weight=BOLD),
        Line(LEFT * 0.0, RIGHT * 0.55, color=ROJO, stroke_width=3),
    ).arrange(RIGHT, buff=0.3)


def construir(scene):
    encabezado = hacer_titulo("¿Cómo pronostica el modelo?")

    # ── 1 · Qué es la presión del sistema ──
    seccion_a = _seccion("La presión del sistema").shift(UP * 2.05)

    demanda = _chip("Demanda", "sangre que el hospital usa")
    menos = texto("−", 46, color=ROJO, weight=BOLD)
    oferta = _chip("Oferta", "donaciones · media 7 días")
    igual = texto("=", 46, color=ROJO, weight=BOLD)
    presion = tarjeta([("Presión", 26, BOLD), ("del sistema", 15, NORMAL)], escala=0.98)
    formula = VGroup(demanda, menos, oferta, igual, presion)
    formula.arrange(RIGHT, buff=0.45).shift(UP * 1.05)

    nota = texto(
        "presión alta = se gasta más sangre de la que llega → riesgo de escasez",
        17, color=GRIS,
    ).next_to(formula, DOWN, buff=0.35)

    # ── 2 · Del dato a la alerta ──
    seccion_b = _seccion("Del dato a la alerta").shift(DOWN * 0.55)

    ejes = Axes(
        x_range=[0, 21, 21], y_range=[0, 3, 3],
        x_length=3.2, y_length=1.4,
        axis_config={"stroke_width": 0, "include_ticks": False, "include_tip": False},
    )
    rng = np.random.default_rng(11)
    ys = 1.1 + 0.45 * np.sin(np.arange(22) * 0.55) + np.linspace(0, 0.9, 22) + rng.normal(0, 0.07, 22)
    curva = VMobject(color=ROJO, stroke_width=3.5)
    curva.set_points_smoothly([ejes.c2p(i, y) for i, y in enumerate(ys)])
    base = Line(ejes.c2p(0, 0), ejes.c2p(21, 0), color=GRIS, stroke_width=2)
    serie = VGroup(ejes, base, curva)
    serie.to_edge(LEFT, buff=0.85).shift(DOWN * 1.85)

    ventana = DashedVMobject(
        RoundedRectangle(
            corner_radius=0.08, width=1.9, height=1.55,
            stroke_color=ROJO, stroke_width=3,
        ),
        num_dashes=42,
    ).move_to(ejes.c2p(15.5, 1.5))
    serie_lbl = texto("presión · últimos 14 días", 15, color=ROJO, weight=BOLD)
    serie_lbl.next_to(serie, UP, buff=0.18)

    modelo = _chip("XGBoost", "aprende de 5 años de datos")
    modelo.move_to(np.array([0.0, -1.85, 0.0]))

    alerta = tarjeta([
        ("¡Escasez en 14 días!", 21, BOLD),
        ("P = 68 % · se activa la campaña", 14, NORMAL),
    ], escala=0.95)
    alerta.to_edge(RIGHT, buff=0.85).match_y(modelo)

    flecha_a = Arrow(
        serie.get_right() + RIGHT * 0.05, modelo.get_left(),
        color=GRIS, stroke_width=4, buff=0.15, max_tip_length_to_length_ratio=0.3,
    )
    flecha_b = Arrow(
        modelo.get_right(), alerta.get_left(),
        color=GRIS, stroke_width=4, buff=0.15, max_tip_length_to_length_ratio=0.3,
    )
    # ── Animación ──
    scene.play(FadeIn(encabezado, shift=DOWN * 0.2), run_time=0.7)

    scene.play(FadeIn(seccion_a, shift=DOWN * 0.1), run_time=0.5)
    scene.play(GrowFromCenter(demanda), run_time=0.5)
    scene.play(FadeIn(menos, scale=1.3), GrowFromCenter(oferta), run_time=0.5)
    scene.play(FadeIn(igual, scale=1.3), GrowFromCenter(presion), run_time=0.5)
    scene.play(Flash(presion, color=ROJO, line_length=0.25), FadeIn(nota), run_time=0.6)

    scene.play(FadeIn(seccion_b, shift=DOWN * 0.1), run_time=0.5)
    scene.play(Create(base), Create(curva), FadeIn(serie_lbl), run_time=1.0)
    scene.play(Create(ventana), run_time=0.6)
    scene.play(GrowArrow(flecha_a), GrowFromCenter(modelo), run_time=0.6)
    scene.play(GrowArrow(flecha_b), run_time=0.5)
    scene.play(
        GrowFromCenter(alerta),
        Flash(alerta, color=ROJO, line_length=0.3),
        run_time=0.7,
    )
    scene.wait(0.6)
    scene.next_slide()
