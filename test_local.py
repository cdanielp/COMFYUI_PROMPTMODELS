"""
test_local.py — Bloque 2: prueba real de cliente REST contra NVIDIA NIM.
Lee la key de .env o variable de entorno. NUNCA imprime la key.

Uso:
    python test_local.py
"""
import sys
import pathlib

# Permite importar core/ sin instalar el paquete
sys.path.insert(0, str(pathlib.Path(__file__).parent))

from core.keys import nvidia_key
from core.client_rest import post_openai


def main() -> None:
    key = nvidia_key()
    print("[test_local] NVIDIA_API_KEY: PRESENTE (valor omitido)")

    payload = {
        "model": "nvidia/nemotron-3-nano-omni-30b-a3b-reasoning",
        "messages": [
            {
                "role": "user",
                "content": "In one sentence, what is a ComfyUI custom node?",
            }
        ],
        "max_tokens": 120,
        "temperature": 0.4,
    }

    print("[test_local] Enviando request a NVIDIA NIM …")
    resp = post_openai(
        base_url="https://integrate.api.nvidia.com/v1",
        endpoint="/chat/completions",
        api_key=key,
        payload=payload,
        provider="NVIDIA",
    )

    text: str = resp["choices"][0]["message"]["content"]
    safe = text[:80].encode("ascii", errors="replace").decode("ascii")
    print("[test_local] HTTP 200 OK")
    print(f"[test_local] Respuesta (primeros 80 chars): {safe!r}")


if __name__ == "__main__":
    main()
