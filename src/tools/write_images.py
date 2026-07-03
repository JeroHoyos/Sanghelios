import os
from functools import lru_cache
from pathlib import Path

from PIL import Image, ImageDraw, ImageFont

EVENT_TEMPLATE = "event.png"
PERSONAL_TEMPLATE = "personal.png"

DARK_NAVY = (15, 23, 58)
RED = (191, 18, 18)
WHITE = (255, 255, 255)

# ── Plantillas de flyer (1414×2000) y sus zonas de texto ──────────────────────
# Cada campo define la caja donde se centra el texto: cx, y1..y2, ancho máximo,
# tamaño inicial de fuente, color y peso. Solo se rellenan las letras.
FLYERS_DIR = Path(__file__).resolve().parents[1] / "static" / "img" / "flyers"

# Beneficios (info de la plantilla clásica) que llenan el espacio vacío.
# Cada uno lleva su ícono ilustrado (assets del proyecto) como viñeta.
ICONS_DIR = Path(__file__).resolve().parents[1] / "static" / "img" / "flyers" / "icons"
BENEFICIOS = [
    ("blood.png", "Es seguro y solo toma 30 minutos"),
    ("hearthand.png", "Tu solidaridad es esperanza para otros"),
    ("patient.png", "Todos podemos ser el héroe de alguien"),
]

