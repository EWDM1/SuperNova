export type ActionType = 'file_write' | 'cli_execute' | 'web_click' | 'api_call';
export type RiskLevel = 'low' | 'medium' | 'high';
export type HITLDecision = 'allow' | 'deny' | 'allow_session';

export interface HITLRequest {
  action_id: string;
  action_type: ActionType;
  description: string;
  risk_level: RiskLevel;
  payload_preview: string;
  timeout_ms: number;
}

export interface HITLResponse {
  action_id: string;
  decision: HITLDecision;
  timestamp: number;
  trigger: 'user_click' | 'timeout';
}
