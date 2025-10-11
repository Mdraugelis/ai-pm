export type AgentMode = 'ai_discovery' | 'risk_assessment' | 'poc_planning' | 'general';

export type ThinkingStep = 'gather' | 'plan' | 'execute' | 'verify';

export type ThinkingEvent = {
  step: ThinkingStep;
  iteration: number;
  confidence?: number;
  reasoning: string;
  details?: any;
  timestamp?: string;
};

export type MessageTurn = {
  role: 'user' | 'assistant';
  content: string;
  timestamp: string;
  thinking?: ThinkingEvent[];
};

export type ConversationHistory = {
  messages: MessageTurn[];
  mode: AgentMode;
  session_id?: string;
};

export type DocumentInfo = {
  doc_id: number;
  doc_type: string;
  added_at: string;
  content_length: number;
  metadata: Record<string, any>;
};

export type AgentResponse = {
  response: string;
  thinking?: ThinkingEvent[];
  complete: boolean;
};

export type StreamEvent = {
  type: 'thinking' | 'iteration' | 'response' | 'complete' | 'error';
  data: any;
};