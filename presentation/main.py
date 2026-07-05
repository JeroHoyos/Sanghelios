"""Presentación Sanghelios.

Orquestador delgado: el estilo vive en ``estilo.py``, las fábricas de
mobjects en ``componentes.py``, los helpers de animación en
``animaciones.py`` y cada diapositiva en su archivo de ``diapositivas/``.

Renderizar:  uv run manim-slides render main.py presentation
"""

from manim import WHITE
from manim_slides import Slide

from animaciones import limpiar_pantalla
from componentes import marco
from diapositivas import SLIDES


class presentation(Slide):
    def construct(self):
        self.camera.background_color = WHITE
        self.marco = marco()
        self.add(self.marco)

        for i, construir in enumerate(SLIDES):
            if i > 0:
                limpiar_pantalla(self)
            construir(self)
