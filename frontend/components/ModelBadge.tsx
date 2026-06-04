"use client";
import type { ModelType } from "@/lib/types";

const CONFIG: Record<ModelType, { label: string; color: string }> = {
  haiku:  { label: "Haiku · rapide",    color: "#2d7a4a" },
  kimi:   { label: "Kimi K2 · long",    color: "#1a4a8a" },
  claude: { label: "Claude · complexe", color: "#8B6914" },
};

export function ModelBadge({ model }: { model: ModelType }) {
  const cfg = CONFIG[model] ?? CONFIG.haiku;
  return (
    <span
      className="inline-flex items-center gap-1.5 px-2 py-0.5 rounded-full text-xs font-medium border"
      style={{ borderColor: cfg.color + "30", color: cfg.color, background: cfg.color + "10" }}
    >
      <span className="w-1.5 h-1.5 rounded-full inline-block" style={{ background: cfg.color }} />
      {cfg.label}
    </span>
  );
}
