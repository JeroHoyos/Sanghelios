"""Helpers de animación compartidos: reciben la escena como primer argumento."""

from manim import (
    DOWN,
    RIGHT,
    TAU,
    AnimationGroup,
    FadeIn,
    FadeOut,
    GrowFromCenter,
    LaggedStart,
    Rotate,
    VGroup,
    linear,
)

from estilo import ROJO


def limpiar_pantalla(scene):
    resto = [m for m in scene.mobjects if m is not getattr(scene, "marco", None)]
    for m in resto:
        m.clear_updaters()
    if resto:
        scene.play(*[FadeOut(m) for m in resto])


def aparecer_uno_a_uno(scene, grupo, run_time=0.4):
    for elemento in grupo:
        scene.play(FadeIn(elemento, shift=RIGHT * 0.2), run_time=run_time)


def animar_reloj(scene, reloj, horario, minutero):
    cara = VGroup(*[m for m in reloj if m not in (horario, minutero)])
    centro = reloj[0].get_center()
    scene.play(FadeIn(cara, scale=0.85), run_time=0.6)
    scene.play(GrowFromCenter(horario), GrowFromCenter(minutero), run_time=0.4)
    scene.play(
        Rotate(minutero, angle=-TAU, about_point=centro),
        Rotate(horario, angle=-TAU / 12, about_point=centro),
        run_time=1.6, rate_func=linear,
    )


def animar_calendario(scene, calendario, rejilla):
    cuerpo = VGroup(*[m for m in calendario if m is not rejilla])
    scene.play(FadeIn(cuerpo, scale=0.85), run_time=0.6)
    scene.play(
        LaggedStart(
            *[c.animate.set_fill(ROJO, opacity=0.85) for c in rejilla],
            lag_ratio=0.08,
        ),
        run_time=1.8,
    )


def animar_linea_tiempo(scene, linea, puntos, etiquetas):
    from manim import Create, GrowFromCenter

    scene.play(Create(linea), run_time=1.0)
    scene.play(
        LaggedStart(
            *[
                AnimationGroup(GrowFromCenter(p), FadeIn(e, shift=DOWN * 0.15))
                for p, e in zip(puntos, etiquetas)
            ],
            lag_ratio=0.4,
        ),
        run_time=1.8,
    )
