"""Registro de diapositivas: una por archivo, en orden de presentación."""

from . import (
    cierre,
    cifras,
    datos,
    demo,
    donaciones,
    escalabilidad,
    grupo_o,
    modelo,
    modulos,
    noticias,
    portada,
    pregunta,
)

SLIDES = [
    portada.construir,
    donaciones.construir,
    noticias.construir,
    cifras.construir,
    datos.construir,
    grupo_o.construir,
    pregunta.construir,
    modulos.construir,
    modelo.construir,
    demo.construir,
    escalabilidad.construir,
    cierre.construir,
]
