"use client";
import { AlertTriangle } from "lucide-react";
import type { Profile } from "@/lib/useProfile";

const PLAN_LABELS: Record<string, string> = {
  free: "Gratuit",
  pro: "Pro",
  business: "Business",
};

export function UsageBanner({ profile, onUpgrade }: { profile: Profile; onUpgrade: () => void }) {
  const pct = Math.round((profile.tasks_used / profile.tasks_limit) * 100);
  const isNearLimit = pct >= 80;
  const isAtLimit = profile.tasks_used >= profile.tasks_limit;

  if (!isNearLimit) return null;

  return (
    <div
      className="flex items-center justify-between gap-3 px-4 py-2.5 text-sm border-b"
      style={{
        background: isAtLimit ? "#fdf0ed" : "#fdf8ed",
        borderColor: isAtLimit ? "#c0392b30" : "#8B691430",
        color: isAtLimit ? "#c0392b" : "#8B6914",
      }}
    >
      <div className="flex items-center gap-2">
        <AlertTriangle size={14} />
        <span>
          {isAtLimit
            ? `Limite atteinte (${profile.tasks_used}/${profile.tasks_limit} tâches)`
            : `${profile.tasks_used}/${profile.tasks_limit} tâches utilisées — limite proche`}
        </span>
      </div>
      {profile.plan === "free" && (
        <button
          onClick={onUpgrade}
          className="text-xs px-3 py-1 rounded-full font-medium"
          style={{ background: "#0D0D0D", color: "#F8F5EF" }}
        >
          Passer à Pro
        </button>
      )}
    </div>
  );
}
