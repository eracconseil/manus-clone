export type ModelType = "haiku" | "kimi" | "claude";
export type ComplexityType = "simple" | "long_context" | "complex";
export type EventType =
  | "routing"
  | "thinking"
  | "tool_call"
  | "tool_result"
  | "response"
  | "error"
  | "done";

export interface AgentEvent {
  type: EventType;
  model?: ModelType;
  complexity?: ComplexityType;
  content?: string;
  tool?: string;
  args?: Record<string, unknown>;
  result?: string;
  error?: boolean;
  message?: string;
  session_id?: string;
  iteration?: number;
}

export interface Message {
  id: string;
  role: "user" | "assistant";
  content: string;
  model?: ModelType;
  events?: AgentEvent[];
  isStreaming?: boolean;
}
