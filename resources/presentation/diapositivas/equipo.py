"""Predicamos con el ejemplo: el equipo ya está donando sangre."""

import os

from manim import (
    BOLD,
    DOWN,
    RIGHT,
    UP,
    FadeIn,
    Group,
    ImageMobject,
    LaggedStart,
    RoundedRectangle,
)

from componentes import texto, titulo
from estilo import ROJO

ASSETS = "assets"
CAJA_W, CAJA_H = 3.6, 4.1
MARGEN = 0.14


def _donante(nombre_archivo, etiqueta):
    """Retrato en un marco de tamaño fijo + nombre."""
    marco = RoundedRectangle(
        width=CAJA_W, height=CAJA_H, corner_radius=0.16,
        stroke_color=ROJO, stroke_width=5, fill_opacity=0,
    )
    foto = ImageMobject(os.path.join(ASSETS, f"{nombre_archivo}.jpeg"))
    foto.scale_to_fit_height(CAJA_H - MARGEN)
    if foto.width > CAJA_W - MARGEN:
        foto.scale_to_fit_width(CAJA_W - MARGEN)
    foto.move_to(marco.get_center())
    retrato = Group(foto, marco)

    nombre = texto(etiqueta, 26, weight=BOLD)
    return Group(retrato, nombre).arrange(DOWN, buff=0.22)


def construir(scene):
    encabezado = titulo("Predicamos con el ejemplo: ya estamos donando")

    donantes = Group(
        _donante("miguel", "Jose Miguel"),
        _donante("jero", "Jero"),
        _donante("daniel", "Daniel"),
    ).arrange(RIGHT, buff=0.55)
    donantes.next_to(encabezado, DOWN, buff=0.55)

    scene.play(FadeIn(encabezado, shift=DOWN * 0.2), run_time=0.9)
    scene.play(
        LaggedStart(
            *[FadeIn(col, shift=UP * 0.2) for col in donantes],
            lag_ratio=0.35,
        ),
        run_time=1.8,
    )
    scene.wait(0.5)

    scene.next_slide()