FLYER_TEMPLATES: dict[str, dict] = {
    "regala-vida": {
        "nombre": "Regala vida (clásica)",
        "campos": {
            "fecha": dict(cx=210, y1=1235, y2=1345, max_w=280, start=32, color=DARK_NAVY, bold=True),
            "lugar": dict(cx=527, y1=1235, y2=1345, max_w=280, start=32, color=DARK_NAVY, bold=True),
        },
        "foto": dict(cx=935, y1=150, d=170),
    },
    "gotita-feliz": {
        "nombre": "Gotita feliz",
        "campos": {
            "titular": dict(cx=707, y1=200, y2=460, max_w=1080, start=86, color=RED, bold=True),
            "mensaje": dict(cx=707, y1=500, y2=740, max_w=1050, start=58, color=DARK_NAVY, bold=False),
            "lugar":   dict(cx=660, y1=1650, y2=1790, max_w=330, start=38, color=DARK_NAVY, bold=True),
            "fecha":   dict(cx=1025, y1=1650, y2=1790, max_w=330, start=38, color=DARK_NAVY, bold=True),
            "nota":    dict(cx=760, y1=1800, y2=1890, max_w=940, start=34, color=RED, bold=False),
        },
        "beneficios": dict(cx=707, y1=820, y2=1400, max_w=1020, start=48, color=DARK_NAVY, bold=True),
        "foto": dict(cx=1190, y1=1080, d=250, ajusta={"beneficios": 720}),
    },
    "bolsa-corazon": {
        "nombre": "Bolsa corazón",
        "campos": {
            "titular": dict(cx=580, y1=170, y2=500, max_w=860, start=78, color=WHITE, bold=True),
            "mensaje": dict(cx=707, y1=720, y2=1000, max_w=1020, start=56, color=WHITE, bold=False),
            "fecha":   dict(cx=375, y1=1590, y2=1745, max_w=310, start=34, color=WHITE, bold=True),
            "lugar":   dict(cx=710, y1=1590, y2=1745, max_w=310, start=34, color=WHITE, bold=True),
            "publico": dict(cx=1010, y1=1590, y2=1745, max_w=310, start=34, color=WHITE, bold=True),
            "nota":    dict(cx=707, y1=1752, y2=1812, max_w=1060, start=30, color=WHITE, bold=False),
        },
        "beneficios": dict(cx=707, y1=1050, y2=1450, max_w=1020, start=46, color=WHITE, bold=True),
        "foto": dict(cx=1230, y1=690, d=210, ajusta={"mensaje": 790}),
    },
    "gota-en-mano": {
        "nombre": "Gota en mano",
        "campos": {
            "titular": dict(cx=707, y1=740, y2=970, max_w=720, start=64, color=WHITE, bold=True),
            "mensaje": dict(cx=707, y1=1000, y2=1190, max_w=800, start=46, color=WHITE, bold=False),
            "fecha":   dict(cx=467, y1=1320, y2=1450, max_w=280, start=32, color=WHITE, bold=True),
            "lugar":   dict(cx=713, y1=1320, y2=1450, max_w=280, start=32, color=WHITE, bold=True),
            "publico": dict(cx=960, y1=1320, y2=1450, max_w=280, start=32, color=WHITE, bold=True),
            "nota":    dict(cx=707, y1=1465, y2=1550, max_w=560, start=29, color=WHITE, bold=False),
        },
        "foto": dict(cx=235, y1=430, d=250),
    },
    "bolsa-doodle": {
        "nombre": "Bolsa doodle",
        "campos": {
            "titular": dict(cx=707, y1=240, y2=500, max_w=1060, start=86, color=RED, bold=True),
            "mensaje": dict(cx=707, y1=540, y2=780, max_w=1020, start=58, color=DARK_NAVY, bold=False),
            "lugar":   dict(cx=700, y1=1590, y2=1745, max_w=320, start=36, color=DARK_NAVY, bold=True),
            "fecha":   dict(cx=1048, y1=1590, y2=1745, max_w=320, start=36, color=DARK_NAVY, bold=True),
            "nota":    dict(cx=875, y1=1780, y2=1860, max_w=560, start=28, color=RED, bold=False),
        },
        "beneficios": dict(cx=707, y1=860, y2=1380, max_w=1000, start=48, color=DARK_NAVY, bold=True),
        "foto": dict(cx=210, y1=215, d=230, ajusta={"titular": 700}),
    },
    "brazo-donante": {
        "nombre": "Brazo donante",
        "campos": {
            "titular": dict(cx=707, y1=190, y2=440, max_w=1080, start=86, color=RED, bold=True),
            "mensaje": dict(cx=707, y1=480, y2=720, max_w=1040, start=58, color=DARK_NAVY, bold=False),
            "fecha":   dict(cx=590, y1=1345, y2=1455, max_w=520, start=36, color=DARK_NAVY, bold=True),
            "lugar":   dict(cx=590, y1=1505, y2=1615, max_w=520, start=36, color=DARK_NAVY, bold=True),
            "publico": dict(cx=500, y1=1655, y2=1765, max_w=340, start=34, color=DARK_NAVY, bold=True),
            "nota":    dict(cx=540, y1=1785, y2=1858, max_w=720, start=29, color=RED, bold=False),
        },
        "beneficios": dict(cx=640, y1=800, y2=1230, max_w=920, start=48, color=DARK_NAVY, bold=True),
        "foto": dict(cx=1215, y1=970, d=220, ajusta={"beneficios": 760}),
    },
}

# Fuentes candidatas por plataforma (la primera que exista se usa).
_FONT_CANDIDATES = {
    True: [  # negrita
        "/usr/share/fonts/truetype/dejavu/DejaVuSans-Bold.ttf",
        "C:/Windows/Fonts/arialbd.ttf",
        "C:/Windows/Fonts/segoeuib.ttf",
    ],
    False: [
        "/usr/share/fonts/truetype/dejavu/DejaVuSans.ttf",
        "C:/Windows/Fonts/arial.ttf",
        "C:/Windows/Fonts/segoeui.ttf",
    ],
}


def _mpl_dejavu(name: str) -> str | None:
    """DejaVu que trae matplotlib (dependencia del proyecto): siempre disponible."""
    try:
        import matplotlib

        path = Path(matplotlib.get_data_path()) / "fonts" / "ttf" / name
        return str(path) if path.exists() else None
    except Exception:
        return None


@lru_cache(maxsize=None)
def _font_path(bold: bool) -> str | None:
    for candidate in _FONT_CANDIDATES[bold]:
        if os.path.exists(candidate):
            return candidate
    return _mpl_dejavu("DejaVuSans-Bold.ttf" if bold else "DejaVuSans.ttf")


