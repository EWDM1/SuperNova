import { AuditLogger, AuditEntry } from './audit-logger';

export class PolicyEngine {
  // ... existing code ...
  constructor(private audit?: AuditLogger) { /* ... */ }

  evaluate(action: any) {
    const result = /* ... existing logic ... */;
    this.audit?.log({
      id: result.actionId,
      timestamp: Date.now(),
      type: 'policy_eval',
      riskScore: result.riskScore,
      decision: result.decision,
      payload: { action_type: action.type, payload_preview: action.payload.slice(0, 80) },
      metadata: { sessionId: '...', os: process.platform, appVersion: '1.0.0' }
    });
    return result;
  }
}
