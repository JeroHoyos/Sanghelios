"""Fábricas de mobjects reutilizables (texto, tarjetas, reloj, árboles…).

Todas son funciones puras: reciben parámetros y devuelven mobjects listos
para posicionar y animar desde las diapositivas.
"""

import os

import numpy as np
from manim import (
    BLACK,
    DOWN,
    LEFT,
    NORMAL,
    ORIGIN,
    PI,
    RIGHT,
    TAU,
    UP,
    WHITE,
    Circle,
    Dot,
    ImageMobject,
    Line,
    Rectangle,
    RoundedRectangle,
    Square,
    Text,
    VGroup,
    config,
)

from estilo import ASSETS, ESCALA_TITULO, FONT, GRIS, ROJO


def marco():
    return Rectangle(
        width=config.frame_width - 0.22,
        height=config.frame_height - 0.22,
        stroke_color=ROJO,
        stroke_width=8,
        fill_opacity=0,
    )


def imagen(nombre, escala=1.0):
    return ImageMobject(os.path.join(ASSETS, f"{nombre}.png")).scale(escala)


def texto(contenido, tam, color=BLACK, weight=NORMAL):
    return Text(contenido, font=FONT, font_size=tam, color=color, weight=weight)


def parrafo(lineas, buff=0.15, alinear=ORIGIN):
    textos = [texto(*linea) for linea in lineas]
    return VGroup(*textos).arrange(DOWN, buff=buff, aligned_edge=alinear)


def tarjeta(lineas, ancho_extra=0.7, alto_extra=0.4, escala=1.0):
    textos = VGroup(*[
        texto(t, fs, color=WHITE, weight=w) for t, fs, w in lineas
    ]).arrange(DOWN, buff=0.1)
    fondo = RoundedRectangle(
        corner_radius=0.14,
        width=textos.width + ancho_extra,
        height=textos.height + alto_extra,
        fill_color=ROJO,
        fill_opacity=1.0,
        stroke_width=0,
    )
    return VGroup(fondo, textos).scale(escala)


def titulo(contenido):
    from manim import BOLD

    t = tarjeta([(contenido, 28, BOLD)], escala=ESCALA_TITULO)
    return t.to_edge(UP, buff=0.6)


def vinetas(textos, tam=26, buff=0.45):
    filas = VGroup()
    for contenido in textos:
        punto = Dot(radius=0.07, color=ROJO)
        filas.add(VGroup(punto, texto(contenido, tam)).arrange(RIGHT, buff=0.25))
    return filas.arrange(DOWN, buff=buff, aligned_edge=LEFT)


def _direccion(hora):
    ang = PI / 2 - hora * TAU / 12
    return np.array([np.cos(ang), np.sin(ang), 0])


def reloj(radio=1.15):
    cara = Circle(
        radius=radio, color=ROJO, stroke_width=6,
        fill_color=WHITE, fill_opacity=1.0,
    )
    centro = cara.get_center()
    marcas = VGroup(*[
        Line(
            centro + radio * 0.82 * _direccion(i),
            centro + radio * 0.96 * _direccion(i),
            color=GRIS, stroke_width=3,
        )
        for i in range(12)
    ])
    horario = Line(centro, centro + radio * 0.5 * UP, color=BLACK, stroke_width=7)
    minutero = Line(centro, centro + radio * 0.78 * UP, color=ROJO, stroke_width=4)
    eje = Dot(centro, radius=0.06, color=BLACK)
    grupo = VGroup(cara, marcas, horario, minutero, eje)
    return grupo, horario, minutero


def calendario(ancho=2.6, alto=2.6, cols=7, filas=4):
    cuerpo = RoundedRectangle(
        width=ancho, height=alto, corner_radius=0.14,
        stroke_color=ROJO, stroke_width=5,
        fill_color=WHITE, fill_opacity=1.0,
    )
    encabezado = RoundedRectangle(
        width=ancho, height=alto * 0.26, corner_radius=0.14,
        fill_color=ROJO, fill_opacity=1.0, stroke_width=0,
    ).align_to(cuerpo, UP)
    anillas = VGroup(*[
        Line(UP * 0.16, DOWN * 0.16, color=GRIS, stroke_width=5) for _ in range(2)
    ]).arrange(RIGHT, buff=ancho * 0.4).move_to(encabezado.get_top())

    celda = ancho / (cols + 1)
    rejilla = VGroup(*[
        Square(side_length=celda * 0.78, stroke_color=GRIS, stroke_width=1.5, fill_opacity=0)
        for _ in range(cols * filas)
    ])
    rejilla.arrange_in_grid(rows=filas, cols=cols, buff=celda * 0.22)
    rejilla.next_to(encabezado, DOWN, buff=0.16)

    grupo = VGroup(cuerpo, encabezado, anillas, rejilla)
    return grupo, rejilla


def enmarcar(img, margen=0.12):
    return RoundedRectangle(
        width=img.width + margen, height=img.height + margen,
        corner_radius=0.14, stroke_color=ROJO, stroke_width=5, fill_opacity=0,
    ).move_to(img.get_center())


def linea_tiempo(anios, largo=8.5):
    from manim import BOLD

    linea = Line(LEFT * largo / 2, RIGHT * largo / 2, color=GRIS, stroke_width=3)
    puntos, etiquetas = VGroup(), VGroup()
    for i, anio in enumerate(anios):
        p = linea.point_from_proportion(i / (len(anios) - 1))
        puntos.add(Dot(p, color=ROJO, radius=0.1))
        etiquetas.add(texto(str(anio), 22, weight=BOLD).next_to(p, DOWN, buff=0.22))
    return VGroup(linea, puntos, etiquetas), linea, puntos, etiquetas


def arbolito(ancho=2.0, alto=1.5):
    """Árbol de decisión binario (profundidad 2) para explicar XGBoost."""
    raiz = np.array([0, alto / 2, 0])
    izq = np.array([-ancho / 4, 0, 0])
    der = np.array([ancho / 4, 0, 0])
    hojas_pos = [
        np.array([x, -alto / 2, 0])
        for x in (-3 * ancho / 8, -ancho / 8, ancho / 8, 3 * ancho / 8)
    ]
    aristas = VGroup(
        Line(raiz, izq), Line(raiz, der),
        Line(izq, hojas_pos[0]), Line(izq, hojas_pos[1]),
        Line(der, hojas_pos[2]), Line(der, hojas_pos[3]),
    )
    aristas.set_stroke(GRIS, 3)
    nodos = VGroup(
        Dot(raiz, radius=0.09, color=BLACK),
        Dot(izq, radius=0.07, color=BLACK),
        Dot(der, radius=0.07, color=BLACK),
    )
    hojas = VGroup(*[
        RoundedRectangle(
            corner_radius=0.06, width=0.36, height=0.3,
            stroke_color=GRIS, stroke_width=2.5,
            fill_color=WHITE, fill_opacity=1.0,
        ).move_to(p + DOWN * 0.08)
        for p in hojas_pos
    ])
    return VGroup(aristas, nodos, hojas), aristas, hojas
