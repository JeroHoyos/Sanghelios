"""Diapositivas agrupadas en mixins temáticos.

Cada diapositiva vive en su propio archivo como ``construir(scene)``; aquí se
agrupan en mixins que exponen métodos ``slide_<nombre>(self)`` para la clase
principal de ``main.py``. ``SlideBase`` aporta la limpieza de pantalla entre
diapositivas y el contador de avance.
"""

from manim import FadeOut

from . import (
    cierre,
    cifras,
    datos,
    demo,
    donaciones,
    equipo,
    escalabilidad,
    grupo_o,
    modelo,
    modulos,
    noticias,
    portada,
    pregunta,
)


class SlideBase:
    """Estado y utilidades compartidas por todas las diapositivas."""

    def iniciar_slide(self):
        """Limpia la pantalla (salvo el marco) antes de construir la siguiente."""
        self._slide_actual = getattr(self, "_slide_actual", 0) + 1
        resto = [m for m in self.mobjects if m is not getattr(self, "marco", None)]
        for m in resto:
            m.clear_updaters()
        if resto:
            self.play(*[FadeOut(m) for m in resto])


def _slide(construir):
    """Adapta un ``construir(scene)`` a un método de diapositiva (limpia y delega)."""

    def metodo(self):
        self.iniciar_slide()
        construir(self)

    return metodo


class SlidesInicio:
    slide_portada = _slide(portada.construir)


class SlidesProblema:
    slide_donaciones = _slide(donaciones.construir)
    slide_noticias = _slide(noticias.construir)
    slide_cifras = _slide(cifras.construir)
    slide_datos = _slide(datos.construir)
    slide_grupo_o = _slide(grupo_o.construir)
    slide_pregunta = _slide(pregunta.construir)


class SlidesSolucion:
    slide_modulos = _slide(modulos.construir)
    slide_modelo = _slide(modelo.construir)
    slide_demo = _slide(demo.construir)
    slide_escalabilidad = _slide(escalabilidad.construir)


class SlidesEquipo:
    slide_equipo = _slide(equipo.construir)
    slide_cierre = _slide(cierre.construir)
