"""
core/keys.py — Resolución de API keys para promptmodels 3.x.

Prioridad por proveedor:
  1) input api_key del nodo si no está vacío
  2) variable de entorno del proveedor
  3) archivo .env en la raíz del paquete (parser propio, sin python-dotenv)

Nunca se imprime ni loguea el valor de una key.
"""
import os
import pathlib
import logging

log = logging.getLogger("promptmodels.keys")

_PKG_ROOT = pathlib.Path(__file__).parent.parent


def _load_dotenv() -> dict:
    env_file = _PKG_ROOT / ".env"
    result: dict = {}
    if not env_file.exists():
        return result
    for line in env_file.read_text(encoding="utf-8-sig").splitlines():
        line = line.strip()
        if not line or line.startswith("#") or "=" not in line:
            continue
        key, _, value = line.partition("=")
        key = key.strip()
        value = value.strip()
        if key:
            result[key] = value
    return result


_dotenv_cache: dict | None = None


def _dotenv() -> dict:
    global _dotenv_cache
    if _dotenv_cache is None:
        _dotenv_cache = _load_dotenv()
    return _dotenv_cache


def resolve_key(node_input: str, env_var: str, provider: str) -> str:
    key = (node_input or "").strip()
    if key:
        return key

    key = os.getenv(env_var, "").strip()
    if key:
        return key

    key = _dotenv().get(env_var, "").strip()
    if key:
        return key

    raise ValueError(
        f"Falta la key de {provider}: pégala en el nodo o configúrala "
        f"en la variable de entorno {env_var} o en el archivo .env"
    )


def nvidia_key(node_input: str = "") -> str:
    return resolve_key(node_input, "NVIDIA_API_KEY", "NVIDIA")


def gemini_key(node_input: str = "") -> str:
    return resolve_key(node_input, "GEMINI_API_KEY", "Gemini")


def grok_key(node_input: str = "") -> str:
    return resolve_key(node_input, "XAI_API_KEY", "Grok/xAI")
