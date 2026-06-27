from PIL import Image, ImageDraw, ImageFont

EVENT_TEMPLATE = "event.png"
PERSONAL_TEMPLATE = "personal.png"

DARK_NAVY = (15, 23, 58)

_FONT_BOLD = "/usr/share/fonts/truetype/dejavu/DejaVuSans-Bold.ttf"
_FONT_REGULAR = "/usr/share/fonts/truetype/dejavu/DejaVuSans.ttf"


def _font(size: int, bold: bool = True) -> ImageFont.FreeTypeFont:
    return ImageFont.truetype(_FONT_BOLD if bold else _FONT_REGULAR, size)


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
        # Column: x=52–368, center_x=210, usable_w=280px
        # Value row: y=1250 (below FECHA label at ~y=1215)
        fecha_font = _auto_font(draw, time, max_w=280, start=28)
        _draw_centered(draw, time, cx=210, y=1250, font=fecha_font, color=DARK_NAVY)

        # ── LUGAR column ──────────────────────────────────────────────────────
        # Column: x=368–685, center_x=527, usable_w=280px
        # Same value row y=1250
        lugar_font = _auto_font(draw, place, max_w=280, start=28)
        _draw_centered(draw, place, cx=527, y=1250, font=lugar_font, color=DARK_NAVY)

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
