import { WebviewWindow } from '@tauri-apps/api/window';
import { listen, emit } from '@tauri-apps/api/event';

const OVERLAY_LABEL = 'supernova_control_border';
let borderWindow: WebviewWindow | null = null;

export async function initBorderOverlay() {
  // Crear ventana al inicio (oculta por defecto)
  borderWindow = new WebviewWindow(OVERLAY_LABEL, {
    url: './src/overlay/border.html',
    title: 'SuperNova Active',
    width: 1920,
    height: 1080,
    decorations: false,
    transparent: true,
    alwaysOnTop: true,
    skipTaskbar: true,
    focus: false,
    resizable: false,
    visible: false,
    acceptFirstMouse: true
  });

  // Escuchar eventos de control
  await listen<string>('control:started', async () => {
    await ensureBorderSize();
    await borderWindow?.show();
    await borderWindow?.eval('window.__borderAPI.show()');
  });

  await listen('control:finished', async () => {
    await borderWindow?.eval('window.__borderAPI.hide()');
    setTimeout(async () => await borderWindow?.hide(), 300);
  });

  // Ajustar a monitor activo al redimensionar
  window.addEventListener('resize', ensureBorderSize);
}

async function ensureBorderSize() {
  if (!borderWindow) return;
  // Tauri v2: obtener dimensiones del monitor primario o donde está el cursor
  // Simplificado: usar pantalla completa del OS
  const { width, height } = await import('@tauri-apps/api/window').then(m => m.availableMonitor());
  await borderWindow.setSize(m.PhysicalSize.new(width, height));
  await borderWindow.setPosition(m.PhysicalPosition.new(0, 0));
}

export async function triggerBorderShow() {
  await emit('control:started');
}

export async function triggerBorderHide() {
  await emit('control:finished');
}
