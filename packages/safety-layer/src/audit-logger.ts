import fs from 'fs';
import path from 'path';
import crypto from 'crypto';

export type AuditEventType = 
  | 'policy_eval' 
  | 'hitl_request' 
  | 'hitl_response' 
  | 'action_start' 
  | 'action_success' 
  | 'action_error' 
  | 'session_init' 
  | 'session_close';

export interface AuditEntry {
  id: string;
  timestamp: number;
  type: AuditEventType;
  riskScore?: number;
  decision?: string;
  payload: Record<string, any>;
  meta: { sessionId: string; os: string; appVersion: string };
}

export class AuditLogger {
  private logDir: string;
  private stream: fs.WriteStream | null = null;
  private currentSize = 0;
  private readonly maxSize = 5 * 1024 * 1024; // 5MB por archivo
  private readonly queue: AuditEntry[] = [];
  private readonly key?: Buffer;
  private isFlushing = false;
  private sessionId: string;

  constructor(logDir: string, encryptionKey?: string) {
    this.logDir = logDir;
    this.sessionId = crypto.randomUUID();
    if (encryptionKey) this.key = crypto.createHash('sha256').update(encryptionKey).digest();
  }

  async init() {
    await fs.promises.mkdir(this.logDir, { recursive: true });
    await this.rotate();
    setInterval(() => this.rotate(), 86400000);
    setInterval(() => this.flush(), 1500);
    if (process.on) process.on('SIGTERM', async () => { await this.flush(); });
  }

  log(entry: AuditEntry) {
    this.queue.push({ ...entry, meta: { ...entry.meta, sessionId: this.sessionId } });
    if (this.queue.length > 200) this.flush();
  }

  async flush() {
    if (this.isFlushing || this.queue.length === 0 || !this.stream) return;
    this.isFlushing = true;
    const batch = this.queue.splice(0, this.queue.length);
    try {
      for (const e of batch) {
        const line = JSON.stringify({ ...e, _schema: 'supernova-audit-v1' });
        const data = this.key ? this.encrypt(line) : line;
        if (this.currentSize + data.length + 1 > this.maxSize) await this.rotate();
        this.stream.write(data + '\n');
        this.currentSize += data.length + 1;
      }
    } finally {
      this.isFlushing = false;
    }
  }

  private encrypt(text: string): string {
    if (!this.key) return text;
    const iv = crypto.randomBytes(16);
    const cipher = crypto.createCipheriv('aes-256-gcm', this.key, iv);
    let enc = cipher.update(text, 'utf8', 'hex') + cipher.final('hex');
    return JSON.stringify({ iv: iv.toString('hex'), tag: cipher.getAuthTag().toString('hex'), d: enc });
  }

  private async rotate() {
    this.stream?.end();
    const date = new Date().toISOString().split('T')[0];
    try {
      const files = (await fs.promises.readdir(this.logDir)).filter(f => f.startsWith(`audit-${date}`));
      const idx = files.length.toString().padStart(2, '0');
      const filepath = path.join(this.logDir, `audit-${date}-${idx}.jsonl`);
      this.stream = fs.createWriteStream(filepath, { flags: 'a' });
      this.currentSize = (await fs.promises.stat(filepath).catch(() => ({ size: 0 }))).size || 0;
    } catch {
      this.stream = null;
    }
  }
}
