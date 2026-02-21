/**
 * grok_ui.js — Extensiones de UI para ComfyUI_Grok
 * ==================================================
 * Funcionalidades:
 *   1. Estilo visual único: fondo negro mate + bordes púrpuras
 *   2. Badge de estado dinámico: Listo / Generando... / Analizando / Error
 *   3. Indicador de modo automático en Grok_Image_Master
 *   4. Contador de imágenes conectadas en Grok_Multimodal_Vision
 *   5. Barra de progreso estimada para Grok_Video_Forge
 *
 * Autor: Prompt Models Studio — xAI Integration Layer v2.0
 */

import { app } from "../../scripts/app.js";

// ──────────────────────────────────────────────
// PALETA DE COLORES GROK
// ──────────────────────────────────────────────
const GROK_COLORS = {
    bgDark:       "#0d0d0d",     // Fondo negro mate
    bgCard:       "#1a1a2e",     // Fondo interno de nodos
    borderPurple: "#7b2fbe",     // Borde púrpura principal
    borderGlow:   "#a855f7",     // Púrpura brillante para hover/activo
    textPrimary:  "#e2e8f0",     // Texto principal
    textMuted:    "#94a3b8",     // Texto secundario
    accentCyan:   "#06b6d4",     // Acento cian para badges de info
    accentGreen:  "#22c55e",     // Verde para estado OK
    accentYellow: "#eab308",     // Amarillo para procesando
    accentRed:    "#ef4444",     // Rojo para error
    accentOrange: "#f97316",     // Naranja para video
};

// IDs de nodos gestionados por esta extensión
const GROK_NODE_TYPES = [
    "GrokTextNode",
    "GrokImageNode",
    "Grok_Multimodal_Vision",
    "Grok_Image_Master",
    "Grok_Video_Forge",
    "Grok_Prompt_Architect",
];

// Estados del badge
const STATUS = {
    READY:      { label: "● Listo",          color: GROK_COLORS.accentGreen  },
    PROCESSING: { label: "⟳ Generando...",   color: GROK_COLORS.accentYellow },
    ANALYZING:  { label: "◎ Analizando...",  color: GROK_COLORS.accentCyan   },
    VIDEO:      { label: "▶ Forjando Video...", color: GROK_COLORS.accentOrange },
    ERROR:      { label: "✕ Error",          color: GROK_COLORS.accentRed    },
    LEGACY:     { label: "⚠ Legado v1",      color: GROK_COLORS.textMuted    },
};


// ──────────────────────────────────────────────
// UTILIDADES DE DIBUJO
// ──────────────────────────────────────────────

/**
 * Aplica el estilo visual de Grok al nodo en el canvas LiteGraph.
 * @param {LGraphNode} node 
 */
function applyGrokStyle(node) {
    node.color          = GROK_COLORS.bgCard;
    node.bgcolor        = GROK_COLORS.bgDark;
    node.shape          = LiteGraph.ROUND_SHAPE;

    // Guardar referencia al status actual
    if (!node._grokStatus) {
        node._grokStatus = isLegacyNode(node.type) ? STATUS.LEGACY : STATUS.READY;
    }
}

/**
 * Verifica si el nodo es de la versión 1 (legado).
 * @param {string} nodeType 
 * @returns {boolean}
 */
function isLegacyNode(nodeType) {
    return nodeType === "GrokTextNode" || nodeType === "GrokImageNode";
}

/**
 * Dibuja el badge de estado en la esquina superior derecha del nodo.
 * Se llama desde el hook onDrawForeground de LiteGraph.
 * @param {CanvasRenderingContext2D} ctx 
 * @param {LGraphNode} node 
 */
function drawStatusBadge(ctx, node) {
    const status = node._grokStatus || STATUS.READY;
    const padding = 6;
    const badgeH  = 18;
    const fontSize = 10;

    ctx.save();
    ctx.font = `bold ${fontSize}px 'Inter', 'Segoe UI', sans-serif`;

    const textW = ctx.measureText(status.label).width;
    const badgeW = textW + padding * 2;
    const x = node.size[0] - badgeW - 8;
    const y = -badgeH - 4;

    // Fondo del badge con borde redondeado
    ctx.beginPath();
    ctx.roundRect(x, y, badgeW, badgeH, 4);
    ctx.fillStyle = GROK_COLORS.bgDark + "cc";  // con transparencia
    ctx.fill();
    ctx.strokeStyle = status.color;
    ctx.lineWidth = 1;
    ctx.stroke();

    // Texto del badge
    ctx.fillStyle   = status.color;
    ctx.textBaseline = "middle";
    ctx.fillText(status.label, x + padding, y + badgeH / 2);

    ctx.restore();
}

/**
 * Dibuja el borde púrpura característico de los nodos Grok.
 * @param {CanvasRenderingContext2D} ctx 
 * @param {LGraphNode} node 
 */
