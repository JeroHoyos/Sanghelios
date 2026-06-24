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
├── main.py            # Definición de la presentación (clase `presentation`)
├── assets/            # Imágenes usadas en las diapositivas
│   ├── logo.png
│   ├── hearthand.png
│   ├── blood.png
│   ├── patient.png
│   └── news/          # Capturas de noticias
├── slides/            # Salida de manim-slides (generada)
└── media/             # Salida de manim (generada)
```

## Diapositivas

1. **Presentación** — logo y curva animada de "presión del sistema" que cruza
   el umbral de escasez.
2. **Donaciones** — usos de la sangre donada.
3. **Noticias** — titulares sobre la escasez de sangre en el país.
