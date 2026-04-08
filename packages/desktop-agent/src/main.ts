import { initBorderOverlay } from './overlay/BorderOverlay';
import { initHITLModal } from '../../safety-layer/src/hitl/ConfirmationModal'; // Ajusta ruta relativa si es necesario
import { AuditLogger } from '../../safety-layer/src/audit-logger';
import path from 'path';
import os from 'os';

async function bootstrap() {
  // 1. Inicializar Audit Logger
  const audit = new AuditLogger(
    path.join(os.homedir(), '.supernova', 'logs'),
    process.env.AUDIT_ENCRYPTION_KEY
  );
  await audit.init();

  // 2. Inicializar Overlay & Modal HITL
  await initBorderOverlay();
  await initHITLModal();

  // 3. Expone audit globalmente para injection en safety-layer/executor
  (globalThis as any).__supernova_audit = audit;

  // ... resto de tu lógica de inicialización Tauri ...
}

bootstrap().catch(console.error);
