from manim import *
from manim_slides import Slide
import numpy as np
import os

ROJO = "#ad211a"
GRIS = "#9aa0a6"
FONT = "Arial"
ASSETS = "assets"
ESCALA_TITULO = 0.9
UMBRAL = 50


class presentation(Slide):
    def construct(self):
        self.camera.background_color = WHITE
        self.marco = self._marco()
        self.add(self.marco)

        self.slide_presentacion()
        self._limpiar_pantalla()
        self.slide_donaciones()
        self._limpiar_pantalla()
        self.slide_noticias()

    def _marco(self):
        return Rectangle(
            width=config.frame_width - 0.22,
            height=config.frame_height - 0.22,
            stroke_color=ROJO,
            stroke_width=8,
            fill_opacity=0,
        )

    def _imagen(self, nombre, escala):
        return ImageMobject(os.path.join(ASSETS, f"{nombre}.png")).scale(escala)

    def _tarjeta(self, lineas, ancho_extra=0.7, alto_extra=0.4, escala=1.0):
        textos = VGroup(*[
            Text(t, font=FONT, font_size=fs, color=WHITE, weight=w)
            for t, fs, w in lineas
        ]).arrange(DOWN, buff=0.1)
        fondo = RoundedRectangle(
            corner_radius=0.14,
            width=textos.width + ancho_extra,
            height=textos.height + alto_extra,
            fill_color=ROJO,
            fill_opacity=1.0,
            stroke_width=0,
        )
        return VGroup(fondo, textos).scale(escala)

    def _limpiar_pantalla(self):
        resto = [m for m in self.mobjects if m is not self.marco]
        for m in resto:
            m.clear_updaters()
        if resto:
            self.play(*[FadeOut(m) for m in resto])

    def slide_presentacion(self):
        logo = self._imagen("logo", 1.3).to_edge(UP, buff=0.5)
        hearthand = self._imagen("hearthand", 0.8).to_corner(DL, buff=0.25).shift(UP * 0.35)
        blood = self._imagen("blood", 0.8).to_corner(DR, buff=0.25).shift(UP * 0.35)

        axes = Axes(
            x_range=[0, 12, 1],
            y_range=[0, 100, 20],
            x_length=9.0,
            y_length=3.6,
            axis_config={"stroke_width": 0, "include_tip": False, "include_ticks": False},
        ).shift(DOWN * 0.5)

        eje_x = Line(axes.c2p(0, 0), axes.c2p(12, 0), color=GRIS, stroke_width=2)
        eje_y = Line(axes.c2p(0, 0), axes.c2p(0, 100), color=GRIS, stroke_width=2)

        rng = np.random.default_rng(7)
        x_nodes = np.linspace(0, 12, 60)
        y_nodes = 20 + 4.8 * x_nodes + 6 * np.sin(x_nodes * 0.8 + 0.3)
        y_nodes += rng.normal(0, 2.2, x_nodes.size)

        def presion(x):
            return float(np.interp(x, x_nodes, y_nodes))

        primer_cruce = x_nodes[np.argmax(y_nodes > UMBRAL)] if (y_nodes > UMBRAL).any() else 12.0

        umbral_graph = axes.plot(lambda x: UMBRAL, x_range=[0, 12])
        umbral_line = DashedLine(
            axes.c2p(0, UMBRAL), axes.c2p(12, UMBRAL),
            color=ROJO, dash_length=0.14, stroke_width=2.0,
        )
        umbral_lbl = Text("Umbral escasez", font=FONT, font_size=15, color=ROJO)
        umbral_lbl.move_to(axes.c2p(2.4, UMBRAL) + UP * 0.24)

        x_tracker = ValueTracker(0.0)

        def linea(x0, x1, stroke):
            if x1 <= x0 + 0.02:
                return VGroup()
            return axes.plot(presion, x_range=[x0, x1, 0.02], color=ROJO, stroke_width=stroke)

        def area(x0, x1, opacity):
            if x1 <= x0 + 0.02:
                return VGroup()
            curva = axes.plot(presion, x_range=[x0, x1, 0.02])
            return axes.get_area(
                curva, x_range=[x0, x1], color=ROJO,
                opacity=opacity, bounded_graph=umbral_graph,
            )

        def segmento(x0_fn, x1_fn, opacity, stroke):
            fill = always_redraw(lambda: area(x0_fn(), x1_fn(), opacity))
            curva = always_redraw(lambda: linea(x0_fn(), x1_fn(), stroke))
            return fill, curva

        zona_segura = segmento(lambda: 0, lambda: min(x_tracker.get_value(), primer_cruce), 0.15, 3.0)
        zona_escasez = segmento(lambda: primer_cruce, lambda: x_tracker.get_value(), 0.28, 3.8)

        cruce_dot = Dot(axes.c2p(primer_cruce, UMBRAL), color=ROJO, radius=0.07)
        excl = Text("!", font=FONT, font_size=80, color=ROJO, weight=BOLD)
        excl.next_to(cruce_dot, UP, buff=0.15)

        self.play(
            FadeIn(logo),
            FadeIn(hearthand, shift=RIGHT * 0.2),
            FadeIn(blood, shift=LEFT * 0.2),
            Create(eje_x),
            Create(eje_y),
            Create(umbral_line),
            FadeIn(umbral_lbl),
            run_time=1.6,
        )
        self.add(*zona_segura, *zona_escasez)

        self.play(x_tracker.animate.set_value(primer_cruce), run_time=2.0, rate_func=linear)
        self.play(
            FadeIn(cruce_dot, scale=0.4),
            GrowFromCenter(excl),
            Flash(excl, color=ROJO, line_length=0.3),
            run_time=0.6,
        )
        self.play(x_tracker.animate.set_value(12), run_time=1.8, rate_func=linear)
        self.wait(0.5)

        self.next_slide()

    def slide_donaciones(self):
        titulo = self._tarjeta(
            [("¿Para qué se usan las donaciones?", 28, BOLD)],
            escala=ESCALA_TITULO,
        ).to_edge(UP, buff=0.6)

        patient = self._imagen("patient", 1.0).scale_to_fit_height(5.0)
        patient.to_edge(RIGHT, buff=0.8).shift(DOWN * 0.4)

        usos = [
            "Intervenciones quirúrgicas",
            "Tratamientos de cáncer",
            "Trasplantes de órganos",
            "Accidentes y emergencias graves",
        ]
        items = VGroup()
        for texto in usos:
            punto = Dot(radius=0.07, color=ROJO)
            etiqueta = Text(texto, font=FONT, font_size=26, color=BLACK)
            items.add(VGroup(punto, etiqueta).arrange(RIGHT, buff=0.25))
        items.arrange(DOWN, buff=0.45, aligned_edge=LEFT)
        items.next_to(titulo, DOWN, buff=1.5).to_edge(LEFT, buff=1.0)

        self.play(
            FadeIn(titulo, shift=DOWN * 0.2),
            FadeIn(patient, shift=LEFT * 0.2),
            run_time=1.0,
        )
        for fila in items:
            self.play(FadeIn(fila, shift=RIGHT * 0.2), run_time=0.4)
        self.wait(0.5)

        self.next_slide()

    def slide_noticias(self):
        titulo = self._tarjeta(
            [("El país sufre escasez de sangre", 28, BOLD)],
            escala=ESCALA_TITULO,
        ).to_edge(UP, buff=0.6)

        nombres = ["news/citytv", "news/teleantioquia", "news/telemedellin", "news/sillavacia"]
        max_alto = config.frame_height - 3.0
        max_ancho = config.frame_width - 1.6

        self.play(FadeIn(titulo, shift=DOWN * 0.2), run_time=0.8)

        anterior = None
        for n in nombres:
            img = self._imagen(n, 1.0).scale_to_fit_height(max_alto)
            if img.width > max_ancho:
                img.scale_to_fit_width(max_ancho)
            img.next_to(titulo, DOWN, buff=0.5)

            if anterior is None:
                self.play(FadeIn(img, scale=0.9), run_time=0.5)
            else:
                self.play(
                    FadeOut(anterior, scale=0.9),
                    FadeIn(img, scale=0.9),
                    run_time=0.5,
                )
            self.wait(0.8)
            anterior = img

        self.wait(0.3)
        self.next_slide()
