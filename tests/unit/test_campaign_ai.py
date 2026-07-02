"""Pruebas unitarias del asistente de campañas (generador por reglas)."""

import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parents[2]))

from src.campaign_ai import _fallback, plan_campaign  # noqa: E402

CAMPOS = {
    "titular", "mensaje", "publico_objetivo", "canal",
    "hashtags", "poster_lugar", "poster_fecha", "poster_mensaje",
}


def test_fallback_devuelve_todos_los_campos():
    out = _fallback({"comuna": "Robledo", "tipo": "O-", "fecha": "Sáb 12 jul"})
    assert CAMPOS.issubset(out.keys())
    assert "O-" in out["titular"]
    assert len(out["hashtags"]) == 3


def test_plan_campaign_sin_api_key_usa_reglas(monkeypatch):
    monkeypatch.delenv("GEMINI_API_KEY", raising=False)
    out = plan_campaign({"comuna": "Bello", "tipo": "AB+"})
    assert out["fuente"] == "reglas"
    assert out["mensaje"]


def test_fallback_tipo_negativo_marca_urgencia():
    out = _fallback({"comuna": "Belén", "tipo": "AB-"})
    assert "necesita" in out["titular"]
