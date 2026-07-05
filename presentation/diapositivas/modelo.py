"""¿Cómo pronostica el modelo? XGBoost: árboles en cadena que suman una alerta."""

import numpy as np
from manim import (
    BOLD,
    DOWN,
    LEFT,
    NORMAL,
    RIGHT,
    UP,
    BLACK,
    Arrow,
    Axes,
    Create,
    DashedLine,
    DashedVMobject,
    FadeIn,
    Flash,
    GrowArrow,
    GrowFromCenter,
    Line,
    Rectangle,
    RoundedRectangle,
    ValueTracker,
    VGroup,
    VMobject,
    WHITE,
    always_redraw,
)

from componentes import arbolito, tarjeta, texto, vinetas
from componentes import titulo as hacer_titulo
from estilo import GRIS, ROJO


def construir(scene):
    encabezado = hacer_titulo("¿Cómo pronostica el modelo? · XGBoost")

    # ── Fila A: serie reciente → ficha de features · fórmula del boosting ──
    ejes = Axes(
        x_range=[0, 21, 21], y_range=[0, 3, 3],
        x_length=3.4, y_length=1.5,
        axis_config={"stroke_width": 0, "include_ticks": False, "include_tip": False},
    )
    rng = np.random.default_rng(11)
    ys = 1.1 + 0.45 * np.sin(np.arange(22) * 0.55) + np.linspace(0, 0.9, 22) + rng.normal(0, 0.07, 22)
    curva = VMobject(color=ROJO, stroke_width=3.5)
    curva.set_points_smoothly([ejes.c2p(i, y) for i, y in enumerate(ys)])
    base = Line(ejes.c2p(0, 0), ejes.c2p(21, 0), color=GRIS, stroke_width=2)
    serie = VGroup(ejes, base, curva)
    serie.to_edge(LEFT, buff=0.75).shift(UP * 1.42)

    ventana = DashedVMobject(
        RoundedRectangle(
            corner_radius=0.08, width=1.25, height=1.5,
            stroke_color=ROJO, stroke_width=3,
        ),
        num_dashes=38,
    ).move_to(ejes.c2p(17.6, 1.45))
    ventana_lbl = texto("últimos 14 días", 14, color=ROJO, weight=BOLD)
    ventana_lbl.next_to(ventana, UP, buff=0.08)

    chips = vinetas(["lags 1–14", "media móvil 7 días", "mes del año"], tam=15, buff=0.14)
    ficha_titulo = texto("features de hoy", 16, color=ROJO, weight=BOLD)
    ficha_int = VGroup(ficha_titulo, chips).arrange(DOWN, buff=0.18, aligned_edge=LEFT)
    ficha_fondo = RoundedRectangle(
        corner_radius=0.14,
        width=ficha_int.width + 0.5, height=ficha_int.height + 0.42,
        stroke_color=ROJO, stroke_width=4, fill_color=WHITE, fill_opacity=1.0,
    )
    ficha = VGroup(ficha_fondo, ficha_int.move_to(ficha_fondo))
    ficha.next_to(serie, RIGHT, buff=0.9).match_y(serie)

    flecha_ficha = Arrow(
        ventana.get_right(), ficha.get_left(), color=GRIS,
        stroke_width=3, buff=0.12, max_tip_length_to_length_ratio=0.18,
    )

    formula = VGroup(
        texto("ŷ", 30, color=ROJO, weight=BOLD),
        texto("=  f1(x) + f2(x) + f3(x) + …", 24, color=BLACK),
    ).arrange(RIGHT, buff=0.18)
    formula.next_to(ficha, RIGHT, buff=0.75).match_y(ficha)
    formula_nota = texto("una suma de árboles pequeños", 15, color=GRIS)
    formula_nota.next_to(formula, DOWN, buff=0.12).align_to(formula, LEFT)

    # ── Fila B: árboles en cadena, cada uno corrige el error del anterior ──
    centros = [LEFT * 3.6, np.array([0.0, 0.0, 0.0]), RIGHT * 3.6]
    aportes = ["+0.28", "+0.21", "+0.19"]
    arboles, titulos_arb, chips_aporte = [], [], []
    for i, c in enumerate(centros):
        arbol, aristas, hojas = arbolito()
        arbol.move_to(c + DOWN * 0.62)
        arboles.append((arbol, aristas, hojas))
        titulos_arb.append(
            texto(f"árbol {i + 1}", 15, color=GRIS, weight=BOLD)
            .next_to(arbol, UP, buff=0.12)
        )
        chips_aporte.append(
            tarjeta([(aportes[i], 20, BOLD)], escala=0.72)
            .next_to(arbol, DOWN, buff=0.16)
        )
    flechas_res, notas_res = [], []
    for i in range(2):
        flecha = Arrow(
            arboles[i][0].get_right() + RIGHT * 0.05,
            arboles[i + 1][0].get_left() + LEFT * 0.05,
            color=GRIS, stroke_width=3, buff=0.05,
            max_tip_length_to_length_ratio=0.14,
        )
        flechas_res.append(flecha)
        notas_res.append(
            texto("corrige el error", 13, color=GRIS).next_to(flecha, UP, buff=0.06)
        )

    # ── Fila C: la suma llena el medidor de probabilidad hasta la alerta ──
    track = RoundedRectangle(
        corner_radius=0.2, width=6.6, height=0.44,
        stroke_color=GRIS, stroke_width=3, fill_color=WHITE, fill_opacity=1.0,
    )
    track.to_edge(DOWN, buff=1.05).shift(LEFT * 2.2)
    prob = ValueTracker(0.0)
    rel_izq = track.get_left() + RIGHT * 0.06

    def _fill():
        ancho = max(prob.get_value() * 6.48, 0.001)
        return Rectangle(
            width=ancho, height=0.3,
            fill_color=ROJO, fill_opacity=0.92, stroke_width=0,
        ).move_to(rel_izq + RIGHT * ancho / 2)

    fill = always_redraw(_fill)
    corte = 0.62
    x_corte = rel_izq[0] + corte * 6.48
    corte_line = DashedLine(
        np.array([x_corte, track.get_top()[1] + 0.14, 0]),
        np.array([x_corte, track.get_bottom()[1] - 0.14, 0]),
        color=BLACK, stroke_width=2.5, dash_length=0.08,
    )
    corte_lbl = texto("corte de alerta", 14, color=GRIS)
    corte_lbl.next_to(corte_line, UP, buff=0.06)
    corte_lbl.shift(RIGHT * (corte_lbl.width / 2 + 0.1))
    nota_prod = texto("En producción son cientos de árboles en cadena", 14, color=GRIS)
    nota_prod.next_to(track, DOWN, buff=0.14).align_to(track, LEFT)
    prob_lbl = always_redraw(lambda: texto(
        f"P(escasez en 14 días) = {int(round(prob.get_value() * 100))} %",
        18, color=BLACK, weight=BOLD,
    ).next_to(track, UP, buff=0.16).align_to(track, LEFT))

    alerta = tarjeta([
        ("¡Escasez en 14 días!", 22, BOLD),
        ("se activa la campaña de donación", 15, NORMAL),
    ], escala=0.88).next_to(track, RIGHT, buff=0.55)

    # ── Animación ──
    scene.play(FadeIn(encabezado, shift=DOWN * 0.2), run_time=0.7)
    scene.play(Create(base), Create(curva), run_time=1.1)
    scene.play(Create(ventana), FadeIn(ventana_lbl, shift=UP * 0.1), run_time=0.7)
    scene.play(GrowArrow(flecha_ficha), FadeIn(ficha, shift=RIGHT * 0.15), run_time=0.7)
    scene.play(FadeIn(formula, shift=UP * 0.1), FadeIn(formula_nota), run_time=0.6)

    scene.play(
        FadeIn(track), Create(corte_line),
        FadeIn(corte_lbl), FadeIn(nota_prod),
        run_time=0.7,
    )
    scene.add(fill, prob_lbl)

    acumulado = [0.28, 0.49, 0.68]
    rutas = [(0, 3, 1), (1, 4, 2), (1, 5, 3)]  # (arista raíz, arista hoja, hoja)
    for i in range(3):
        arbol, aristas, hojas = arboles[i]
        intro = [FadeIn(arbol, shift=UP * 0.15), FadeIn(titulos_arb[i])]
        if i > 0:
            intro += [GrowArrow(flechas_res[i - 1]), FadeIn(notas_res[i - 1])]
        scene.play(*intro, run_time=0.55)
        arista_a, arista_b, hoja = rutas[i]
        scene.play(aristas[arista_a].animate.set_stroke(ROJO, 6), run_time=0.3)
        scene.play(aristas[arista_b].animate.set_stroke(ROJO, 6), run_time=0.3)
        scene.play(
            hojas[hoja].animate.set_fill(ROJO, opacity=0.92).set_stroke(ROJO, 2.5),
            GrowFromCenter(chips_aporte[i]),
            run_time=0.45,
        )
        scene.play(prob.animate.set_value(acumulado[i]), run_time=0.8)

    scene.play(
        GrowFromCenter(alerta),
        Flash(corte_line, color=ROJO, line_length=0.25),
        run_time=0.7,
    )
    scene.wait(0.6)
    scene.next_slide()
