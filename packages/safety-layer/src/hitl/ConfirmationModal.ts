import { WebviewWindow } from '@tauri-apps/api/window';
import { listen, emit } from '@tauri-apps/api/event';
import { HITLRequest, HITLResponse } from './types';

const MODAL_LABEL = 'supernova_hitl_confirmation';
let pendingResolvers = new Map<string, { resolve: (r: HITLResponse) => void; timeout: NodeJS.Timeout }>();
let modalWindow: WebviewWindow | null = null;

export async function initHITLModal() {
  modalWindow = new WebviewWindow(MODAL_LABEL, {
    url: './src/hitl/ConfirmationModal.html',
    title: 'SuperNova: Confirmar Acción',
    width: 480, height: 380,
    decorations: false, transparent: false, alwaysOnTop: true,
    skipTaskbar: true, focus: true, resizable: false, visible: false,
    center: true
  });

  await listen<{ request: HITLRequest }>('hitl:request', async ({ payload }) => {
    await showModal(payload.request);
  });

  await listen<{ decision: HITLResponse['decision']; trigger: HITLResponse['trigger'] }>('hitl:response', async ({ payload }) => {
    const activeReq = [...pendingResolvers.values()].pop();
    if (activeReq) {
      clearTimeout(activeReq.timeout);
      activeReq.resolve({
        action_id: 'pending', // Se asigna en request
        decision: payload.decision,
        timestamp: Date.now(),
        trigger: payload.trigger
      });
      await modalWindow?.hide();
      await modalWindow?.eval('window.__hitlAPI.close()');
    }
  });
}

async function showModal(req: HITLRequest) {
  if (!modalWindow) return;
  
  const promise = new Promise<HITLResponse>((resolve) => {
    pendingResolvers.set(req.action_id, { resolve, timeout: setTimeout(() => {
      modalWindow?.eval(`window.respond('deny', 'timeout')`);
    }, req.timeout_ms) });
  });

  await modalWindow.eval(`window.__hitlAPI.open(${JSON.stringify(req)})`);
  await modalWindow.show();
  
  const response = await promise;
  response.action_id = req.action_id; // Assign ID post-resolution
  await emit('hitl:resolved', response);
}

// Expuesto para el safety-layer
export async function triggerHITLRequest(req: HITLRequest) {
  await emit('hitl:request', { request: req });
}
