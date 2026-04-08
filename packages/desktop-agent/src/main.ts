import { initBorderOverlay } from './overlay/BorderOverlay';
import { invoke } from '@tauri-apps/api/tauri';

async function bootstrap() {
  // 1. Inicializar overlay
  await initBorderOverlay();

  // 2. Hook en el ciclo de ejecución del agente
  // Ejemplo: wrapper alrededor del action-executor
  const originalExecute = window.__actionExecutor?.run;
  if (originalExecute) {
    window.__actionExecutor.run = async (task: any) => {
      await invoke('emit', { event: 'control:started' });
      try {
        return await originalExecute(task);
      } finally {
        await invoke('emit', { event: 'control:finished' });
      }
    };
  }
}

bootstrap().catch(console.error);
