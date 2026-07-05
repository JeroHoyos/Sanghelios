"""Cierre: la frase final y los logos de Sanghelios y MinTIC."""

from manim import (
    BOLD,
    DOWN,
    LEFT,
    RIGHT,
    UP,
    Create,
    FadeIn,
    Flash,
    Group,
    Line,
    VGroup,
)

from componentes import imagen, texto
from estilo import GRIS, ROJO


def construir(scene):
    frase = VGroup(
        texto("Porque en el sistema de salud,", 42, weight=BOLD),
        texto("el tiempo es vida.", 54, color=ROJO, weight=BOLD),
    ).arrange(DOWN, buff=0.42).shift(UP * 0.9)

    gota_izq = imagen("blood", 0.55).next_to(frase, LEFT, buff=0.7)
    gota_der = imagen("blood", 0.55).next_to(frase, RIGHT, buff=0.7)

    gracias = texto("Gracias", 36, color=GRIS).next_to(frase, DOWN, buff=0.6)

    separador = Line(LEFT * 4.6, RIGHT * 4.6, color=ROJO, stroke_width=3)
    separador.next_to(gracias, DOWN, buff=0.5)

    logo_sang = imagen("logo-blanco").scale_to_fit_height(1.55)
    logo_mintic = imagen("mintic").scale_to_fit_height(1.05)
    logos = Group(logo_sang, logo_mintic).arrange(RIGHT, buff=1.5)
    logos.to_edge(DOWN, buff=0.55)

    scene.play(FadeIn(frase[0], shift=UP * 0.15), run_time=0.8)
    scene.play(
        FadeIn(frase[1], shift=UP * 0.15),
        FadeIn(gota_izq, shift=RIGHT * 0.2),
        FadeIn(gota_der, shift=LEFT * 0.2),
        run_time=0.8,
    )
    scene.play(Flash(frase[1], color=ROJO, line_length=0.35), run_time=0.6)
    scene.play(
        FadeIn(gracias),
        Create(separador),
        FadeIn(logo_sang, shift=UP * 0.15),
        FadeIn(logo_mintic, shift=UP * 0.15),
        run_time=0.9,
    )
    scene.wait(0.5)

    scene.next_slide()
