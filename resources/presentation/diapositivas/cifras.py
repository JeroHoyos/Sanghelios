"""La demanda no se detiene: 42 pacientes/hora y 100 donantes diarios."""

from manim import BOLD, DOWN, NORMAL, RIGHT, UP, BLACK, LEFT, FadeIn

from animaciones import animar_calendario, animar_reloj
from componentes import calendario, parrafo, reloj, texto, titulo
from estilo import GRIS, ROJO


def construir(scene):
    encabezado = titulo("La demanda de sangre no se detiene")

    reloj_g, horario, minutero = reloj()
    reloj_g.to_edge(LEFT, buff=2.7).shift(UP * 0.55)
    texto_reloj = parrafo([
        ("En promedio cada hora", 24, BLACK, NORMAL),
        ("42 pacientes", 40, ROJO, BOLD),
        ("necesitan sangre en el país", 24, BLACK, NORMAL),
    ]).next_to(reloj_g, DOWN, buff=0.5)

    calendario_g, rejilla = calendario()
    calendario_g.to_edge(RIGHT, buff=2.7).match_y(reloj_g)
    texto_cal = parrafo([
        ("Se requieren por lo menos", 24, BLACK, NORMAL),
        ("100 donantes diarios", 40, ROJO, BOLD),
        ("en el departamento", 24, BLACK, NORMAL),
    ]).next_to(calendario_g, DOWN, buff=0.5).match_y(texto_reloj)

    fuente = texto("Fuente: Telemedellín", 16, color=GRIS).to_edge(DOWN, buff=0.35)

    scene.play(FadeIn(encabezado, shift=DOWN * 0.2), run_time=0.8)

    animar_reloj(scene, reloj_g, horario, minutero)
    scene.play(FadeIn(texto_reloj, shift=UP * 0.2), run_time=0.7)

    animar_calendario(scene, calendario_g, rejilla)
    scene.play(FadeIn(texto_cal, shift=UP * 0.2), run_time=0.7)

    scene.play(FadeIn(fuente), run_time=0.4)
    scene.wait(0.5)
    scene.next_slide()
