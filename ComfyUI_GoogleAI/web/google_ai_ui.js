/**
 * google_ai_ui.js - Frontend para ComfyUI_GoogleAI (V2.0)
 * =========================================================
 * SOLO: Global API Key en Settings + inyección pre-queue.
 * El "Explicador de Errores" fue movido a ComfyUI_UniversalErrorExplainer.
 *
 * Autor: Prompt Models Studio | cdanielp
 */

import { app } from "../../scripts/app.js";

const SETTING_KEY = "GoogleAI.apiKey";
const NODE_FAMILY_PREFIX = "GoogleAI_";

app.registerExtension({
    name: "GoogleAI.Settings",

    /**
     * Registra el campo de API Key en los Settings de ComfyUI (⚙️).
     */
    async setup() {
        app.ui.settings.addSetting({
            id: SETTING_KEY,
            name: "Google AI API Key (Gemini)",
            type: "text",
            defaultValue: "",
            tooltip: "Tu API Key de Google AI Studio. Se guarda en localStorage.",
            attrs: {
                type: "password",
                placeholder: "Pega tu API Key aquí...",
                style: "width: 100%; max-width: 400px;",
            },
            onChange(value) {
                if (value && value.trim()) {
                    localStorage.setItem("googleai_api_key", value.trim());
                } else {
                    localStorage.removeItem("googleai_api_key");
                }
            },
        });

        // Sincronizar localStorage → Settings al iniciar
        const stored = localStorage.getItem("googleai_api_key");
        if (stored && !app.ui.settings.getSettingValue(SETTING_KEY)) {
            app.ui.settings.setSettingValue(SETTING_KEY, stored);
        }

        console.log("[GoogleAI] Settings extension loaded.");
    },

    /**
     * Inyecta la API Key global en nodos GoogleAI_ que tengan el campo vacío,
     * justo antes de que el payload se envíe al servidor Python.
     */
    async beforeQueuePrompt(graphData) {
        const globalKey = _getGlobalApiKey();
        if (!globalKey) return graphData;

        const prompt = graphData?.output;
        if (!prompt) return graphData;

        for (const nodeId in prompt) {
            const node = prompt[nodeId];
            if (!node?.class_type) continue;

            if (node.class_type.startsWith(NODE_FAMILY_PREFIX)) {
                const inputs = node.inputs || {};
                if (!inputs.api_key || inputs.api_key.trim() === "") {
                    inputs.api_key = globalKey;
                }
            }
        }

        return graphData;
    },
});

/**
 * Obtiene la API Key global desde Settings o localStorage.
 */
function _getGlobalApiKey() {
    try {
        const key = app.ui.settings.getSettingValue(SETTING_KEY);
        if (key && key.trim()) return key.trim();
    } catch (_) {}

    const ls = localStorage.getItem("googleai_api_key");
    return ls && ls.trim() ? ls.trim() : null;
}
