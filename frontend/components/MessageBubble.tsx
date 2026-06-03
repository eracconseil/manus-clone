"use client";
import { ModelBadge } from "./ModelBadge";
import { ToolCallCard } from "./ToolCallCard";
import type { Message, AgentEvent } from "@/lib/types";

function renderMarkdown(text: string): React.ReactNode {
  // Simple markdown: code blocks, inline code, bold, newlines
  const parts = text.split(/(```[\s\S]*?```|`[^`]+`|\*\*[^*]+\*\*)/g);
  return parts.map((part, i) => {
    if (part.startsWith("```") && part.endsWith("```")) {
      const code = part.slice(3, -3).replace(/^\w+\n/, "");
      return <pre key={i}><code>{code}</code></pre>;
    }
    if (part.startsWith("`") && part.endsWith("`")) {
      return <code key={i}>{part.slice(1, -1)}</code>;
    }
    if (part.startsWith("**") && part.endsWith("**")) {
      return <strong key={i}>{part.slice(2, -2)}</strong>;
    }
    return <span key={i}>{part}</span>;
  });
}

function groupToolEvents(events: AgentEvent[]) {
  const groups: Array<{ call: AgentEvent; result?: AgentEvent }> = [];
  for (let i = 0; i < events.length; i++) {
    if (events[i].type === "tool_call") {
      const result = events[i + 1]?.type === "tool_result" ? events[i + 1] : undefined;
      groups.push({ call: events[i], result });
      if (result) i++;
    }
  }
  return groups;
}

export function MessageBubble({ message }: { message: Message }) {
  const isUser = message.role === "user";

  if (isUser) {
    return (
      <div className="flex justify-end mb-4">
        <div
          className="max-w-[70%] px-4 py-3 rounded-2xl rounded-tr-sm text-sm leading-relaxed"
          style={{ background: "#7c6af7", color: "#fff" }}
        >
          {message.content}
        </div>
      </div>
    );
  }

  const toolGroups = groupToolEvents(message.events ?? []);

  return (
    <div className="flex gap-3 mb-6">
      {/* Avatar */}
      <div
        className="w-7 h-7 rounded-full flex-shrink-0 flex items-center justify-center text-xs font-bold mt-0.5"
        style={{ background: "#1e1e2e", color: "#7c6af7" }}
      >
        M
      </div>

      <div className="flex-1 min-w-0">
        {/* Model badge */}
        {message.model && (
          <div className="mb-2">
            <ModelBadge model={message.model} />
          </div>
        )}

        {/* Tool calls */}
        {toolGroups.length > 0 && (
          <div className="mb-3">
            {toolGroups.map((g, i) => (
              <ToolCallCard key={i} callEvent={g.call} resultEvent={g.result} />
            ))}
          </div>
        )}

        {/* Response text */}
        {message.content && (
          <div
            className={`text-sm leading-relaxed ${message.isStreaming ? "typing-cursor" : ""}`}
            style={{ color: "#e2e2f0" }}
          >
            {renderMarkdown(message.content)}
          </div>
        )}

        {/* Loading state */}
        {message.isStreaming && !message.content && toolGroups.length === 0 && (
          <div className="flex gap-1 mt-1">
            {[0, 1, 2].map((i) => (
              <div
                key={i}
                className="w-1.5 h-1.5 rounded-full animate-bounce"
                style={{ background: "#6b6b8a", animationDelay: `${i * 0.15}s` }}
              />
            ))}
          </div>
        )}
      </div>
    </div>
  );
}
