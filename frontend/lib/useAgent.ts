"use client";
import { useState, useCallback, useRef } from "react";
import type { Message, AgentEvent, ModelType } from "./types";

const API_URL = process.env.NEXT_PUBLIC_API_URL ?? "https://manus-clone-production.up.railway.app";

function uid() {
  return Math.random().toString(36).slice(2);
}

export function useAgent() {
  const [messages, setMessages] = useState<Message[]>([]);
  const [isLoading, setIsLoading] = useState(false);
  const sessionId = useRef(uid());

  const sendMessage = useCallback(async (text: string) => {
    const userMsg: Message = { id: uid(), role: "user", content: text };
    const assistantMsg: Message = {
      id: uid(),
      role: "assistant",
      content: "",
      events: [],
      isStreaming: true,
    };

    setMessages((prev) => [...prev, userMsg, assistantMsg]);
    setIsLoading(true);

    try {
      const res = await fetch(`${API_URL}/api/agent/run`, {
        method: "POST",
        headers: { "Content-Type": "application/json" },
        body: JSON.stringify({ session_id: sessionId.current, message: text }),
      });

      if (!res.ok || !res.body) throw new Error(`HTTP ${res.status}`);

      const reader = res.body.getReader();
      const decoder = new TextDecoder();
      let buffer = "";

      while (true) {
        const { done, value } = await reader.read();
        if (done) break;

        buffer += decoder.decode(value, { stream: true });
        const lines = buffer.split("\n");
        buffer = lines.pop() ?? "";

        for (const line of lines) {
          if (!line.startsWith("data:")) continue;
          try {
            const event: AgentEvent = JSON.parse(line.slice(5).trim());
            setMessages((prev) => {
              const msgs = [...prev];
              const idx = msgs.findIndex((m) => m.id === assistantMsg.id);
              if (idx === -1) return prev;
              const msg = { ...msgs[idx] };

              if (event.type === "routing") {
                msg.model = event.model as ModelType;
              } else if (event.type === "response" && event.content) {
                msg.content += event.content;
              } else if (event.type === "done") {
                msg.isStreaming = false;
              } else {
                msg.events = [...(msg.events ?? []), event];
              }

              msgs[idx] = msg;
              return msgs;
            });
          } catch {
            // skip malformed line
          }
        }
      }
    } catch (err) {
      setMessages((prev) => {
        const msgs = [...prev];
        const idx = msgs.findIndex((m) => m.id === assistantMsg.id);
        if (idx !== -1) {
          msgs[idx] = {
            ...msgs[idx],
            content: `Erreur : ${err instanceof Error ? err.message : "inconnue"}`,
            isStreaming: false,
          };
        }
        return msgs;
      });
    } finally {
      setIsLoading(false);
    }
  }, []);

  return { messages, isLoading, sendMessage };
}
