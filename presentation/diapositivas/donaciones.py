"""¿Para qué se usan las donaciones? Usos clínicos y dependencia del sistema."""

from manim import BOLD, DOWN, LEFT, NORMAL, RIGHT, UP, BLACK, FadeIn, GrowFromCenter

from animaciones import aparecer_uno_a_uno
from componentes import imagen, parrafo, tarjeta, titulo, vinetas
from estilo import ROJO


def construir(scene):
    encabezado = titulo("¿Para qué se usan las donaciones?")

    patient = imagen("patient").scale_to_fit_height(5.0)
    patient.to_edge(RIGHT, buff=0.8).shift(DOWN * 0.4)

    items = vinetas([
        "Intervenciones quirúrgicas",
        "Tratamientos de cáncer",
        "Trasplantes de órganos",
        "Accidentes y emergencias graves",
    ])
    items.next_to(encabezado, DOWN, buff=1.0).to_edge(LEFT, buff=1.0)

    mensaje = parrafo([
        ("El sistema depende", 26, BLACK, NORMAL),
        ("100% de las donaciones:", 30, ROJO, BOLD),
        ("la sangre no se puede fabricar", 26, BLACK, NORMAL),
    ], buff=0.12, alinear=LEFT)
    mensaje.next_to(items, DOWN, buff=0.7).align_to(items, LEFT)

    vidas = tarjeta(
        [("1 donación puede salvar hasta 3 vidas", 22, BOLD)], escala=0.9,
    ).to_edge(DOWN, buff=0.55).match_x(patient)

    scene.play(
        FadeIn(encabezado, shift=DOWN * 0.2),
        FadeIn(patient, shift=LEFT * 0.2),
        run_time=1.0,
    )
    aparecer_uno_a_uno(scene, items)
    scene.play(FadeIn(mensaje, shift=UP * 0.2), run_time=0.8)
    scene.play(GrowFromCenter(vidas), run_time=0.5)
    scene.wait(0.5)

    scene.next_slide()
