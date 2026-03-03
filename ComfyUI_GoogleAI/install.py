"""
install.py - Dependencias del sistema para ComfyUI_GoogleAI V2.4.3
===================================================================
Ejecutado automáticamente por ComfyUI-Manager y ComfyDeploy durante
la instalación del nodo. Idempotente: si ya está instalado, no hace nada.

Autor: Prompt Models Studio | cdanielp
"""

import subprocess
import shutil
import sys

# ============================================================================
# 1. ffmpeg (sistema) — necesario para video Veo 3.1 y extracción de audio
# ============================================================================
if not shutil.which("ffmpeg"):
    print("[PromptModels] 📦 Instalando ffmpeg (necesario para Veo 3.1)...")
    try:
        subprocess.run(["apt-get", "update", "-qq"], capture_output=True, timeout=60)
        subprocess.run(
            ["apt-get", "install", "-y", "-qq", "--no-install-recommends", "ffmpeg"],
            capture_output=True, timeout=120,
        )
        if shutil.which("ffmpeg"):
            print("[PromptModels] ✅ ffmpeg instalado correctamente")
        else:
            print(
                "[PromptModels] ⚠️ No se pudo instalar ffmpeg automáticamente.\n"
                "  Instálalo manualmente:\n"
                "    Linux/Docker: apt install ffmpeg\n"
                "    macOS:        brew install ffmpeg\n"
                "    Windows:      choco install ffmpeg"
            )
    except Exception as e:
        print(f"[PromptModels] ⚠️ Error instalando ffmpeg: {e}")
else:
    print("[PromptModels] ✅ ffmpeg ya disponible")

# ============================================================================
# 2. scipy (opcional) — lectura WAV optimizada para audio
# ============================================================================
try:
    import scipy
    print(f"[PromptModels] ✅ scipy {scipy.__version__} disponible")
except ImportError:
    print("[PromptModels] 📦 Instalando scipy (lectura WAV optimizada)...")
    try:
        subprocess.run(
            [sys.executable, "-m", "pip", "install", "scipy", "--break-system-packages", "-q"],
            capture_output=True, timeout=120,
        )
        print("[PromptModels] ✅ scipy instalado")
    except Exception as e:
        print(f"[PromptModels] ⚠️ scipy no instalado ({e}) — se usará fallback manual")