function drawGrokBorder(ctx, node) {
    const isActive = node._grokStatus &&
                     node._grokStatus !== STATUS.READY &&
                     node._grokStatus !== STATUS.LEGACY;

    const borderColor = isActive ? GROK_COLORS.borderGlow : GROK_COLORS.borderPurple;
    const lineWidth   = isActive ? 2 : 1.5;

    ctx.save();
    ctx.beginPath();
    ctx.roundRect(0, -LiteGraph.NODE_TITLE_HEIGHT, node.size[0], node.size[1] + LiteGraph.NODE_TITLE_HEIGHT, 8);
    ctx.strokeStyle = borderColor;
    ctx.lineWidth   = lineWidth;

    // Efecto glow cuando está procesando
    if (isActive) {
        ctx.shadowColor = GROK_COLORS.borderGlow;
        ctx.shadowBlur  = 10;
    }

    ctx.stroke();
    ctx.restore();
}

/**
 * Dibuja información de modo en Grok_Image_Master según las conexiones.
 * @param {CanvasRenderingContext2D} ctx 
 * @param {LGraphNode} node 
 */
function drawImageMasterMode(ctx, node) {
    if (node.type !== "Grok_Image_Master") return;

    const hasRefImage = node.inputs?.find(i => i.name === "reference_image")?.link != null;
    const hasMask     = node.inputs?.find(i => i.name === "mask")?.link != null;

    let modeLabel, modeColor;
    if (hasMask && hasRefImage) {
        modeLabel = "🖌 INPAINTING";
        modeColor = GROK_COLORS.accentCyan;
    } else if (hasRefImage) {
        modeLabel = "🔄 IMAGE-TO-IMAGE";
        modeColor = GROK_COLORS.accentYellow;
    } else {
        modeLabel = "✨ GENERACIÓN PURA";
        modeColor = GROK_COLORS.accentGreen;
    }

    ctx.save();
    ctx.font      = "bold 9px 'Inter', monospace";
    ctx.fillStyle = modeColor;
    ctx.textAlign = "center";
    ctx.fillText(modeLabel, node.size[0] / 2, node.size[1] - 8);
    ctx.restore();
}

/**
 * Dibuja contador de imágenes conectadas en Grok_Multimodal_Vision.
 * @param {CanvasRenderingContext2D} ctx 
 * @param {LGraphNode} node 
 */
function drawImageCounter(ctx, node) {
    if (node.type !== "Grok_Multimodal_Vision") return;

    const imagePins = ["image_1", "image_2", "image_3", "image_4", "image_5", "video_frames"];
    let connectedCount = 0;
    let hasVideo = false;

    imagePins.forEach(pinName => {
        const input = node.inputs?.find(i => i.name === pinName);
        if (input?.link != null) {
            if (pinName === "video_frames") hasVideo = true;
            else connectedCount++;
        }
    });

    if (connectedCount === 0 && !hasVideo) return;

    let counterText = `📷 ${connectedCount}/5 imgs`;
    if (hasVideo) counterText += " + 🎬 video";

    ctx.save();
    ctx.font      = "bold 9px 'Inter', monospace";
    ctx.fillStyle = GROK_COLORS.accentCyan;
    ctx.textAlign = "center";
    ctx.fillText(counterText, node.size[0] / 2, node.size[1] - 8);
    ctx.restore();
}

/**
 * Dibuja barra de progreso estimada para Grok_Video_Forge.
 * La barra es puramente visual; se anima mientras el nodo está en estado VIDEO.
 * @param {CanvasRenderingContext2D} ctx 
 * @param {LGraphNode} node 
 */
function drawVideoProgress(ctx, node) {
    if (node.type !== "Grok_Video_Forge") return;
    if (node._grokStatus !== STATUS.VIDEO) return;

    const now      = Date.now();
    const elapsed  = (now - (node._videoStartTime || now)) / 1000;
    const estimated = 60; // segundos estimados de generación
    const progress  = Math.min(elapsed / estimated, 0.95); // max 95% hasta confirmar

    const barW = node.size[0] - 20;
    const barH = 6;
    const barX = 10;
    const barY = node.size[1] - 16;

    ctx.save();

    // Fondo de la barra
    ctx.beginPath();
    ctx.roundRect(barX, barY, barW, barH, 3);
    ctx.fillStyle = "#2d2d2d";
    ctx.fill();

    // Progreso
    const fillW = Math.max(barW * progress, 10);
    ctx.beginPath();
    ctx.roundRect(barX, barY, fillW, barH, 3);

    const gradient = ctx.createLinearGradient(barX, 0, barX + fillW, 0);
    gradient.addColorStop(0, GROK_COLORS.borderPurple);
    gradient.addColorStop(1, GROK_COLORS.accentOrange);
    ctx.fillStyle = gradient;
    ctx.fill();

    // Texto de progreso
    ctx.font      = "9px monospace";
    ctx.fillStyle = GROK_COLORS.textMuted;
    ctx.textAlign = "center";
    ctx.fillText(
        `${Math.round(progress * 100)}% — ${Math.round(elapsed)}s`,
        node.size[0] / 2,
        barY - 4
    );

    ctx.restore();
}


// ──────────────────────────────────────────────
// HOOKS DE LITEGRAPH
// ──────────────────────────────────────────────

