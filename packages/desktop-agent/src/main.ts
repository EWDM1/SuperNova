import { initBorderOverlay } from './overlay/BorderOverlay';
import { initHITLModal } from '../../safety-layer/src/hitl/ConfirmationModal';
import { AuditLogger } from '../../safety-layer/src/audit-logger';
import path from 'path';
import os from 'os';

async function bootstrap() {
  try {
    // 1. Inicializar Audit Logger
    const audit = new AuditLogger(
      path.join(os.homedir(), '.supernova', 'logs'),
      process.env.AUDIT_ENCRYPTION_KEY
    );
    await audit.init();

    // 2. Exponer logger globalmente para inyección en safety-layer/executor
    (globalThis as any).__supernova_audit = audit;

    // 3. Inicializar componentes de UI
    await initBorderOverlay();
    await initHITLModal();

    console.log('✅ SuperNova Desktop Agent inicializado correctamente.');
  } catch (error) {
    console.error('❌ Error crítico en bootstrap de SuperNova:', error);
  }
}

bootstrap().catch(console.error);
