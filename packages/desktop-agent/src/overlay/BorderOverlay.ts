import { WebviewWindow } from '@tauri-apps/api/window';
import { listen, emit } from '@tauri-apps/api/event';

const OVERLAY_LABEL = 'supernova_control_border';
let borderWindow: WebviewWindow | null = null;

type OverlayState = 'idle' | 'executing' | 'awaiting_confirmation' | 'completed' | 'error';

export async function initBorderOverlay() {
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

  await listen<{ state: OverlayState }>('supernova:state-change', async ({ payload }) => {
    if (!borderWindow) return;
    if (payload.state !== 'idle' && !(await borderWindow.isVisible())) {
      await borderWindow.show();
    }
    await borderWindow.eval(`window.__borderAPI.setState('${payload.state}')`);
    
    if (payload.state === 'completed' || payload.state === 'error') {
      setTimeout(async () => {
        if (borderWindow && await borderWindow.isVisible()) {
          await borderWindow.eval(`window.__borderAPI.setState('idle')`);
          await borderWindow.hide();
        }
      }, 1500);
    }
  });
}

export async function triggerStateChange(state: OverlayState, context?: string) {
  await emit('supernova:state-change', { state, timestamp: Date.now(), context });
}
