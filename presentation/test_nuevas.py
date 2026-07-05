"""Escena temporal para probar las diapositivas nuevas (borrar tras la prueba)."""

from manim import WHITE
from manim_slides import Slide

from animaciones import limpiar_pantalla
from componentes import marco
from diapositivas import cierre, escalabilidad, modulos, pregunta


class TestNuevas(Slide):
    def construct(self):
        self.camera.background_color = WHITE
        self.marco = marco()
        self.add(self.marco)
        for i, mod in enumerate([pregunta, modulos, escalabilidad, cierre]):
            if i > 0:
                limpiar_pantalla(self)
            mod.construir(self)
