# ComfyUI_GoogleAI V2.5.1 — Seed Fix

## Qué se arregló

Los seeds no se reproducían correctamente por 3 problemas:

1. **Overflow de 64-bit**: El widget de seed aceptaba valores hasta 2^64 pero JavaScript y la API de Google solo manejan 32-bit con precisión. Los seeds grandes se corrompían silenciosamente.

2. **seed=0 ignorado**: Poner seed=0 con randomize desactivado no fijaba la semilla porque el código lo trataba como "sin seed". Ahora seed=0 sí se envía.

3. **Random fuera de rango**: El randomize generaba seeds de 64-bit que la API truncaba o rechazaba.

## Acción requerida

Actualizar el nodo. No hay cambios en workflows existentes — los inputs son los mismos, solo se corrigió el rango interno.

## Instalación

ComfyUI Manager: Update all → reiniciar ComfyUI
Manual: `cd custom_nodes/COMFYUI_PROMPTMODELS && git pull`
