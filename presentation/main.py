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
            self.slide_grupo_o,
            self.slide_modelo,
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

    def _arbolito(self, ancho=2.0, alto=1.5):
        """Árbol de decisión binario (profundidad 2) para explicar XGBoost."""
        raiz = np.array([0, alto / 2, 0])
        izq = np.array([-ancho / 4, 0, 0])
        der = np.array([ancho / 4, 0, 0])
        hojas_pos = [
            np.array([x, -alto / 2, 0])
            for x in (-3 * ancho / 8, -ancho / 8, ancho / 8, 3 * ancho / 8)
        ]
        aristas = VGroup(
            Line(raiz, izq), Line(raiz, der),
            Line(izq, hojas_pos[0]), Line(izq, hojas_pos[1]),
            Line(der, hojas_pos[2]), Line(der, hojas_pos[3]),
        )
        aristas.set_stroke(GRIS, 3)
        nodos = VGroup(
            Dot(raiz, radius=0.09, color=BLACK),
            Dot(izq, radius=0.07, color=BLACK),
            Dot(der, radius=0.07, color=BLACK),
        )
        hojas = VGroup(*[
            RoundedRectangle(
                corner_radius=0.06, width=0.36, height=0.3,
                stroke_color=GRIS, stroke_width=2.5,
                fill_color=WHITE, fill_opacity=1.0,
            ).move_to(p + DOWN * 0.08)
            for p in hojas_pos
        ])
        return VGroup(aristas, nodos, hojas), aristas, hojas

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
        subtitulo = self._texto(
            "Inteligencia predictiva para bancos de sangre", 21, color=GRIS,
        ).next_to(logo, DOWN, buff=0.12)
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
        umbral_lbl = self._texto("Umbral de escasez", 15, color=ROJO)
        umbral_lbl.move_to(axes.c2p(2.4, UMBRAL) + UP * 0.24)

        # Zonas como en el dashboard real (a la izquierda de la gráfica)
        zona_crit = self._texto("ZONA CRÍTICA", 14, color=ROJO, weight=BOLD)
        zona_crit.move_to(axes.c2p(1.15, UMBRAL + 34))
        zona_est = self._texto("ZONA ESTABLE", 14, color=GRIS, weight=BOLD)
        zona_est.move_to(axes.c2p(1.15, UMBRAL - 34))
        presion_lbl = self._texto("Presión (demanda − oferta)", 15, color=ROJO, weight=BOLD)

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
            FadeIn(subtitulo, shift=DOWN * 0.1),
            FadeIn(hearthand, shift=RIGHT * 0.2),
            FadeIn(blood, shift=LEFT * 0.2),
            Create(eje_x),
            Create(eje_y),
            Create(umbral_line),
            FadeIn(umbral_lbl),
            FadeIn(zona_crit),
            FadeIn(zona_est),
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
        presion_lbl.move_to(axes.c2p(8.6, presion(11.4) + 14))
        self.play(FadeIn(presion_lbl, shift=UP * 0.1), run_time=0.5)
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

        vidas = self._tarjeta(
            [("1 donación puede salvar hasta 3 vidas", 22, BOLD)], escala=0.9,
        ).to_edge(DOWN, buff=0.55).match_x(patient)

        self.play(
            FadeIn(titulo, shift=DOWN * 0.2),
            FadeIn(patient, shift=LEFT * 0.2),
            run_time=1.0,
        )
        self._aparecer_uno_a_uno(items)
        self.play(FadeIn(mensaje, shift=UP * 0.2), run_time=0.8)
        self.play(GrowFromCenter(vidas), run_time=0.5)
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
            "Banco de sangre · 35.840 registros",
            "Población atendida · 221.203 registros",
            "Defunciones · 5.094 registros",
        ], tam=24, buff=0.35)
        depurado = self._texto(
            "26.107 donaciones válidas tras la limpieza", 22, color=ROJO, weight=BOLD,
        )
        bloque = VGroup(encabezado, registros, depurado).arrange(DOWN, buff=0.4, aligned_edge=LEFT)
        bloque.next_to(hospital, RIGHT, buff=1.0).align_to(hospital, UP)

        linea_tiempo, linea, puntos, etiquetas = self._linea_tiempo([2020, 2021, 2022, 2023, 2024, 2025])
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
        self.play(FadeIn(depurado, shift=RIGHT * 0.2), run_time=0.5)
        self._animar_linea_tiempo(linea, puntos, etiquetas)
        self.play(FadeIn(fuente), run_time=0.4)
        self.wait(0.5)
        self.next_slide()

    def slide_grupo_o(self):
        titulo = self._titulo("Casi el 60% solo puede recibir 2 de los 8 tipos")

        # Distribución ABO/Rh en 87.481 donantes (Hospital Pablo Tobón Uribe)
        datos = [
            ("O+", 52.1, True), ("A+", 28.0, False), ("O−", 7.0, True),
            ("B+", 6.7, False), ("A−", 3.5, False), ("AB+", 1.7, False),
            ("B−", 0.8, False), ("AB−", 0.3, False),
        ]
        base_y = -1.75
        escala_h = 3.1 / 52.1
        ancho_b, paso, x0 = 0.62, 0.985, -6.1

        barras, etiquetas, pcts = VGroup(), VGroup(), VGroup()
        barras_gris, pcts_gris = [], []
        for i, (nombre, pct, es_o) in enumerate(datos):
            alto = max(pct * escala_h, 0.07)
            x = x0 + i * paso
            barra = Rectangle(
                width=ancho_b, height=alto,
                fill_color=ROJO if es_o else GRIS,
                fill_opacity=0.95 if es_o else 0.55,
                stroke_width=0,
            ).move_to(np.array([x, base_y + alto / 2, 0]))
            lbl = self._texto(nombre, 15, color=ROJO if es_o else BLACK, weight=BOLD)
            lbl.move_to(np.array([x, base_y - 0.3, 0]))
            pt = self._texto(f"{pct:.1f}".replace(".", ",") + " %", 13,
                             color=ROJO if es_o else GRIS)
            pt.move_to(np.array([x, base_y + alto + 0.22, 0]))
            barras.add(barra)
            etiquetas.add(lbl)
            pcts.add(pt)
            if not es_o:
                barras_gris.append(barra)
                pcts_gris.append(pt)
        eje = Line(
            np.array([x0 - 0.55, base_y, 0]),
            np.array([x0 + 7 * paso + 0.55, base_y, 0]),
            color=GRIS, stroke_width=2.5,
        )

        tarjeta_o = self._parrafo([
            ("≈ 60 %", 58, ROJO, BOLD),
            ("de la población es grupo O:", 21, BLACK, NORMAL),
            ("solo puede recibir O− u O+", 24, ROJO, BOLD),
        ], buff=0.18).move_to(np.array([4.35, 0.75, 0]))
        nota_o = self._texto("52,1 % (O+)  +  7,0 % (O−)  =  59,1 %", 17, color=GRIS)
        nota_o.next_to(tarjeta_o, DOWN, buff=0.3)

        fuente = self._texto(
            "Fuente: Banco de sangre · Hospital Pablo Tobón Uribe · 87.481 donantes",
            16, color=GRIS,
        ).to_edge(DOWN, buff=0.35)

        self.play(FadeIn(titulo, shift=DOWN * 0.2), run_time=0.8)
        self.play(Create(eje), run_time=0.5)
        self.play(
            LaggedStart(*[GrowFromEdge(b, DOWN) for b in barras], lag_ratio=0.12),
            LaggedStart(*[FadeIn(e) for e in etiquetas], lag_ratio=0.12),
            run_time=1.8,
        )
        self.play(
            LaggedStart(*[FadeIn(p, shift=UP * 0.1) for p in pcts], lag_ratio=0.1),
            run_time=1.0,
        )
        self.wait(0.3)
        self.play(
            *[b.animate.set_opacity(0.22) for b in barras_gris],
            *[p.animate.set_opacity(0.35) for p in pcts_gris],
            run_time=0.7,
        )
        self.play(
            Indicate(barras[0], scale_factor=1.05, color=ROJO),
            Indicate(barras[2], scale_factor=1.15, color=ROJO),
            run_time=0.8,
        )
        self.play(FadeIn(tarjeta_o, shift=UP * 0.2), run_time=0.7)
        self.play(
            FadeIn(nota_o),
            Flash(tarjeta_o[0], color=ROJO, line_length=0.3),
            run_time=0.6,
        )
        self.play(FadeIn(fuente), run_time=0.4)
        self.wait(0.5)
        self.next_slide()

    def slide_modelo(self):
        titulo = self._titulo("¿Cómo pronostica el modelo? · XGBoost")

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
        ventana_lbl = self._texto("últimos 14 días", 14, color=ROJO, weight=BOLD)
        ventana_lbl.next_to(ventana, UP, buff=0.08)

        chips = self._vinetas(["lags 1–14", "media móvil 7 días", "mes del año"], tam=15, buff=0.14)
        ficha_titulo = self._texto("features de hoy", 16, color=ROJO, weight=BOLD)
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
            self._texto("ŷ", 30, color=ROJO, weight=BOLD),
            self._texto("=  f1(x) + f2(x) + f3(x) + …", 24, color=BLACK),
        ).arrange(RIGHT, buff=0.18)
        formula.next_to(ficha, RIGHT, buff=0.75).match_y(ficha)
        formula_nota = self._texto("una suma de árboles pequeños", 15, color=GRIS)
        formula_nota.next_to(formula, DOWN, buff=0.12).align_to(formula, LEFT)

        # ── Fila B: árboles en cadena, cada uno corrige el error del anterior ──
        centros = [LEFT * 3.6, ORIGIN, RIGHT * 3.6]
        aportes = ["+0.28", "+0.21", "+0.19"]
        arboles, titulos_arb, chips_aporte = [], [], []
        for i, c in enumerate(centros):
            arbol, aristas, hojas = self._arbolito()
            arbol.move_to(c + DOWN * 0.62)
            arboles.append((arbol, aristas, hojas))
            titulos_arb.append(
                self._texto(f"árbol {i + 1}", 15, color=GRIS, weight=BOLD)
                .next_to(arbol, UP, buff=0.12)
            )
            chips_aporte.append(
                self._tarjeta([(aportes[i], 20, BOLD)], escala=0.72)
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
                self._texto("corrige el error", 13, color=GRIS).next_to(flecha, UP, buff=0.06)
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
        corte_lbl = self._texto("corte de alerta", 14, color=GRIS)
        corte_lbl.next_to(corte_line, UP, buff=0.06)
        corte_lbl.shift(RIGHT * (corte_lbl.width / 2 + 0.1))
        nota_prod = self._texto("En producción son cientos de árboles en cadena", 14, color=GRIS)
        nota_prod.next_to(track, DOWN, buff=0.14).align_to(track, LEFT)
        prob_lbl = always_redraw(lambda: self._texto(
            f"P(escasez en 14 días) = {int(round(prob.get_value() * 100))} %",
            18, color=BLACK, weight=BOLD,
        ).next_to(track, UP, buff=0.16).align_to(track, LEFT))

        alerta = self._tarjeta([
            ("¡Escasez en 14 días!", 22, BOLD),
            ("se activa la campaña de donación", 15, NORMAL),
        ], escala=0.88).next_to(track, RIGHT, buff=0.55)

        # ── Animación ──
        self.play(FadeIn(titulo, shift=DOWN * 0.2), run_time=0.7)
        self.play(Create(base), Create(curva), run_time=1.1)
        self.play(Create(ventana), FadeIn(ventana_lbl, shift=UP * 0.1), run_time=0.7)
        self.play(GrowArrow(flecha_ficha), FadeIn(ficha, shift=RIGHT * 0.15), run_time=0.7)
        self.play(FadeIn(formula, shift=UP * 0.1), FadeIn(formula_nota), run_time=0.6)

        self.play(
            FadeIn(track), Create(corte_line),
            FadeIn(corte_lbl), FadeIn(nota_prod),
            run_time=0.7,
        )
        self.add(fill, prob_lbl)

        acumulado = [0.28, 0.49, 0.68]
        rutas = [(0, 3, 1), (1, 4, 2), (1, 5, 3)]  # (arista raíz, arista hoja, hoja)
        for i in range(3):
            arbol, aristas, hojas = arboles[i]
            intro = [FadeIn(arbol, shift=UP * 0.15), FadeIn(titulos_arb[i])]
            if i > 0:
                intro += [GrowArrow(flechas_res[i - 1]), FadeIn(notas_res[i - 1])]
            self.play(*intro, run_time=0.55)
            arista_a, arista_b, hoja = rutas[i]
            self.play(aristas[arista_a].animate.set_stroke(ROJO, 6), run_time=0.3)
            self.play(aristas[arista_b].animate.set_stroke(ROJO, 6), run_time=0.3)
            self.play(
                hojas[hoja].animate.set_fill(ROJO, opacity=0.92).set_stroke(ROJO, 2.5),
                GrowFromCenter(chips_aporte[i]),
                run_time=0.45,
            )
            self.play(prob.animate.set_value(acumulado[i]), run_time=0.8)

        self.play(
            GrowFromCenter(alerta),
            Flash(corte_line, color=ROJO, line_length=0.25),
            run_time=0.7,
        )
        self.wait(0.6)
        self.next_slide()
