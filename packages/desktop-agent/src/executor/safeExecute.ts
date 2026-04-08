import { PolicyEngine, PolicyAction } from '../../safety-layer/src/policy-engine';
import { triggerHITLRequest } from '../../safety-layer/src/hitl/ConfirmationModal';
import { listen } from '@tauri-apps/api/event';
import fs from 'fs';
import path from 'path';

const policyConfigPath = path.join(__dirname, '../../../safety-layer/policy-config.json');
const rawConfig = fs.readFileSync(policyConfigPath, 'utf8');
const policy = new PolicyEngine(JSON.parse(rawConfig), (globalThis as any).__supernova_audit);

let hitlResolver: ((val: any) => void) | null = null;
listen('hitl:resolved', (e: any) => {
  if (hitlResolver) hitlResolver(e.payload);
});

export async function safeExecute(action: PolicyAction & { execute: () => Promise<any> }) {
  const evaluation = policy.evaluate(action);

  if (evaluation.decision === 'DENY') {
    throw new Error(`BLOCKED_BY_POLICY: ${evaluation.reason} (Score: ${evaluation.riskScore})`);
  }

  if (evaluation.decision === 'HITL') {
    await triggerHITLRequest({
      action_id: action.id,
      action_type: action.type,
      description: evaluation.reason,
      risk_level: evaluation.riskLevel,
      payload_preview: action.payload.slice(0, 150),
      timeout_ms: 30000
    });

    const response = await new Promise<any>(resolve => {
      hitlResolver = resolve;
    });

    if (response.decision === 'deny') {
      throw new Error('HITL_DENIED_BY_USER');
    }
    if (response.decision === 'allow_session') {
      policy.addToSessionAllowlist(action.payload);
    }
  }

  return await action.execute();
}
