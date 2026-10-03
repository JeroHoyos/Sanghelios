# resources — material visual

| Recurso | Qué es |
|---|---|
| [Video de presentación](https://www.youtube.com/watch?v=7mOG2cgMJ0c) | Presentación del proyecto en YouTube |
| `presentation/` | Fuente de la presentación: diapositivas animadas con **Manim** |
| `portada.png` | Imagen principal del proyecto (logo Sanghelios) |
| `screenshots/` | Capturas de los módulos de la aplicación, usadas en el [README](../README.md) |
| `Presentacion.pptx` · `presentacion.pdf` | Exportes estáticos de la presentación — ver abajo |

## Exportar la presentación

Desde la raíz del repositorio:

```bash
uv run manim-slides render resources/presentation/main.py   # renderiza las escenas
uv run manim-slides convert --to pptx Presentacion resources/Presentacion.pptx
```

El PDF (`presentacion.pdf`) se exporta desde PowerPoint o con
`manim-slides convert --to pdf`.
