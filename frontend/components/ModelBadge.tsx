"use client";
import type { ModelType } from "@/lib/types";

const CONFIG: Record<ModelType, { label: string; color: string; dot: string }> = {
  qwen:   { label: "Qwen 3.5",   color: "#10b981", dot: "bg-emerald-400" },
  kimi:   { label: "Kimi K2",    color: "#3b82f6", dot: "bg-blue-400" },
  claude: { label: "Claude Sonnet", color: "#f59e0b", dot: "bg-amber-400" },
};

export function ModelBadge({ model }: { model: ModelType }) {
  const cfg = CONFIG[model];
  return (
    <span
      className="inline-flex items-center gap-1.5 px-2 py-0.5 rounded-full text-xs font-medium border"
      style={{ borderColor: cfg.color + "40", color: cfg.color, background: cfg.color + "14" }}
    >
      <span className={`w-1.5 h-1.5 rounded-full ${cfg.dot}`} />
      {cfg.label}
    </span>
  );
}