/**
 * Engancha los métodos de dibujo personalizados a un nodo específico.
 * @param {LGraphNode} node 
 */
function hookGrokNode(node) {
    // Estilo base
    applyGrokStyle(node);

    // Guardar referencia al método original de dibujo (si existe)
    const originalOnDrawForeground = node.onDrawForeground?.bind(node);

    node.onDrawForeground = function(ctx) {
        // Llamar al dibujo original si existe
        if (originalOnDrawForeground) {
            originalOnDrawForeground(ctx);
        }

        // Aplicar extensiones visuales de Grok
        drawGrokBorder(ctx, this);
        drawStatusBadge(ctx, this);
        drawImageMasterMode(ctx, this);
        drawImageCounter(ctx, this);
        drawVideoProgress(ctx, this);
    };

    // Redimensionar nodo para acomodar elementos extra
    if (!isLegacyNode(node.type)) {
        const extraHeight = 24;
        if (node.size[1] < 200) {
            node.size[1] += extraHeight;
        }
    }
}


// ──────────────────────────────────────────────
// API PÚBLICA: CONTROL DE ESTADO
// ──────────────────────────────────────────────

/**
 * Cambia el estado visual de un nodo Grok.
 * @param {LGraphNode} node 
 * @param {"READY"|"PROCESSING"|"ANALYZING"|"VIDEO"|"ERROR"} statusKey 
 */
function setGrokStatus(node, statusKey) {
    if (!node) return;
    node._grokStatus = STATUS[statusKey] || STATUS.READY;

    if (statusKey === "VIDEO") {
        node._videoStartTime = Date.now();
    }

    // Forzar re-render del canvas
    app.graph?.setDirtyCanvas(true, true);
}


// ──────────────────────────────────────────────
// REGISTRO DE LA EXTENSIÓN EN COMFYUI
// ──────────────────────────────────────────────

app.registerExtension({
    name: "PromptModels.GrokUI",

    /**
     * Se ejecuta cuando ComfyUI carga todos los tipos de nodos.
     * Aquí modificamos el comportamiento de los nodos antes de que se instancien.
     */
    async beforeRegisterNodeDef(nodeType, nodeData, app) {
        if (!GROK_NODE_TYPES.includes(nodeData.name)) return;

        // ── Hook: onCreate ────────────────────────────────────────────
        // Se ejecuta cada vez que se crea una instancia del nodo en el canvas
        const originalOnNodeCreated = nodeType.prototype.onNodeCreated;
        nodeType.prototype.onNodeCreated = function() {
            if (originalOnNodeCreated) {
                originalOnNodeCreated.apply(this, arguments);
            }
            hookGrokNode(this);
        };

        // ── Hook: onExecutionStart ─────────────────────────────────────
        // Se ejecuta cuando ComfyUI comienza a procesar este nodo
        const originalOnExecutionStart = nodeType.prototype.onExecutionStart;
        nodeType.prototype.onExecutionStart = function() {
            if (originalOnExecutionStart) {
                originalOnExecutionStart.apply(this, arguments);
            }

            // Elegir estado según tipo de nodo
            if (this.type === "Grok_Video_Forge") {
                setGrokStatus(this, "VIDEO");
            } else if (this.type === "Grok_Multimodal_Vision") {
                setGrokStatus(this, "ANALYZING");
            } else {
                setGrokStatus(this, "PROCESSING");
            }
        };

        // ── Hook: onExecuted ──────────────────────────────────────────
        // Se ejecuta cuando el nodo termina de procesar
        const originalOnExecuted = nodeType.prototype.onExecuted;
        nodeType.prototype.onExecuted = function(output) {
            if (originalOnExecuted) {
                originalOnExecuted.apply(this, arguments);
            }
            setGrokStatus(this, "READY");
        };
    },

    /**
     * Se ejecuta cuando se carga un workflow completo desde JSON.
     * Aplica estilos a nodos Grok ya existentes en el grafo.
     */
    async loadedGraphNode(node, app) {
        if (GROK_NODE_TYPES.includes(node.type)) {
            hookGrokNode(node);
        }
    },
});


// ──────────────────────────────────────────────
// ANIMACIÓN DEL CANVAS (para barra de progreso de video)
// ──────────────────────────────────────────────
// Fuerza re-renders periódicos solo cuando hay nodos de video en proceso

let _animFrameId = null;

function _checkForActiveVideoNodes() {
    const hasActiveVideo = app.graph?.nodes?.some(
        n => n.type === "Grok_Video_Forge" && n._grokStatus === STATUS.VIDEO
    );

    if (hasActiveVideo) {
        app.graph?.setDirtyCanvas(true, false);
        _animFrameId = requestAnimationFrame(_checkForActiveVideoNodes);
    } else {
        _animFrameId = null;
    }
}

// Iniciar loop de animación cuando hay nodos de video procesando
const _originalSetDirtyCanvas = LGraphCanvas.prototype.setDirtyCanvas;
// (el loop se activa automáticamente al cambiar a estado VIDEO via setGrokStatus)

// Exportar para uso externo si otros módulos necesitan controlar el estado
export { setGrokStatus, STATUS, GROK_COLORS };
