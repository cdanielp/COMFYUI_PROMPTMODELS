/**
 * Titan Suite - Script de Interfaz
 * Mejora la experiencia de usuario con auto-refresh de widgets
 */

import { app } from "../../scripts/app.js";

// Registrar extensión
app.registerExtension({
    name: "Titan.Suite.Refresh",
    
    async beforeRegisterNodeDef(nodeType, nodeData, app) {
        // Solo aplicar a nodos Titan_Maestro
        if (nodeData.name !== "Titan_Maestro") {
            return;
        }
        
        // Guardar referencia al método original
        const onExecuted = nodeType.prototype.onExecuted;
        
        // Override del método onExecuted
        nodeType.prototype.onExecuted = function(message) {
            // Llamar método original si existe
            if (onExecuted) {
                onExecuted.apply(this, arguments);
            }
            
            // Buscar si el mensaje indica que se guardó algo
            // Esto requiere que el nodo envíe un mensaje específico
            if (message && message.saved) {
                console.log("[Titan Suite] Prompt guardado, refrescando widgets...");
                refreshFavoritosWidget(this);
            }
        };
    },
    
    async nodeCreated(node) {
        // Añadir botón de refresh manual si es Titan_Maestro
        if (node.comfyClass === "Titan_Maestro") {
            // Buscar el widget de accion_bunker
            const accionWidget = node.widgets?.find(w => w.name === "accion_bunker");
            
            if (accionWidget) {
                // Guardar callback original
                const originalCallback = accionWidget.callback;
                
                // Override del callback
                accionWidget.callback = function(value) {
                    if (originalCallback) {
                        originalCallback.apply(this, arguments);
                    }
                    
                    // Si se seleccionó guardar, programar refresh
                    if (value === "💾 GUARDAR este Prompt") {
                        setTimeout(() => {
                            console.log("[Titan Suite] Acción de guardado detectada");
                            // Notificar al usuario
                            showNotification("Prompt guardado. Presiona F5 para ver en el menú.");
                        }, 500);
                    }
                };
            }
        }
    }
});

/**
 * Intenta refrescar el widget de favoritos
 * Nota: Esto es experimental y puede no funcionar en todas las versiones
 */
function refreshFavoritosWidget(node) {
    try {
        const favWidget = node.widgets?.find(w => w.name === "favoritos");
        if (favWidget && favWidget.options && favWidget.options.values) {
            // Forzar re-fetch de valores
            // Esto depende de la implementación interna de ComfyUI
            console.log("[Titan Suite] Widget encontrado, intentando refresh...");
            
            // Método 1: Invalidar caché de valores
            if (typeof app.graph?.setDirtyCanvas === 'function') {
                app.graph.setDirtyCanvas(true, true);
            }
            
            // Método 2: Recargar definición del nodo (más agresivo)
            // Deshabilitado por defecto para evitar problemas
            // app.refreshComboInNodes();
        }
    } catch (e) {
        console.warn("[Titan Suite] Error en refresh:", e);
    }
}

/**
 * Muestra una notificación temporal al usuario
 */
function showNotification(message, duration = 3000) {
    // Crear elemento de notificación
    const notification = document.createElement("div");
    notification.className = "titan-notification";
    notification.textContent = message;
    notification.style.cssText = `
        position: fixed;
        bottom: 20px;
        right: 20px;
        background: #2a2a2a;
        color: #fff;
        padding: 12px 20px;
        border-radius: 8px;
        border-left: 4px solid #4CAF50;
        box-shadow: 0 4px 12px rgba(0,0,0,0.3);
        z-index: 10000;
        font-family: sans-serif;
        font-size: 14px;
        animation: slideIn 0.3s ease;
    `;
    
    // Añadir estilos de animación si no existen
    if (!document.getElementById("titan-notification-styles")) {
        const style = document.createElement("style");
        style.id = "titan-notification-styles";
        style.textContent = `
            @keyframes slideIn {
                from { transform: translateX(100%); opacity: 0; }
                to { transform: translateX(0); opacity: 1; }
            }
            @keyframes slideOut {
                from { transform: translateX(0); opacity: 1; }
                to { transform: translateX(100%); opacity: 0; }
            }
        `;
        document.head.appendChild(style);
    }
    
    document.body.appendChild(notification);
    
    // Remover después de la duración
    setTimeout(() => {
        notification.style.animation = "slideOut 0.3s ease";
        setTimeout(() => notification.remove(), 300);
    }, duration);
}

console.log("✅ Titan Suite UI Extension cargada");
