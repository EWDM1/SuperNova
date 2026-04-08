import { emit } from '@tauri-apps/api/event';

export const ControlState = {
  async activate() {
    await emit('control:started', { timestamp: Date.now() });
  },
  async deactivate() {
    await emit('control:finished', { timestamp: Date.now() });
  }
};
