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

        slides = [
            self.slide_presentacion,
            self.slide_donaciones,
            self.slide_noticias,
            self.slide_cifras,
            self.slide_datos,
        ]
        for i, slide in enumerate(slides):
            if i > 0:
                self._limpiar_pantalla()
            slide()

    # ----- Fábricas de mobjects -----

    def _marco(self):
        return Rectangle(
            width=config.frame_width - 0.22,
            height=config.frame_height - 0.22,
            stroke_color=ROJO,
            stroke_width=8,
            fill_opacity=0,
        )

    def _imagen(self, nombre, escala=1.0):
        return ImageMobject(os.path.join(ASSETS, f"{nombre}.png")).scale(escala)

    def _texto(self, texto, tam, color=BLACK, weight=NORMAL):
        return Text(texto, font=FONT, font_size=tam, color=color, weight=weight)

    def _parrafo(self, lineas, buff=0.15, alinear=ORIGIN):
        textos = [self._texto(*linea) for linea in lineas]
        return VGroup(*textos).arrange(DOWN, buff=buff, aligned_edge=alinear)

    def _tarjeta(self, lineas, ancho_extra=0.7, alto_extra=0.4, escala=1.0):
        textos = VGroup(*[
            self._texto(t, fs, color=WHITE, weight=w) for t, fs, w in lineas
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

    def _titulo(self, texto):
        tarjeta = self._tarjeta([(texto, 28, BOLD)], escala=ESCALA_TITULO)
        return tarjeta.to_edge(UP, buff=0.6)

    def _vinetas(self, textos, tam=26, buff=0.45):
        filas = VGroup()
        for texto in textos:
            punto = Dot(radius=0.07, color=ROJO)
            filas.add(VGroup(punto, self._texto(texto, tam)).arrange(RIGHT, buff=0.25))
        return filas.arrange(DOWN, buff=buff, aligned_edge=LEFT)

    def _reloj(self, radio=1.15):
        cara = Circle(
            radius=radio, color=ROJO, stroke_width=6,
            fill_color=WHITE, fill_opacity=1.0,
        )
        centro = cara.get_center()
        marcas = VGroup(*[
            Line(
                centro + radio * 0.82 * self._direccion(i),
                centro + radio * 0.96 * self._direccion(i),
                color=GRIS, stroke_width=3,
            )
            for i in range(12)
        ])
        horario = Line(centro, centro + radio * 0.5 * UP, color=BLACK, stroke_width=7)
        minutero = Line(centro, centro + radio * 0.78 * UP, color=ROJO, stroke_width=4)
        eje = Dot(centro, radius=0.06, color=BLACK)
        reloj = VGroup(cara, marcas, horario, minutero, eje)
        return reloj, horario, minutero

    def _direccion(self, hora):
        ang = PI / 2 - hora * TAU / 12
        return np.array([np.cos(ang), np.sin(ang), 0])

    def _calendario(self, ancho=2.6, alto=2.6, cols=7, filas=4):
        cuerpo = RoundedRectangle(
            width=ancho, height=alto, corner_radius=0.14,
            stroke_color=ROJO, stroke_width=5,
            fill_color=WHITE, fill_opacity=1.0,
        )
        encabezado = RoundedRectangle(
            width=ancho, height=alto * 0.26, corner_radius=0.14,
            fill_color=ROJO, fill_opacity=1.0, stroke_width=0,
        ).align_to(cuerpo, UP)
        anillas = VGroup(*[
            Line(UP * 0.16, DOWN * 0.16, color=GRIS, stroke_width=5) for _ in range(2)
        ]).arrange(RIGHT, buff=ancho * 0.4).move_to(encabezado.get_top())

        celda = ancho / (cols + 1)
        rejilla = VGroup(*[
            Square(side_length=celda * 0.78, stroke_color=GRIS, stroke_width=1.5, fill_opacity=0)
            for _ in range(cols * filas)
        ])
        rejilla.arrange_in_grid(rows=filas, cols=cols, buff=celda * 0.22)
        rejilla.next_to(encabezado, DOWN, buff=0.16)

        calendario = VGroup(cuerpo, encabezado, anillas, rejilla)
        return calendario, rejilla

    def _enmarcar(self, img, margen=0.12):
        return RoundedRectangle(
            width=img.width + margen, height=img.height + margen,
            corner_radius=0.14, stroke_color=ROJO, stroke_width=5, fill_opacity=0,
        ).move_to(img.get_center())

    def _linea_tiempo(self, anios, largo=8.5):
        linea = Line(LEFT * largo / 2, RIGHT * largo / 2, color=GRIS, stroke_width=3)
        puntos, etiquetas = VGroup(), VGroup()
        for i, anio in enumerate(anios):
            p = linea.point_from_proportion(i / (len(anios) - 1))
            puntos.add(Dot(p, color=ROJO, radius=0.1))
            etiquetas.add(self._texto(str(anio), 22, weight=BOLD).next_to(p, DOWN, buff=0.22))
        return VGroup(linea, puntos, etiquetas), linea, puntos, etiquetas

    # ----- Helpers de animación -----

    def _limpiar_pantalla(self):
        resto = [m for m in self.mobjects if m is not self.marco]
        for m in resto:
            m.clear_updaters()
        if resto:
            self.play(*[FadeOut(m) for m in resto])

    def _aparecer_uno_a_uno(self, grupo, run_time=0.4):
        for elemento in grupo:
            self.play(FadeIn(elemento, shift=RIGHT * 0.2), run_time=run_time)

    def _animar_reloj(self, reloj, horario, minutero):
        cara = VGroup(*[m for m in reloj if m not in (horario, minutero)])
        centro = reloj[0].get_center()
        self.play(FadeIn(cara, scale=0.85), run_time=0.6)
        self.play(GrowFromCenter(horario), GrowFromCenter(minutero), run_time=0.4)
        self.play(
            Rotate(minutero, angle=-TAU, about_point=centro),
            Rotate(horario, angle=-TAU / 12, about_point=centro),
            run_time=1.6, rate_func=linear,
        )

    def _animar_calendario(self, calendario, rejilla):
        cuerpo = VGroup(*[m for m in calendario if m is not rejilla])
        self.play(FadeIn(cuerpo, scale=0.85), run_time=0.6)
        self.play(
            LaggedStart(
                *[c.animate.set_fill(ROJO, opacity=0.85) for c in rejilla],
                lag_ratio=0.08,
            ),
            run_time=1.8,
        )

    def _animar_linea_tiempo(self, linea, puntos, etiquetas):
        self.play(Create(linea), run_time=1.0)
        self.play(
            LaggedStart(
                *[
                    AnimationGroup(GrowFromCenter(p), FadeIn(e, shift=DOWN * 0.15))
                    for p, e in zip(puntos, etiquetas)
                ],
                lag_ratio=0.4,
            ),
            run_time=1.8,
        )

    # ----- Diapositivas -----

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

        x_nodes, y_nodes = self._datos_presion()
        presion = lambda x: float(np.interp(x, x_nodes, y_nodes))
        primer_cruce = x_nodes[np.argmax(y_nodes > UMBRAL)] if (y_nodes > UMBRAL).any() else 12.0

        umbral_graph = axes.plot(lambda x: UMBRAL, x_range=[0, 12])
        umbral_line = DashedLine(
            axes.c2p(0, UMBRAL), axes.c2p(12, UMBRAL),
            color=ROJO, dash_length=0.14, stroke_width=2.0,
        )
        umbral_lbl = self._texto("Umbral escasez", 15, color=ROJO)
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
        excl = self._texto("!", 80, color=ROJO, weight=BOLD).next_to(cruce_dot, UP, buff=0.15)

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

    def _datos_presion(self):
        rng = np.random.default_rng(7)
        x = np.linspace(0, 12, 60)
        y = 20 + 4.8 * x + 6 * np.sin(x * 0.8 + 0.3) + rng.normal(0, 2.2, x.size)
        return x, y

    def slide_donaciones(self):
        titulo = self._titulo("¿Para qué se usan las donaciones?")

        patient = self._imagen("patient").scale_to_fit_height(5.0)
        patient.to_edge(RIGHT, buff=0.8).shift(DOWN * 0.4)

        items = self._vinetas([
            "Intervenciones quirúrgicas",
            "Tratamientos de cáncer",
            "Trasplantes de órganos",
            "Accidentes y emergencias graves",
        ])
        items.next_to(titulo, DOWN, buff=1.0).to_edge(LEFT, buff=1.0)

        mensaje = self._parrafo([
            ("El sistema depende", 26, BLACK, NORMAL),
            ("100% de las donaciones:", 30, ROJO, BOLD),
            ("la sangre no se puede fabricar", 26, BLACK, NORMAL),
        ], buff=0.12, alinear=LEFT)
        mensaje.next_to(items, DOWN, buff=0.7).align_to(items, LEFT)

        self.play(
            FadeIn(titulo, shift=DOWN * 0.2),
            FadeIn(patient, shift=LEFT * 0.2),
            run_time=1.0,
        )
        self._aparecer_uno_a_uno(items)
        self.play(FadeIn(mensaje, shift=UP * 0.2), run_time=0.8)
        self.wait(0.5)

        self.next_slide()

    def slide_noticias(self):
        titulo = self._titulo("El país sufre escasez de sangre")
        nombres = ["news/citytv", "news/teleantioquia", "news/telemedellin", "news/sillavacia"]
        max_alto = config.frame_height - 3.0
        max_ancho = config.frame_width - 1.6

        self.play(FadeIn(titulo, shift=DOWN * 0.2), run_time=0.8)

        anterior = None
        for nombre in nombres:
            img = self._imagen(nombre).scale_to_fit_height(max_alto)
            if img.width > max_ancho:
                img.scale_to_fit_width(max_ancho)
            img.next_to(titulo, DOWN, buff=0.5)

            if anterior is None:
                self.play(FadeIn(img, scale=0.9), run_time=0.5)
            else:
                self.play(FadeOut(anterior, scale=0.9), FadeIn(img, scale=0.9), run_time=0.5)
            self.wait(0.8)
            anterior = img

        self.wait(0.3)
        self.next_slide()

    def slide_cifras(self):
        titulo = self._titulo("La demanda de sangre no se detiene")

        reloj, horario, minutero = self._reloj()
        reloj.to_edge(LEFT, buff=2.7).shift(UP * 0.55)
        texto_reloj = self._parrafo([
            ("En promedio cada hora", 24, BLACK, NORMAL),
            ("42 pacientes", 40, ROJO, BOLD),
            ("necesitan sangre en el país", 24, BLACK, NORMAL),
        ]).next_to(reloj, DOWN, buff=0.5)

        calendario, rejilla = self._calendario()
        calendario.to_edge(RIGHT, buff=2.7).match_y(reloj)
        texto_cal = self._parrafo([
            ("Se requieren por lo menos", 24, BLACK, NORMAL),
            ("100 donantes diarios", 40, ROJO, BOLD),
            ("en el departamento", 24, BLACK, NORMAL),
        ]).next_to(calendario, DOWN, buff=0.5).match_y(texto_reloj)

        fuente = self._texto("Fuente: Telemedellín", 16, color=GRIS).to_edge(DOWN, buff=0.35)

        self.play(FadeIn(titulo, shift=DOWN * 0.2), run_time=0.8)

        self._animar_reloj(reloj, horario, minutero)
        self.play(FadeIn(texto_reloj, shift=UP * 0.2), run_time=0.7)

        self._animar_calendario(calendario, rejilla)
        self.play(FadeIn(texto_cal, shift=UP * 0.2), run_time=0.7)

        self.play(FadeIn(fuente), run_time=0.4)
        self.wait(0.5)
        self.next_slide()

    def slide_datos(self):
        titulo = self._titulo("Analizamos datos oficiales del Hospital General de Medellín")

        hospital = self._imagen("hospital_general").scale_to_fit_height(3.4)
        hospital.to_edge(LEFT, buff=1.0).shift(UP * 0.3)
        marco_foto = self._enmarcar(hospital)

        encabezado = self._texto("Registros analizados:", 26, color=ROJO, weight=BOLD)
        registros = self._vinetas([
            "Donaciones de sangre",
            "Población atendida",
            "Defunciones registradas",
        ], tam=24, buff=0.35)
        bloque = VGroup(encabezado, registros).arrange(DOWN, buff=0.4, aligned_edge=LEFT)
        bloque.next_to(hospital, RIGHT, buff=1.0).align_to(hospital, UP)

        linea_tiempo, linea, puntos, etiquetas = self._linea_tiempo([2022, 2023, 2024, 2025, 2026])
        linea_tiempo.to_edge(DOWN, buff=1.1)

        fuente = self._texto("Fuente: datos.gov.co", 16, color=GRIS).to_edge(DOWN, buff=0.35)

        self.play(FadeIn(titulo, shift=DOWN * 0.2), run_time=0.8)
        self.play(
            FadeIn(hospital, shift=RIGHT * 0.2),
            Create(marco_foto),
            run_time=1.0,
        )
        self.play(FadeIn(encabezado, shift=RIGHT * 0.2), run_time=0.5)
        self._aparecer_uno_a_uno(registros)
        self._animar_linea_tiempo(linea, puntos, etiquetas)
        self.play(FadeIn(fuente), run_time=0.4)
        self.wait(0.5)
        self.next_slide()
