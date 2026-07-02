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
