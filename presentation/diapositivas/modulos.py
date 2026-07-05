"""Los tres módulos de SangHelios: forecasting, multi-agente y centro operacional."""

import numpy as np
from manim import (
    BLACK,
    BOLD,
    DOWN,
    LEFT,
    RIGHT,
    UP,
    Arrow,
    Dot,
    FadeIn,
    GrowArrow,
    Line,
    RoundedRectangle,
    VGroup,
    VMobject,
    WHITE,
)

from componentes import tarjeta, texto
from componentes import titulo as hacer_titulo
from estilo import GRIS, ROJO


def _icono_forecast():
    """Mini serie temporal que sube y cruza en alerta."""
    base = Line(LEFT * 0.55, RIGHT * 0.55, color=GRIS, stroke_width=3).shift(DOWN * 0.28)
    curva = VMobject(color=ROJO, stroke_width=4.5)
    curva.set_points_smoothly([
        np.array([-0.5, -0.2, 0]), np.array([-0.2, 0.0, 0]),
        np.array([0.05, -0.1, 0]), np.array([0.5, 0.32, 0]),
    ])
    punta = Dot(np.array([0.5, 0.32, 0]), radius=0.06, color=ROJO)
    return VGroup(base, curva, punta)


def _icono_agentes():
    """Red de agentes: tres nodos conectados."""
    a = np.array([0.0, 0.3, 0])
    b = np.array([-0.42, -0.22, 0])
    c = np.array([0.42, -0.22, 0])
    aristas = VGroup(Line(a, b), Line(b, c), Line(c, a)).set_stroke(GRIS, 3)
    nodos = VGroup(*[Dot(p, radius=0.09, color=ROJO) for p in (a, b, c)])
    return VGroup(aristas, nodos)


def _icono_web():
    """Ventanita de navegador."""
    ventana = RoundedRectangle(
        corner_radius=0.08, width=1.0, height=0.66,
        stroke_color=ROJO, stroke_width=3.5, fill_opacity=0,
    )
    barra = Line(
        ventana.get_corner(UP + LEFT) + DOWN * 0.18,
        ventana.get_corner(UP + RIGHT) + DOWN * 0.18,
        color=ROJO, stroke_width=2.5,
    )
    punto = Dot(
        ventana.get_corner(UP + LEFT) + DOWN * 0.09 + RIGHT * 0.1,
        radius=0.03, color=ROJO,
    )
    return VGroup(ventana, barra, punto)


def _modulo(numero, icono, nombre, lineas, nota):
    detalle = VGroup(*[texto(t, 17, color=BLACK) for t in lineas])
    detalle.arrange(DOWN, buff=0.14)
    contenido = VGroup(
        icono,
        texto(nombre, 25, color=ROJO, weight=BOLD),
        detalle,
        texto(nota, 14, color=GRIS),
    ).arrange(DOWN, buff=0.24)

    fondo = RoundedRectangle(
        corner_radius=0.16, width=4.15, height=3.75,
        stroke_color=ROJO, stroke_width=4, fill_color=WHITE, fill_opacity=1.0,
    )
    contenido.move_to(fondo.get_center() + DOWN * 0.1)
    chip = tarjeta([(numero, 22, BOLD)], ancho_extra=0.36, alto_extra=0.22, escala=0.8)
    chip.move_to(fondo.get_top())
    return VGroup(fondo, contenido, chip)


def construir(scene):
    encabezado = hacer_titulo("Tres módulos para adelantarse a la crisis")

    modulos = VGroup(
        _modulo("1", _icono_forecast(), "Forecasting", [
            "XGBoost anticipa la escasez",
            "con 14 días de ventaja,",
            "por fenotipo sanguíneo",
        ], "presión = demanda − oferta (7 días)"),
        _modulo("2", _icono_agentes(), "Multi-Agente", [
            "elige la comuna y el día",
            "idóneos para la recolección;",
            "un agente de marketing (LLMs)",
            "genera las piezas gráficas",
        ], "se activa con cada alerta"),
        _modulo("3", _icono_web(), "Centro Operacional", [
            "interfaz web interactiva:",
            "dashboard del banco de sangre",
            "y mapa 3D de campañas",
        ], "FastAPI"),
    ).arrange(RIGHT, buff=0.55).shift(DOWN * 0.5)

    flechas = VGroup(*[
        Arrow(
            modulos[i].get_right(), modulos[i + 1].get_left(),
            color=GRIS, stroke_width=4, buff=0.08,
            max_tip_length_to_length_ratio=0.45,
        )
        for i in range(2)
    ])

    scene.play(FadeIn(encabezado, shift=DOWN * 0.2), run_time=0.7)
    for i, modulo in enumerate(modulos):
        if i > 0:
            scene.play(GrowArrow(flechas[i - 1]), run_time=0.35)
        scene.play(FadeIn(modulo, shift=UP * 0.2), run_time=0.6)
    scene.wait(0.5)

    scene.next_slide()
