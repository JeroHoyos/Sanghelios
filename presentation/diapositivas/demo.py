"""Demo: el video del prototipo reproducido dentro de un mockup de navegador.

Coloca la grabación de pantalla de la web en ``assets/demo.mp4`` y la
diapositiva la incrusta (fotogramas extraídos con ffmpeg a ``media/``).
Si el archivo no existe, se muestra la pantalla de carga como señal
para reproducir el video por fuera.
"""

import glob
import os
import shutil
import subprocess

import numpy as np
from manim import (
    BOLD,
    DOWN,
    RIGHT,
    UP,
    AddTextLetterByLetter,
    Create,
    Dot,
    FadeIn,
    Flash,
    Rectangle,
    RoundedRectangle,
    ValueTracker,
    VGroup,
    WHITE,
    always_redraw,
)
from PIL import Image

from componentes import imagen, texto, titulo
from estilo import ASSETS, GRIS, ROJO

VIDEO = os.path.join(ASSETS, "demo.mp4")
FRAMES_DIR = os.path.join("media", "demo_frames")
FPS = 12          # fotogramas por segundo extraídos del video
ANCHO_PX = 1080   # ancho en píxeles de cada fotograma


def _extraer_frames():
    """Extrae el video a PNGs (cacheado por firma del archivo fuente)."""
    marca = os.path.join(FRAMES_DIR, "fuente.txt")
    firma = f"{os.path.getmtime(VIDEO)}-{os.path.getsize(VIDEO)}-{FPS}-{ANCHO_PX}"
    if os.path.exists(marca):
        with open(marca) as f:
            if f.read() == firma:
                rutas = sorted(glob.glob(os.path.join(FRAMES_DIR, "f_*.png")))
                if rutas:
                    return rutas
    shutil.rmtree(FRAMES_DIR, ignore_errors=True)
    os.makedirs(FRAMES_DIR)
    subprocess.run(
        [
            "ffmpeg", "-y", "-loglevel", "error", "-i", VIDEO,
            "-vf", f"fps={FPS},scale={ANCHO_PX}:-2",
            os.path.join(FRAMES_DIR, "f_%05d.png"),
        ],
        check=True,
    )
    with open(marca, "w") as f:
        f.write(firma)
    return sorted(glob.glob(os.path.join(FRAMES_DIR, "f_*.png")))


def _reproducir_video(scene, rutas, centro, ancho_max, alto_max):
    """Muestra los fotogramas en secuencia dentro del área dada."""
    from manim import ImageMobject

    pantalla = ImageMobject(rutas[0])
    pantalla.scale_to_fit_width(ancho_max)
    if pantalla.height > alto_max:
        pantalla.scale_to_fit_height(alto_max)
    pantalla.move_to(centro)

    scene.play(FadeIn(pantalla, scale=0.98), run_time=0.5)

    pantalla.tiempo = 0.0
    pantalla.idx = 0

    def _avanzar(mob, dt):
        mob.tiempo += dt
        idx = min(int(mob.tiempo * FPS), len(rutas) - 1)
        if idx != mob.idx:
            mob.idx = idx
            mob.pixel_array = np.asarray(
                Image.open(rutas[idx]).convert("RGBA"), dtype=np.uint8,
            )

    pantalla.add_updater(_avanzar)
    scene.wait(len(rutas) / FPS)
    pantalla.remove_updater(_avanzar)


def construir(scene):
    encabezado = titulo("Veámoslo en vivo")

    # ── Ventana de navegador ──
    ancho_v, alto_v = 9.6, 4.9
    centro = np.array([0.0, -0.5, 0.0])
    ventana = RoundedRectangle(
        corner_radius=0.18, width=ancho_v, height=alto_v,
        stroke_color=GRIS, stroke_width=4, fill_color=WHITE, fill_opacity=1.0,
    ).move_to(centro)
    barra_sup = Rectangle(
        width=ancho_v - 0.08, height=0.62,
        fill_color="#F6EFE4", fill_opacity=1.0, stroke_width=0,
    ).move_to(centro + UP * (alto_v / 2 - 0.35))
    botones = VGroup(
        Dot(radius=0.07, color=ROJO),
        Dot(radius=0.07, color=GRIS),
        Dot(radius=0.07, color="#d8d2c7"),
    ).arrange(RIGHT, buff=0.14).move_to(barra_sup.get_left() + RIGHT * 0.55)

    pildora = RoundedRectangle(
        corner_radius=0.16, width=3.9, height=0.42,
        stroke_color=GRIS, stroke_width=2.5, fill_color=WHITE, fill_opacity=1.0,
    ).move_to(barra_sup.get_center())
    url = texto("www.sanghelios.com", 17, color=ROJO, weight=BOLD)
    url.move_to(pildora.get_center())

    scene.play(FadeIn(encabezado, shift=DOWN * 0.2), run_time=0.7)
    scene.play(
        Create(ventana), FadeIn(barra_sup), FadeIn(botones),
        run_time=0.9,
    )
    scene.play(FadeIn(pildora), run_time=0.4)
    scene.play(AddTextLetterByLetter(url), run_time=1.3)
    scene.play(Flash(pildora, color=ROJO, line_length=0.2), run_time=0.5)

    # ── Contenido: video de la demo (o pantalla de carga si no hay video) ──
    centro_contenido = centro + DOWN * 0.31
    if os.path.exists(VIDEO):
        rutas = _extraer_frames()
        _reproducir_video(
            scene, rutas, centro_contenido,
            ancho_max=ancho_v - 0.35, alto_max=alto_v - 0.62 - 0.35,
        )
    else:
        logo = imagen("logo-blanco").scale_to_fit_height(1.35).move_to(centro + UP * 0.55)
        cargando = texto("Iniciando la demo de la web…", 18, color=GRIS)
        cargando.move_to(centro + DOWN * 0.55)

        track = RoundedRectangle(
            corner_radius=0.13, width=4.6, height=0.3,
            stroke_color=GRIS, stroke_width=2.5, fill_color=WHITE, fill_opacity=1.0,
        ).move_to(centro + DOWN * 1.15)
        avance = ValueTracker(0.0)
        borde_izq = track.get_left() + RIGHT * 0.05

        def _fill():
            ancho = max(avance.get_value() * 4.5, 0.001)
            return Rectangle(
                width=ancho, height=0.18,
                fill_color=ROJO, fill_opacity=0.92, stroke_width=0,
            ).move_to(borde_izq + RIGHT * ancho / 2)

        fill = always_redraw(_fill)

        scene.play(FadeIn(logo, scale=0.9), FadeIn(cargando), FadeIn(track), run_time=0.7)
        scene.add(fill)
        scene.play(avance.animate.set_value(1.0), run_time=1.8)

    scene.wait(0.5)
    scene.next_slide()
