"use client";
import { useState, useRef, useEffect } from "react";
import { Send, Loader2 } from "lucide-react";

interface Props {
  onSend: (text: string) => void;
  disabled?: boolean;
}

const SUGGESTIONS = [
  "Écris un script Python pour analyser un fichier CSV",
  "Recherche les meilleures pratiques pour lancer un SaaS B2B",
  "Crée un plan marketing en 5 étapes pour une app mobile",
  "Explique le fonctionnement d'une architecture microservices",
];

export function ChatInput({ onSend, disabled }: Props) {
  const [value, setValue] = useState("");
  const textareaRef = useRef<HTMLTextAreaElement>(null);

  useEffect(() => {
    if (textareaRef.current) {
      textareaRef.current.style.height = "auto";
      textareaRef.current.style.height = Math.min(textareaRef.current.scrollHeight, 160) + "px";
    }
  }, [value]);

  const submit = () => {
    const trimmed = value.trim();
    if (!trimmed || disabled) return;
    onSend(trimmed);
    setValue("");
  };

  const onKey = (e: React.KeyboardEvent) => {
    if (e.key === "Enter" && !e.shiftKey) {
      e.preventDefault();
      submit();
    }
  };

  return (
    <div className="p-4">
      <div
        className="rounded-2xl border transition-colors"
        style={{ background: "#ffffff", borderColor: "#e8e0d0" }}
      >
        <textarea
          ref={textareaRef}
          value={value}
          onChange={(e) => setValue(e.target.value)}
          onKeyDown={onKey}
          placeholder="Donne une tâche à Orion..."
          disabled={disabled}
          rows={1}
          className="w-full bg-transparent px-4 pt-3 pb-2 text-sm resize-none outline-none leading-relaxed"
          style={{ color: "#0D0D0D", minHeight: 44 }}
        />
        <div className="flex items-center justify-between px-3 pb-2">
          <span className="text-xs" style={{ color: "#8a7a6a" }}>
            Shift+Enter pour nouvelle ligne
          </span>
          <button
            onClick={submit}
            disabled={!value.trim() || disabled}
            className="flex items-center gap-1.5 px-3 py-1.5 rounded-lg text-xs font-medium transition-all disabled:opacity-40"
            style={{ background: "#0D0D0D", color: "#F8F5EF" }}
          >
            {disabled ? <Loader2 size={13} className="animate-spin" /> : <Send size={13} />}
            Envoyer
          </button>
        </div>
      </div>

      {/* Suggestions */}
      <div className="flex gap-2 mt-2 flex-wrap">
        {SUGGESTIONS.map((s, i) => (
          <button
            key={i}
            onClick={() => !disabled && onSend(s)}
            disabled={disabled}
            className="text-xs px-3 py-1.5 rounded-full border transition-colors disabled:opacity-40"
            style={{ borderColor: "#e8e0d0", color: "#8a7a6a", background: "#ffffff" }}
          >
            {s.slice(0, 40)}…
          </button>
        ))}
      </div>
    </div>
  );
}
