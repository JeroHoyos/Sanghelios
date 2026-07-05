"""La pregunta que guía el proyecto, en grande y en negrita."""

from manim import BOLD, DOWN, LEFT, RIGHT, UP, FadeIn, Flash, VGroup

from componentes import imagen, texto
from estilo import GRIS, ROJO


def construir(scene):
    kicker = texto("Esto nos llevó a hacernos una pregunta", 22, color=GRIS)

    pregunta = VGroup(
        texto("¿Cómo podemos adelantarnos", 42, weight=BOLD),
        texto("a la escasez de sangre", 46, color=ROJO, weight=BOLD),
        texto("antes de que ponga en riesgo", 42, weight=BOLD),
        texto("la vida de un paciente?", 46, color=ROJO, weight=BOLD),
    ).arrange(DOWN, buff=0.32)

    VGroup(kicker, pregunta).arrange(DOWN, buff=0.75)

    marca_agua = texto("?", 340, color=ROJO, weight=BOLD)
    marca_agua.set_opacity(0.07).to_edge(RIGHT, buff=1.1)

    hearthand = imagen("hearthand", 0.8).to_corner(DOWN + LEFT, buff=0.25).shift(UP * 0.35)
    blood = imagen("blood", 0.8).to_corner(DOWN + RIGHT, buff=0.25).shift(UP * 0.35)

    scene.play(
        FadeIn(kicker, shift=DOWN * 0.15),
        FadeIn(marca_agua, scale=0.9),
        FadeIn(hearthand, shift=RIGHT * 0.2),
        FadeIn(blood, shift=LEFT * 0.2),
        run_time=0.7,
    )
    for linea in pregunta:
        scene.play(FadeIn(linea, shift=UP * 0.15), run_time=0.55)
    scene.play(Flash(pregunta[-1], color=ROJO, line_length=0.3), run_time=0.6)
    scene.wait(0.5)

    scene.next_slide()
