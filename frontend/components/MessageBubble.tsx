"use client";
import ReactMarkdown from "react-markdown";
import remarkGfm from "remark-gfm";
import { ModelBadge } from "./ModelBadge";
import { ToolCallCard } from "./ToolCallCard";
import type { Message, AgentEvent } from "@/lib/types";

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

const mdComponents = {
  h1: ({ children }: any) => (
    <h1 style={{ fontSize: 18, fontWeight: 700, color: "#0D0D0D", margin: "16px 0 8px", fontFamily: "'Georgia', serif", borderBottom: "1px solid #e8e0d0", paddingBottom: 6 }}>{children}</h1>
  ),
  h2: ({ children }: any) => (
    <h2 style={{ fontSize: 15, fontWeight: 700, color: "#0D0D0D", margin: "14px 0 6px", fontFamily: "'Georgia', serif" }}>{children}</h2>
  ),
  h3: ({ children }: any) => (
    <h3 style={{ fontSize: 13, fontWeight: 600, color: "#2a1a0a", margin: "10px 0 4px" }}>{children}</h3>
  ),
  p: ({ children }: any) => (
    <p style={{ margin: "6px 0", lineHeight: 1.7, color: "#0D0D0D" }}>{children}</p>
  ),
  ul: ({ children }: any) => (
    <ul style={{ margin: "6px 0", paddingLeft: 20, listStyleType: "disc" }}>{children}</ul>
  ),
  ol: ({ children }: any) => (
    <ol style={{ margin: "6px 0", paddingLeft: 20 }}>{children}</ol>
  ),
  li: ({ children }: any) => (
    <li style={{ margin: "3px 0", lineHeight: 1.6, color: "#0D0D0D" }}>{children}</li>
  ),
  strong: ({ children }: any) => (
    <strong style={{ fontWeight: 700, color: "#0D0D0D" }}>{children}</strong>
  ),
  em: ({ children }: any) => (
    <em style={{ fontStyle: "italic", color: "#4a3a2a" }}>{children}</em>
  ),
  code: ({ inline, children }: any) =>
    inline ? (
      <code style={{ background: "#ede8df", border: "1px solid #e8e0d0", borderRadius: 4, padding: "1px 5px", fontSize: 12, fontFamily: "monospace", color: "#8B6914" }}>{children}</code>
    ) : (
      <pre style={{ background: "#f0ece4", border: "1px solid #e8e0d0", borderRadius: 8, padding: "10px 14px", overflowX: "auto", margin: "8px 0" }}>
        <code style={{ fontSize: 12, fontFamily: "monospace", color: "#2a1a0a" }}>{children}</code>
      </pre>
    ),
  blockquote: ({ children }: any) => (
    <blockquote style={{ borderLeft: "3px solid #8B6914", margin: "8px 0", paddingLeft: 12, color: "#6a5a4a", fontStyle: "italic" }}>{children}</blockquote>
  ),
  hr: () => (
    <hr style={{ border: "none", borderTop: "1px solid #e8e0d0", margin: "12px 0" }} />
  ),
  table: ({ children }: any) => (
    <div style={{ overflowX: "auto", margin: "8px 0" }}>
      <table style={{ borderCollapse: "collapse", width: "100%", fontSize: 13 }}>{children}</table>
    </div>
  ),
  th: ({ children }: any) => (
    <th style={{ border: "1px solid #e8e0d0", padding: "6px 10px", background: "#f0ece4", fontWeight: 600, textAlign: "left", color: "#0D0D0D" }}>{children}</th>
  ),
  td: ({ children }: any) => (
    <td style={{ border: "1px solid #e8e0d0", padding: "5px 10px", color: "#0D0D0D" }}>{children}</td>
  ),
};

export function MessageBubble({ message }: { message: Message }) {
  const isUser = message.role === "user";

  if (isUser) {
    return (
      <div className="flex justify-end mb-4">
        <div
          className="max-w-[70%] px-4 py-3 rounded-2xl rounded-tr-sm text-sm leading-relaxed"
          style={{ background: "#0D0D0D", color: "#F8F5EF" }}
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
        style={{ background: "#0D0D0D", color: "#F8F5EF", fontFamily: "'Georgia', serif" }}
      >
        O
      </div>

      <div className="flex-1 min-w-0">
        {message.model && (
          <div className="mb-2">
            <ModelBadge model={message.model} />
          </div>
        )}

        {toolGroups.length > 0 && (
          <div className="mb-3">
            {toolGroups.map((g, i) => (
              <ToolCallCard key={i} callEvent={g.call} resultEvent={g.result} />
            ))}
          </div>
        )}

        {message.content && (
          <div className={`text-sm ${message.isStreaming ? "typing-cursor" : ""}`}>
            <ReactMarkdown
              remarkPlugins={[remarkGfm]}
              components={mdComponents as any}
            >
              {message.content}
            </ReactMarkdown>
          </div>
        )}

        {message.isStreaming && !message.content && toolGroups.length === 0 && (
          <div className="flex gap-1 mt-1">
            {[0, 1, 2].map((i) => (
              <div
                key={i}
                className="w-1.5 h-1.5 rounded-full animate-bounce"
                style={{ background: "#8a7a6a", animationDelay: `${i * 0.15}s` }}
              />
            ))}
          </div>
        )}
      </div>
    </div>
  );
}
