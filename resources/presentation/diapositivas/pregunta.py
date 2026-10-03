"""La pregunta que guía el proyecto, en grande y en negrita."""

from manim import (
    BOLD,
    DOWN,
    LEFT,
    ORIGIN,
    RIGHT,
    UP,
    Create,
    FadeIn,
    Flash,
    Line,
    VGroup,
)

from componentes import texto
from estilo import GRIS, ROJO


def construir(scene):
    # "?" gigante muy tenue, centrado detrás del texto
    marca_agua = texto("?", 460, color=ROJO, weight=BOLD)
    marca_agua.set_opacity(0.11).move_to(ORIGIN).shift(UP * 0.1)

    # Kicker flanqueado por dos rayitas rojas
    kicker = VGroup(
        Line(LEFT * 0.9, ORIGIN, color=ROJO, stroke_width=3),
        texto("Esto nos llevó a hacernos una pregunta", 22, color=GRIS),
        Line(ORIGIN, RIGHT * 0.9, color=ROJO, stroke_width=3),
    ).arrange(RIGHT, buff=0.35)

    pregunta = VGroup(
        texto("¿Cómo podemos adelantarnos", 44, weight=BOLD),
        texto("a la escasez de sangre", 52, color=ROJO, weight=BOLD),
        texto("antes de que ponga en riesgo", 44, weight=BOLD),
        texto("la vida de un paciente?", 52, color=ROJO, weight=BOLD),
    ).arrange(DOWN, buff=0.34)

    subrayado = Line(LEFT * 2.9, RIGHT * 2.9, color=ROJO, stroke_width=5)

    bloque = VGroup(kicker, pregunta, subrayado)
    bloque.arrange(DOWN, buff=0.55).move_to(ORIGIN)

    scene.play(
        FadeIn(marca_agua, scale=1.08),
        FadeIn(kicker, shift=DOWN * 0.15),
        run_time=0.8,
    )
    for linea in pregunta:
        scene.play(FadeIn(linea, shift=UP * 0.15), run_time=0.5)
    scene.play(Create(subrayado), run_time=0.6)
    scene.play(Flash(pregunta[-1], color=ROJO, line_length=0.3), run_time=0.6)
    scene.wait(0.5)

    scene.next_slide()
