# Presentación Sanghelios

Presentación animada sobre donación de sangre construida con
[Manim](https://www.manim.community/) y
[Manim Slides](https://manim-slides.eertmans.be/).

## Requisitos

- Python 3.13
- [uv](https://docs.astral.sh/uv/) (gestor de dependencias del proyecto)
- Dependencias del sistema de Manim (LaTeX, FFmpeg). Ver la
  [guía de instalación de Manim](https://docs.manim.community/en/stable/installation.html).

Las dependencias de Python (`manim`, `manim-slides`, `numpy`, ...) están
declaradas en el `pyproject.toml` de la raíz del repositorio.

## Instalación

Desde la raíz del repositorio:

```bash
uv sync
```

## Compilar la presentación

Todos los comandos se ejecutan dentro de la carpeta `presentation/`
(la ruta `assets/` se resuelve de forma relativa).

```bash
cd presentation
```

### 1. Renderizar las diapositivas

```bash
uv run manim-slides render main.py presentation
```

- `main.py` → archivo fuente.
- `presentation` → nombre de la clase `Slide` dentro de `main.py`.

Para previsualizar mientras editas, usa baja calidad (`-ql`):

```bash
uv run manim-slides render -ql main.py presentation
```

### 2. Reproducir la presentación

```bash
uv run manim-slides present presentation
```

Controles: `→` / barra espaciadora para avanzar, `←` para retroceder,
`q` para salir.

### 3. Exportar a HTML (opcional)

```bash
uv run manim-slides convert presentation presentation.html
```

Genera un `presentation.html` autónomo que se abre en cualquier navegador.

### 4. Exportar a vídeo / PDF (opcional)

```bash
uv run manim-slides convert --to=pptx presentation presentation.pptx
```

## Estructura

```
presentation/
├── main.py            # Orquestador: clase `presentation` que recorre SLIDES
├── estilo.py          # Paleta, tipografía y constantes compartidas
├── componentes.py     # Fábricas de mobjects (tarjetas, reloj, árboles…)
├── animaciones.py     # Helpers de animación que reciben la escena
├── diapositivas/      # Una diapositiva por archivo, registradas en __init__.py
│   ├── portada.py
│   ├── donaciones.py
│   ├── noticias.py
│   ├── cifras.py
│   ├── datos.py
│   ├── grupo_o.py
│   ├── modelo.py
│   └── demo.py
├── assets/            # Imágenes usadas en las diapositivas
│   ├── logo.png
│   ├── hearthand.png
│   ├── blood.png
│   ├── patient.png
│   └── news/          # Capturas de noticias
├── slides/            # Salida de manim-slides (generada)
└── media/             # Salida de manim (generada)
```

Para agregar una diapositiva: crea `diapositivas/nueva.py` con una función
`construir(scene)` y regístrala en la lista `SLIDES` de
`diapositivas/__init__.py` en la posición deseada.

## Diapositivas

1. **Portada** — logo y curva animada de presión que cruza el umbral de escasez.
2. **Donaciones** — usos de la sangre donada; 1 donación salva hasta 3 vidas.
3. **Noticias** — titulares sobre la escasez de sangre en el país.
4. **Cifras** — 42 pacientes/hora y 100 donantes diarios necesarios.
5. **Datos** — datasets del HGM con sus conteos y línea de tiempo 2020–2025.
6. **Grupo O** — distribución ABO/Rh (Pablo Tobón Uribe): ≈60% solo recibe O.
7. **Modelo** — animación de XGBoost: árboles que suman hasta la alerta.
8. **Demo** — navegador cargando `localhost:8000`, pie para pasar a la web.
