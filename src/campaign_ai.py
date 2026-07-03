"""Asistente de IA para planear publicidad de campañas de donación de sangre.

Usa Google Gemini cuando hay ``GEMINI_API_KEY`` en el entorno; si la llamada
falla (sin clave, red, formato), cae a un generador basado en reglas para que
el asistente siempre devuelva una propuesta útil.
"""

from __future__ import annotations

import json
import os
import urllib.error
import urllib.request

_GEMINI_URL = (
    "https://generativelanguage.googleapis.com/v1beta/models/"
    "gemini-2.5-flash:generateContent"
)

_CAMPOS = (
    "titular", "mensaje", "publico_objetivo", "canal",
    "hashtags", "poster_lugar", "poster_fecha", "poster_mensaje",
)

# Contexto clínico por grupo para enriquecer las sugerencias.
_NOTA_TIPO = {
    "O-": "donante universal: su sangre sirve para urgencias de cualquier paciente; el más crítico.",
    "O+": "el grupo más frecuente y de mayor impacto en campañas masivas.",
    "A-": "grupo negativo escaso; alta responsabilidad de cobertura.",
    "A+": "grupo frecuente; buen objetivo para captación general.",
    "B-": "grupo negativo escaso; reservas bajas.",
    "B+": "grupo poco común; captación focalizada.",
    "AB-": "el más escaso; monitoreo permanente.",
    "AB+": "receptor universal; su plasma es valioso.",
}


def _prompt(ctx: dict) -> str:
    tipo = ctx.get("tipo", "O-")
    return (
        "Eres un estratega de marketing social para un banco de sangre en Medellín, "
        "Colombia. Diseña una pieza de publicidad para una campaña de donación.\n\n"
        f"Contexto:\n"
        f"- Comuna/zona: {ctx.get('comuna', 'Medellín')}\n"
        f"- Grupo sanguíneo prioritario: {tipo} ({_NOTA_TIPO.get(tipo, '')})\n"
        f"- Fecha/horario tentativo: {ctx.get('fecha') or 'por definir'}\n"
        f"- Objetivo: {ctx.get('objetivo') or 'aumentar donaciones y cubrir la escasez proyectada'}\n"
        f"- Tono deseado: {ctx.get('tono') or 'cercano y urgente'}\n\n"
        "Responde SOLO con un JSON válido (sin markdown) con estas claves exactas:\n"
        '{"titular": str (máx 8 palabras, potente), '
        '"mensaje": str (2-3 frases, motiva a donar), '
        '"publico_objetivo": str (a quién y por qué), '
        '"canal": str (dónde difundir: redes, universidades, empresas, radio…), '
        '"hashtags": [str, str, str], '
        '"poster_lugar": str (lugar concreto para el afiche), '
        '"poster_fecha": str (fecha y hora para el afiche), '
        '"poster_mensaje": str (1 frase breve para el afiche)}\n'
        "Todo en español de Colombia."
    )


def _call_gemini(prompt: str, key: str) -> dict:
    payload = json.dumps({
        "contents": [{"parts": [{"text": prompt}]}],
        "generationConfig": {"temperature": 0.9, "responseMimeType": "application/json"},
    }).encode("utf-8")
    req = urllib.request.Request(
        _GEMINI_URL, data=payload, method="POST",
        headers={"Content-Type": "application/json", "x-goog-api-key": key},
    )
    with urllib.request.urlopen(req, timeout=25) as resp:
        raw = json.loads(resp.read().decode("utf-8"))
    text = raw["candidates"][0]["content"]["parts"][0]["text"]
    data = json.loads(text)
    return {k: data.get(k, "") for k in _CAMPOS}


def _fallback(ctx: dict) -> dict:
    tipo = ctx.get("tipo", "O-")
    comuna = ctx.get("comuna", "Medellín")
    fecha = ctx.get("fecha") or "próximo sábado · 8am – 2pm"
    urgente = tipo.endswith("-")
    titular = (
        f"{comuna} necesita tu sangre {tipo}" if urgente
        else f"Dona sangre {tipo} en {comuna}"
    )
    mensaje = (
        f"Las reservas de {tipo} están bajo el nivel seguro. "
        f"Con una donación de 10 minutos puedes salvar hasta 3 vidas en {comuna}. "
        "Te esperamos."
    )
    return {
        "titular": titular,
        "mensaje": mensaje,
        "publico_objetivo": (
            f"Adultos 18–45 de {comuna} y alrededores; prioriza donantes {tipo} "
            "y campañas en universidades y empresas cercanas."
        ),
        "canal": "Instagram y WhatsApp locales, carteleras en universidades y empresas de la zona.",
        "hashtags": ["#DonaVidaMedellín", f"#Sangre{tipo.replace('-', 'Neg').replace('+', 'Pos')}", "#Sanghelios"],
        "poster_lugar": f"Punto de donación · {comuna}",
        "poster_fecha": fecha,
        "poster_mensaje": f"Tu sangre {tipo} salva vidas. Dona hoy.",
    }


