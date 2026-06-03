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
    <div className="my-1.5 rounded-lg border overflow-hidden text-sm"
         style={{ borderColor: hasError ? "#ef444440" : "#1e1e2e", background: "#0d0d18" }}>
      <button
        onClick={() => setOpen(!open)}
        className="w-full flex items-center gap-2 px-3 py-2 text-left hover:bg-white/5 transition-colors"
      >
        <span style={{ color: "#6b6b8a" }}>{icon}</span>
        <span className="text-xs font-medium" style={{ color: "#a0a0c0" }}>{label}</span>
        {callEvent.args && (
          <span className="text-xs truncate flex-1" style={{ color: "#6b6b8a" }}>
            {Object.values(callEvent.args)[0]?.toString().slice(0, 60)}
          </span>
        )}
        {resultEvent && (
          <span className={`text-xs ml-auto ${hasError ? "text-red-400" : "text-emerald-400"}`}>
            {hasError ? "erreur" : "ok"}
          </span>
        )}
        <span style={{ color: "#6b6b8a" }}>
          {open ? <ChevronDown size={12} /> : <ChevronRight size={12} />}
        </span>
      </button>
      {open && (
        <div className="border-t px-3 py-2 space-y-2" style={{ borderColor: "#1e1e2e" }}>
          {callEvent.args && (
            <div>
              <div className="text-xs mb-1" style={{ color: "#6b6b8a" }}>Paramètres</div>
              <pre className="text-xs !p-2 !m-0" style={{ background: "#070710" }}>
                {JSON.stringify(callEvent.args, null, 2)}
              </pre>
            </div>
          )}
          {resultEvent?.result && (
            <div>
              <div className="text-xs mb-1" style={{ color: "#6b6b8a" }}>Résultat</div>
              <pre className="text-xs !p-2 !m-0 whitespace-pre-wrap" style={{ background: "#070710" }}>
                {resultEvent.result}
              </pre>
            </div>
          )}
        </div>
      )}
    </div>
  );
}
