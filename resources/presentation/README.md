# Presentación Sanghelios

Presentación animada sobre donación de sangre construida con
[Manim](https://www.manim.community/) y
[Manim Slides](https://manim-slides.eertmans.be/).

## Requisitos

- Python
- [uv](https://docs.astral.sh/uv/) 

## Ejecución


```bash
uv sync

uv run manim-slides render -ql main.py presentation

uv run manim-slides present presentation
```