def _font(size: int, bold: bool = True) -> ImageFont.FreeTypeFont:
    path = _font_path(bold)
    if path:
        return ImageFont.truetype(path, size)
    return ImageFont.load_default(size)


def _text_w(draw: ImageDraw.ImageDraw, text: str, font: ImageFont.FreeTypeFont) -> int:
    bbox = draw.textbbox((0, 0), text, font=font)
    return bbox[2] - bbox[0]


def _auto_font(
    draw: ImageDraw.ImageDraw,
    text: str,
    max_w: int,
    start: int = 28,
    bold: bool = True,
) -> ImageFont.FreeTypeFont:
    size = start
    while size >= 12:
        f = _font(size, bold)
        if _text_w(draw, text, f) <= max_w:
            return f
        size -= 2
    return _font(12, bold)


def _draw_centered(
    draw: ImageDraw.ImageDraw,
    text: str,
    cx: int,
    y: int,
    font: ImageFont.FreeTypeFont,
    color: tuple,
) -> None:
    w = _text_w(draw, text, font)
    draw.text((cx - w // 2, y), text, font=font, fill=color)


def _wrap(draw: ImageDraw.ImageDraw, text: str, font, max_w: int) -> list[str]:
    lines, cur = [], ""
    for word in text.split():
        test = (cur + " " + word).strip()
        if _text_w(draw, test, font) <= max_w:
            cur = test
        else:
            if cur:
                lines.append(cur)
            cur = word
    if cur:
        lines.append(cur)
    return lines


def _wrap_balanced(draw: ImageDraw.ImageDraw, text: str, font, max_w: int) -> list[str]:
    """Como _wrap pero con líneas de largo parejo: busca el ancho mínimo que
    mantiene el mismo número de líneas, evitando líneas huérfanas ("...sangre / O-")."""
    lines = _wrap(draw, text, font, max_w)
    n = len(lines)
    if n <= 1:
        return lines
    lo = max(_text_w(draw, w, font) for w in text.split())
    hi = max_w
    best = lines
    while lo <= hi:
        mid = (lo + hi) // 2
        cand = _wrap(draw, text, font, mid)
        if len(cand) <= n:
            best = cand
            hi = mid - 1
        else:
            lo = mid + 1
    return best


def _draw_centered_wrapped(
    draw: ImageDraw.ImageDraw,
    text: str,
    cx: int,
    y1: int,
    y2: int,
    max_w: int,
    start: int = 32,
    color: tuple = (15, 23, 58),
    bold: bool = True,
    align: str = "center",
) -> None:
    """Texto multilínea centrado (o alineado a la izquierda con ``align='left'``,
    donde ``cx`` pasa a ser el borde izquierdo) y centrado verticalmente dentro
    de la caja (y1..y2): busca la fuente más grande cuyas líneas quepan en
    ancho y alto, así el texto nunca se sale de la tarjeta ni queda diminuto."""
    text = " ".join(str(text).split())
    if not text:
        return

    def _put(line: str, y: int, font) -> None:
        if align == "left":
            draw.text((cx, y), line, font=font, fill=color)
        else:
            _draw_centered(draw, line, cx, y, font, color)

    box_h = y2 - y1
    size = start
    while size >= 13:
        font = _font(size, bold)
        lines = _wrap_balanced(draw, text, font, max_w)
        lh = draw.textbbox((0, 0), "Ag", font=font)[3] + 6
        total_h = len(lines) * lh
        if total_h <= box_h and all(_text_w(draw, ln, font) <= max_w for ln in lines):
            y = y1 + (box_h - total_h) // 2
            for i, ln in enumerate(lines):
                _put(ln, y + i * lh, font)
            return
        size -= 2
    # Último recurso: fuente mínima, recortando a lo que quepa en la caja.
    font = _font(13, bold)
    lh = 22
    lines = _wrap(draw, text, font, max_w)[: max(1, box_h // lh)]
    y = y1 + (box_h - len(lines) * lh) // 2
    for i, ln in enumerate(lines):
        _put(ln, y + i * lh, font)


def _draw_in_box(
    draw: ImageDraw.ImageDraw,
    text: str,
    x1: int,
    y1: int,
    x2: int,
    y2: int,
    font: ImageFont.FreeTypeFont,
    color: tuple,
    pad: int = 6,
) -> None:
    max_w = x2 - x1 - pad * 2
    lh = draw.textbbox((0, 0), "Ag", font=font)[3] + 4
    words = text.split()
    lines, cur = [], ""
    for word in words:
        test = (cur + " " + word).strip()
        if _text_w(draw, test, font) <= max_w:
            cur = test
        else:
            if cur:
                lines.append(cur)
            cur = word
    if cur:
        lines.append(cur)
    total_h = len(lines) * lh
    sy = y1 + pad + max(0, ((y2 - y1) - total_h) // 2)
    for i, line in enumerate(lines):
        draw.text((x1 + pad, sy + i * lh), line, font=font, fill=color)


def _draw_benefits(img: Image.Image, draw: ImageDraw.ImageDraw, zona: dict) -> None:
    """Lista de beneficios con íconos ilustrados como viñetas, alineada a la
    izquierda del bloque y repartida uniformemente (llena el espacio vacío)."""
    cx, y1, y2 = zona["cx"], zona["y1"], zona["y2"]
    max_w, color, bold = zona["max_w"], zona["color"], zona["bold"]
    icon_gap = 26
    size = zona.get("start", 42)
    while size >= 20:
        font = _font(size, bold)
        icon_size = int(size * 3.2)
        if all(icon_size + icon_gap + _text_w(draw, t, font) <= max_w for _, t in BENEFICIOS):
            break
        size -= 2
    font = _font(size, bold)
    icon_size = int(size * 3.2)
    lh = max(icon_size, draw.textbbox((0, 0), "Ag", font=font)[3])
    block_w = max(icon_size + icon_gap + _text_w(draw, t, font) for _, t in BENEFICIOS)
    x = cx - block_w // 2
    gap = (y2 - y1 - len(BENEFICIOS) * lh) // max(1, len(BENEFICIOS) - 1)
    gap = min(gap, lh)  # aire agradable sin desparramarse
    total = len(BENEFICIOS) * lh + (len(BENEFICIOS) - 1) * gap
    y = y1 + max(0, (y2 - y1 - total) // 2)
    text_h = draw.textbbox((0, 0), "Ag", font=font)[3]
    for icon_name, texto in BENEFICIOS:
        icon_path = ICONS_DIR / icon_name
        if icon_path.exists():
            icon = Image.open(icon_path).convert("RGBA")
            icon.thumbnail((icon_size, icon_size), Image.LANCZOS)
            iy = y + (lh - icon.height) // 2
            img.paste(icon, (x + (icon_size - icon.width) // 2, iy), icon)
        ty = y + (lh - text_h) // 2
        draw.text((x + icon_size + icon_gap, ty), texto, font=font, fill=color)
        y += lh + gap


def _paste_avatar(img: Image.Image, draw: ImageDraw.ImageDraw,
                  foto_path: str, cx: int, cy: int, d: int) -> None:
    """Pega la foto recortada en círculo con anillo blanco + rojo (insignia)."""
    from PIL import ImageOps

    foto = ImageOps.fit(Image.open(foto_path).convert("RGBA"), (d, d), Image.LANCZOS)
    mask = Image.new("L", (d, d), 0)
    ImageDraw.Draw(mask).ellipse((0, 0, d, d), fill=255)
    img.paste(foto, (cx - d // 2, cy - d // 2), mask)
    draw.ellipse((cx - d // 2, cy - d // 2, cx + d // 2, cy + d // 2),
                 outline=WHITE, width=9)
    draw.ellipse((cx - d // 2 - 5, cy - d // 2 - 5, cx + d // 2 + 5, cy + d // 2 + 5),
                 outline=RED, width=5)


def compatibles_para(tipo: str) -> list[str]:
    """Grupos que pueden DONARLE a un receptor del tipo dado (ABO/Rh)."""
    tipos = ["O-", "O+", "A-", "A+", "B-", "B+", "AB-", "AB+"]
    abo_ok = {"O": ["O"], "A": ["O", "A"], "B": ["O", "B"], "AB": ["O", "A", "B", "AB"]}
    abo_r, rh_r = tipo[:-1], tipo[-1]
    return [d for d in tipos
            if d[:-1] in abo_ok.get(abo_r, []) and (d[-1] == "-" or rh_r == "+")]


def create_personal_flyer(nombre: str, tipo: str, lugar: str, mensaje: str,
                          foto_path: str | None, output_path: str) -> str:
    """Flyer personal ("TU DONACIÓN ES PARA:"): nombre, tipo de sangre, los
    grupos que pueden donarle y, si hay, la foto de la persona en un avatar
    circular sobre la tarjeta."""
    base = Path(__file__).resolve().parents[1] / "static" / "img" / "personal.png"
    img = Image.open(base).convert("RGBA")
    draw = ImageDraw.Draw(img)

    # Avatar circular bien grande sobre el corazón, sin tapar textos de la tarjeta
    if foto_path and Path(foto_path).exists():
        _paste_avatar(img, draw, foto_path, cx=922, cy=668, d=250)

    # Campos de la tarjeta (fuentes más generosas y centrado vertical fino)
    _draw_in_box(draw, nombre, x1=615, y1=818, x2=963, y2=858,
                 font=_auto_font(draw, nombre, max_w=335, start=30), color=DARK_NAVY)
    etiqueta_tipo = f"Sangre {tipo}"
    _draw_in_box(draw, etiqueta_tipo, x1=672, y1=873, x2=964, y2=913,
                 font=_auto_font(draw, etiqueta_tipo, max_w=280, start=30), color=RED)
    compat = compatibles_para(tipo)
    texto_msg = f"Pueden donarle: {', '.join(compat)}."
    if mensaje:
        texto_msg += " " + mensaje
    _draw_in_box(draw, texto_msg, x1=613, y1=928, x2=983, y2=1035,
                 font=_font(24, bold=False), color=DARK_NAVY, pad=12)
    # Lugar alineado con la etiqueta "LUGAR" (misma columna, pegado debajo)
    _draw_centered_wrapped(draw, lugar, cx=688, y1=1205, y2=1310,
                           max_w=312, start=30, color=DARK_NAVY, align="left")

    img.convert("RGB").save(output_path)
    return output_path


def create_flyer(template: str, textos: dict, output_path: str,
                 foto_path: str | None = None) -> str:
    """Rellena una plantilla de ``FLYER_TEMPLATES`` con los textos dados.

    ``textos`` admite las claves definidas en la plantilla (titular, mensaje,
    fecha, lugar, publico, nota); las vacías se omiten. Si llega ``foto_path``
    se pega como insignia circular en la zona ``foto`` de la plantilla y los
    bloques que la rozan se angostan según ``ajusta``.
    """
    spec = FLYER_TEMPLATES.get(template)
    if spec is None:
        raise ValueError(f"Plantilla desconocida: {template}")
    img = Image.open(FLYERS_DIR / f"{template}.png").convert("RGBA")
    draw = ImageDraw.Draw(img)

    con_foto = bool(foto_path and Path(foto_path).exists() and "foto" in spec)
    ajustes = spec["foto"].get("ajusta", {}) if con_foto else {}

    for campo, zona in spec["campos"].items():
        valor = str(textos.get(campo) or "").strip()
        if valor:
            if campo in ajustes:
                zona = {**zona, "max_w": ajustes[campo]}
            _draw_centered_wrapped(draw, valor, **zona)
    if "beneficios" in spec:
        zona_b = spec["beneficios"]
        if "beneficios" in ajustes:
            zona_b = {**zona_b, "max_w": ajustes["beneficios"]}
        _draw_benefits(img, draw, zona_b)
    if con_foto:
        f = spec["foto"]
        _paste_avatar(img, draw, foto_path, cx=f["cx"], cy=f["y1"], d=f["d"])
    img.convert("RGB").save(output_path)
    return output_path


class BloodDonationPoster:
    @staticmethod
    def create_event(
        place: str,
        time: str,
        output_path: str = "event_output.png",
        template_path: str = EVENT_TEMPLATE,
    ) -> str:
        img = Image.open(template_path).convert("RGB")
        draw = ImageDraw.Draw(img)

        # ── FECHA column ──────────────────────────────────────────────────────
        # Columna x=52–368 (centro 210). El valor vive bajo el rótulo FECHA,
        # dentro de la banda blanca de la tarjeta: y 1235–1345.
        _draw_centered_wrapped(draw, time, cx=210, y1=1235, y2=1345,
                               max_w=280, start=32, color=DARK_NAVY)

        # ── LUGAR column ──────────────────────────────────────────────────────
        # Columna x=368–685 (centro 527), misma banda vertical.
        _draw_centered_wrapped(draw, place, cx=527, y1=1235, y2=1345,
                               max_w=280, start=32, color=DARK_NAVY)

        img.save(output_path)
        return output_path

    @staticmethod
    def create_personal(
        name: str,
        id_number: str,
        place: str,
        message: str,
        output_path: str = "personal_output.png",
        template_path: str = PERSONAL_TEMPLATE,
    ) -> str:
        img = Image.open(template_path).convert("RGBA")
        draw = ImageDraw.Draw(img)

        # ── NOMBRE field ──────────────────────────────────────────────────────
        # Input box: x=612–963, y=820–855  (clear white area after "NOMBRE:" label)
        _draw_in_box(
            draw,
            name,
            x1=612,
            y1=820,
            x2=963,
            y2=855,
            font=_auto_font(draw, name, max_w=335, start=26),
            color=DARK_NAVY,
        )

        # ── IDENTIFICACIÓN field ──────────────────────────────────────────────
        # Input box: x=669–964, y=875–910  (clear white after "IDENTIFICACIÓN:" label)
        _draw_in_box(
            draw,
            id_number,
            x1=669,
            y1=875,
            x2=964,
            y2=910,
            font=_auto_font(draw, id_number, max_w=280, start=26),
            color=DARK_NAVY,
        )

        # ── MENSAJE field (multiline) ─────────────────────────────────────────
        # Input box: x=611–983, y=931–1032  (taller box, no label text inside)
        _draw_in_box(
            draw,
            message,
            x1=611,
            y1=931,
            x2=983,
            y2=1032,
            font=_font(22, bold=False),
            color=DARK_NAVY,
            pad=10,
        )

        # ── LUGAR (right panel below pin icon) ────────────────────────────────
        # Right white panel: x=670–985, center_x=827, usable_w=299px
        # Placed at y=1165, below the "LUGAR" label text at ~y=1118–1148
        lugar_font = _auto_font(draw, place, max_w=299, start=26)
        _draw_centered(draw, place, cx=827, y=1195, font=lugar_font, color=DARK_NAVY)

        img.save(output_path)
        return output_path


if __name__ == "__main__":
    BloodDonationPoster.create_event(
        place="Hospital San Vicente",
        time="Sábado 28 Jun · 8am–2pm",
        output_path="event_output.png",
    )
    print("event_output.png saved")

    BloodDonationPoster.create_personal(
        name="Carlos Gómez",
        id_number="1.234.567.890",
        place="Clínica Las Américas",
        message="Ayúdanos a salvar la vida de nuestra familia. Cualquier tipo de sangre es bienvenida.",
        output_path="personal_output.png",
    )
    print("personal_output.png saved")
