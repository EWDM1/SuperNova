import { emit } from '@tauri-apps/api/event';

export const SafetyEvents = {
  requestConfirmation: (context: string) => 
    emit('supernova:state-change', { state: 'awaiting_confirmation', timestamp: Date.now(), context }),
  
  confirmationGranted: () => 
    emit('supernova:state-change', { state: 'executing', timestamp: Date.now() }),
    
  confirmationDenied: () => 
    emit('supernova:state-change', { state: 'idle', timestamp: Date.now() })
};
