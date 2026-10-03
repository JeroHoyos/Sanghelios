"""Presentación Sanghelios.

Orquestador delgado: el estilo vive en ``estilo.py``, las fábricas de
mobjects en ``componentes.py``, los helpers de animación en
``animaciones.py`` y cada diapositiva en su archivo de ``diapositivas/``.
Las diapositivas se agrupan en mixins temáticos (``Slides*``) que aportan
los métodos ``slide_*`` invocados desde ``construct``.

Renderizar:  uv run manim-slides render main.py presentation
"""

from manim import WHITE
from manim_slides import Slide

from componentes import marco
from diapositivas import (
    SlideBase,
    SlidesEquipo,
    SlidesInicio,
    SlidesProblema,
    SlidesSolucion,
)


class presentation(
    SlidesInicio,
    SlidesProblema,
    SlidesSolucion,
    SlidesEquipo,
    SlideBase,
    Slide,
):
    def construct(self):
        self._slide_actual = 0
        self._TOTAL_SLIDES = 13
        self.camera.background_color = WHITE
        self.marco = marco()
        self.add(self.marco)

        self.slide_portada()

        self.slide_donaciones()
        self.slide_noticias()
        self.slide_cifras()
        self.slide_datos()

        self.slide_pregunta()

        self.slide_modulos()
        self.slide_modelo()
        self.slide_demo()
        self.slide_escalabilidad()

        self.slide_equipo()
        self.slide_cierre()