def _gemini_json(prompt: str, key: str, temperature: float = 0.2) -> dict:
    """Llamada genérica a Gemini que devuelve el JSON parseado de la respuesta."""
    payload = json.dumps({
        "contents": [{"parts": [{"text": prompt}]}],
        "generationConfig": {"temperature": temperature, "responseMimeType": "application/json"},
    }).encode("utf-8")
    req = urllib.request.Request(
        _GEMINI_URL, data=payload, method="POST",
        headers={"Content-Type": "application/json", "x-goog-api-key": key},
    )
    with urllib.request.urlopen(req, timeout=25) as resp:
        raw = json.loads(resp.read().decode("utf-8"))
    return json.loads(raw["candidates"][0]["content"]["parts"][0]["text"])


def _prompt_lugar(texto: str, zona: str) -> str:
    return (
        "Eres un guía local experto de Medellín, Colombia. Un usuario describe de "
        f"forma informal o vaga un lugar: «{texto}»"
        + (f" (zona de referencia: {zona})" if zona else "")
        + ".\nIdentifica el lugar REAL más probable al que se refiere (clínica, "
        "hospital, universidad, parque, centro comercial, estación del metro, etc.).\n"
        "Responde SOLO con JSON válido: "
        '{"encontrado": true|false, "nombre": "nombre oficial del lugar", '
        '"direccion": "dirección real (calle/carrera) en Medellín", '
        '"nota": "1 frase corta explicando por qué crees que es ese"}. '
        "Si la descripción no alcanza para identificar un lugar concreto, usa "
        'encontrado=false y deja los demás campos vacíos.'
    )


def _buscar_nominatim(texto: str) -> dict | None:
    """Respaldo con OpenStreetMap cuando no hay clave de Gemini."""
    import urllib.parse

    q = urllib.parse.urlencode({
        "q": f"{texto}, Medellín, Colombia", "format": "json", "limit": 1,
    })
    req = urllib.request.Request(
        f"https://nominatim.openstreetmap.org/search?{q}",
        headers={"User-Agent": "Sanghelios/1.0 (banco de sangre HGM)"},
    )
    with urllib.request.urlopen(req, timeout=10) as resp:
        rows = json.loads(resp.read().decode("utf-8"))
    if not rows:
        return None
    partes = [p.strip() for p in rows[0].get("display_name", "").split(",")]
    return {
        "encontrado": True,
        "nombre": partes[0] if partes else texto,
        "direccion": ", ".join(partes[1:3]),
        "nota": "Encontrado en OpenStreetMap.",
    }


def buscar_lugar(texto: str, zona: str = "") -> dict:
    """Resuelve una descripción vaga («la clínica por Las Vegas») al lugar real.

    Gemini interpreta el lenguaje informal; si no hay clave o falla, se intenta
    con Nominatim. Si nada identifica el lugar, devuelve ``encontrado=False``.
    """
    key = os.environ.get("GEMINI_API_KEY", "").strip()
    if key:
        try:
            data = _gemini_json(_prompt_lugar(texto, zona), key)
            if data.get("encontrado") and data.get("nombre"):
                return {
                    "encontrado": True,
                    "nombre": str(data.get("nombre", "")).strip(),
                    "direccion": str(data.get("direccion", "")).strip(),
                    "nota": str(data.get("nota", "")).strip(),
                }
        except (urllib.error.URLError, KeyError, ValueError, TimeoutError):
            pass
    try:
        if (hit := _buscar_nominatim(texto)) is not None:
            return hit
    except (urllib.error.URLError, ValueError, TimeoutError):
        pass
    return {"encontrado": False, "nombre": "", "direccion": "", "nota": ""}


def plan_campaign(ctx: dict) -> dict:
    """Devuelve la propuesta de campaña. Añade ``fuente`` = 'gemini' | 'reglas'."""
    key = os.environ.get("GEMINI_API_KEY", "").strip()
    if key:
        try:
            data = _call_gemini(_prompt(ctx), key)
            if data.get("titular") and data.get("mensaje"):
                data["fuente"] = "gemini"
                return data
        except (urllib.error.URLError, KeyError, ValueError, TimeoutError):
            pass
    data = _fallback(ctx)
    data["fuente"] = "reglas"
    return data
