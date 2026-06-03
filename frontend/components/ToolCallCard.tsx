"use client";
import { useState } from "react";
import { ChevronDown, ChevronRight, Terminal, Globe, FileText, Search } from "lucide-react";
import type { AgentEvent } from "@/lib/types";

const TOOL_ICONS: Record<string, React.ReactNode> = {
  web_search:      <Search size={13} />,
  browser_navigate:<Globe size={13} />,
  code_executor:   <Terminal size={13} />,
  file_read:       <FileText size={13} />,
  file_write:      <FileText size={13} />,
  file_list:       <FileText size={13} />,
};

const TOOL_LABELS: Record<string, string> = {
  web_search:      "Recherche web",
  browser_navigate:"Navigation",
  code_executor:   "Exécution code",
  file_read:       "Lecture fichier",
  file_write:      "Écriture fichier",
  file_list:       "Liste fichiers",
};

interface Props {
  callEvent: AgentEvent;
  resultEvent?: AgentEvent;
}

export function ToolCallCard({ callEvent, resultEvent }: Props) {
  const [open, setOpen] = useState(false);
  const tool = callEvent.tool ?? "";
  const label = TOOL_LABELS[tool] ?? tool;
  const icon = TOOL_ICONS[tool] ?? <Terminal size={13} />;
  const hasError = resultEvent?.error;

  return (
    <div
      className="my-1.5 rounded-lg border overflow-hidden text-sm"
      style={{ borderColor: hasError ? "#c0392b40" : "#e8e0d0", background: "#f0ece4" }}
    >
      <button
        onClick={() => setOpen(!open)}
        className="w-full flex items-center gap-2 px-3 py-2 text-left transition-colors"
        style={{ background: "transparent" }}
      >
        <span style={{ color: "#8B6914" }}>{icon}</span>
        <span className="text-xs font-medium" style={{ color: "#0D0D0D" }}>{label}</span>
        {callEvent.args && (
          <span className="text-xs truncate flex-1" style={{ color: "#8a7a6a" }}>
            {Object.values(callEvent.args)[0]?.toString().slice(0, 60)}
          </span>
        )}
        {resultEvent && (
          <span className={`text-xs ml-auto font-medium`} style={{ color: hasError ? "#c0392b" : "#2d7a4a" }}>
            {hasError ? "erreur" : "ok"}
          </span>
        )}
        <span style={{ color: "#8a7a6a" }}>
          {open ? <ChevronDown size={12} /> : <ChevronRight size={12} />}
        </span>
      </button>
      {open && (
        <div className="border-t px-3 py-2 space-y-2" style={{ borderColor: "#e8e0d0" }}>
          {callEvent.args && (
            <div>
              <div className="text-xs mb-1" style={{ color: "#8a7a6a" }}>Paramètres</div>
              <pre className="text-xs !p-2 !m-0" style={{ background: "#ede8df" }}>
                {JSON.stringify(callEvent.args, null, 2)}
              </pre>
            </div>
          )}
          {resultEvent?.result && (
            <div>
              <div className="text-xs mb-1" style={{ color: "#8a7a6a" }}>Résultat</div>
              <pre className="text-xs !p-2 !m-0 whitespace-pre-wrap" style={{ background: "#ede8df" }}>
                {resultEvent.result}
              </pre>
            </div>
          )}
        </div>
      )}
    </div>
  );
}
