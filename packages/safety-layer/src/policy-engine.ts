import { v4 as uuidv4 } from 'uuid';
import { AuditLogger, AuditEntry } from './audit-logger';

export type ActionType = 'file_write' | 'file_read' | 'cli_execute' | 'web_click' | 'web_navigate' | 'api_call' | 'ui_interact';
export type PolicyDecision = 'ALLOW' | 'DENY' | 'HITL';
export type RiskLevel = 'low' | 'medium' | 'high' | 'critical';

export interface PolicyAction {
  id: string;
  type: ActionType;
  payload: string;
  sourceApp?: string;
}

export interface PolicyEvaluation {
  decision: PolicyDecision;
  riskScore: number;
  riskLevel: RiskLevel;
  reason: string;
  timestamp: number;
  actionId: string;
}

export interface PolicyConfig {
  riskThresholds: { hitl: number; deny: number };
  allowlistPatterns: string[];
  denylistPatterns: string[];
  enableHeuristicScoring: boolean;
}

const DEFAULT_CONFIG: PolicyConfig = {
  riskThresholds: { hitl: 45, deny: 80 },
  allowlistPatterns: [],
  denylistPatterns: ['sudo rm -rf', 'DROP TABLE', 'format C:', '*/../*', 'rm -rf /', 'del /f /s /q'],
  enableHeuristicScoring: true,
};

export class PolicyEngine {
  private config: PolicyConfig;
  private sessionAllowlist: Set<string>;
  private audit?: AuditLogger;
  private readonly BASE_RISK: Record<ActionType, number> = {
    file_read: 10, web_navigate: 15, web_click: 25, api_call: 35,
    ui_interact: 40, file_write: 50, cli_execute: 75,
  };

  constructor(config: Partial<PolicyConfig> = {}, audit?: AuditLogger) {
    this.config = { ...DEFAULT_CONFIG, ...config };
    this.sessionAllowlist = new Set(this.config.allowlistPatterns);
    this.audit = audit;
  }

  evaluate(action: PolicyAction): PolicyEvaluation {
    const id = action.id || uuidv4();
    let score = this.BASE_RISK[action.type] ?? 30;
    let reason = `Base risk: ${action.type}`;

    if (this.sessionAllowlist.has(action.payload)) {
      const res = { decision: 'ALLOW' as PolicyDecision, riskScore: 0, riskLevel: 'low' as RiskLevel, reason: 'Session allowlist', timestamp: Date.now(), actionId: id };
      this.audit?.log({ ...res, payload: { type: action.type }, meta: { sessionId: '', os: process.platform, appVersion: '1.0.0' } });
      return res;
    }

    if (this.config.denylistPatterns.some(p => this.match(action.payload, p))) {
      const res = { decision: 'DENY' as PolicyDecision, riskScore: 100, riskLevel: 'critical' as RiskLevel, reason: 'Denied by policy', timestamp: Date.now(), actionId: id };
      this.audit?.log({ ...res, payload: { type: action.type }, meta: { sessionId: '', os: process.platform, appVersion: '1.0.0' } });
      return res;
    }

    if (this.config.enableHeuristicScoring) {
      score += this.heuristicScore(action.payload, action.type);
    }

    let decision: PolicyDecision = 'ALLOW';
    if (score >= this.config.riskThresholds.deny) {
      decision = 'DENY';
      reason = `Risk ${score} >= deny threshold`;
    } else if (score >= this.config.riskThresholds.hitl) {
      decision = 'HITL';
      reason = `Risk ${score} requires confirmation`;
    }

    const riskLevel = score < 30 ? 'low' : score < 60 ? 'medium' : score < 80 ? 'high' : 'critical';
    const res = { decision, riskScore: Math.min(100, score), riskLevel, reason, timestamp: Date.now(), actionId: id };
    this.audit?.log({ ...res, payload: { type: action.type, preview: action.payload.slice(0, 80) }, meta: { sessionId: '', os: process.platform, appVersion: '1.0.0' } });
    return res;
  }

  addToSessionAllowlist(payload: string) { this.sessionAllowlist.add(payload); }
  clearSessionAllowlist() { this.sessionAllowlist.clear(); }
  updateConfig(cfg: Partial<PolicyConfig>) { this.config = { ...this.config, ...cfg }; }

  private match(text: string, pattern: string): boolean {
    const safe = pattern.replace(/[.*+?^${}()|[\]\\]/g, '\\$&');
    const regex = new RegExp(safe.replace(/\*/g, '.*').replace(/\?/g, '.'), 'i');
    return regex.test(text);
  }

  private heuristicScore(payload: string, type: ActionType): number {
    let p = 0; const l = payload.toLowerCase();
    if (type === 'cli_execute' && (l.includes('sudo') || l.includes('admin'))) p += 15;
    if (l.includes('rm ') || l.includes('del ') || l.includes('erase')) p += 20;
    if (l.includes('drop ') || l.includes('truncate') || l.includes('alter ')) p += 25;
    if (l.startsWith('http://') && !l.startsWith('https://')) p += 10;
    if (payload.length > 400) p += 5;
    return p;
  }
}
