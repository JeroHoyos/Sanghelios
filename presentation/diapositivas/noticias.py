"""El país sufre escasez de sangre: recortes de prensa, uno tras otro."""

from manim import DOWN, FadeIn, FadeOut, config

from componentes import imagen, titulo


def construir(scene):
    encabezado = titulo("El país sufre escasez de sangre")
    nombres = ["news/citytv", "news/teleantioquia", "news/telemedellin", "news/sillavacia"]
    max_alto = config.frame_height - 3.0
    max_ancho = config.frame_width - 1.6

    scene.play(FadeIn(encabezado, shift=DOWN * 0.2), run_time=0.8)

    anterior = None
    for nombre in nombres:
        img = imagen(nombre).scale_to_fit_height(max_alto)
        if img.width > max_ancho:
            img.scale_to_fit_width(max_ancho)
        img.next_to(encabezado, DOWN, buff=0.5)

        if anterior is None:
            scene.play(FadeIn(img, scale=0.9), run_time=0.5)
        else:
            scene.play(FadeOut(anterior, scale=0.9), FadeIn(img, scale=0.9), run_time=0.5)
        scene.wait(0.8)
        anterior = img

    scene.wait(0.3)
    scene.next_slide()
