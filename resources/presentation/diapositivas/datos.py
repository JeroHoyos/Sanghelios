"""Datos oficiales del HGM: conteos por dataset y línea de tiempo 2020-2025."""

from manim import BOLD, DOWN, LEFT, RIGHT, UP, Create, FadeIn, VGroup

from animaciones import animar_linea_tiempo, aparecer_uno_a_uno
from componentes import enmarcar, imagen, linea_tiempo, texto, titulo, vinetas
from estilo import GRIS, ROJO


def construir(scene):
    encabezado = titulo("Analizamos datos oficiales del Hospital General de Medellín")

    hospital = imagen("hospital_general").scale_to_fit_height(3.4)
    hospital.to_edge(LEFT, buff=1.0).shift(UP * 0.3)
    marco_foto = enmarcar(hospital)

    rotulo = texto("Registros analizados:", 26, color=ROJO, weight=BOLD)
    registros = vinetas([
        "Banco de sangre · 35.840 registros",
        "Población atendida · 221.203 registros",
        "Defunciones · 5.094 registros",
    ], tam=24, buff=0.35)
    bloque = VGroup(rotulo, registros).arrange(DOWN, buff=0.4, aligned_edge=LEFT)
    bloque.next_to(hospital, RIGHT, buff=1.0).align_to(hospital, UP)

    linea_g, linea, puntos, etiquetas = linea_tiempo([2020, 2021, 2022, 2023, 2024, 2025])
    linea_g.to_edge(DOWN, buff=1.1)

    fuente = texto("Fuente: datos.gov.co", 16, color=GRIS).to_edge(DOWN, buff=0.35)

    scene.play(FadeIn(encabezado, shift=DOWN * 0.2), run_time=0.8)
    scene.play(
        FadeIn(hospital, shift=RIGHT * 0.2),
        Create(marco_foto),
        run_time=1.0,
    )
    scene.play(FadeIn(rotulo, shift=RIGHT * 0.2), run_time=0.5)
    aparecer_uno_a_uno(scene, registros)
    animar_linea_tiempo(scene, linea, puntos, etiquetas)
    scene.play(FadeIn(fuente), run_time=0.4)
    scene.wait(0.5)
    scene.next_slide()
