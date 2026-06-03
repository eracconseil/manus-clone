"use client";
import { useState } from "react";
import Link from "next/link";
import { Zap, MessageSquare, TrendingUp, CreditCard, ArrowLeft, Crown } from "lucide-react";
import { useProfile } from "@/lib/useProfile";
import { UpgradeModal } from "@/components/UpgradeModal";

const API_URL = process.env.NEXT_PUBLIC_API_URL ?? "http://localhost:8000";

const PLAN_CONFIG = {
  free:     { label: "Gratuit",  color: "#6b6b8a", limit: 10 },
  pro:      { label: "Pro",      color: "#7c6af7", limit: 150 },
  business: { label: "Business", color: "#f59e0b", limit: 600 },
};

export default function Dashboard() {
  const { profile, loading, refresh } = useProfile();
  const [showUpgrade, setShowUpgrade] = useState(false);

  const handleUpgrade = async (plan: string) => {
    const res = await fetch(`${API_URL}/api/billing/checkout`, {
      method: "POST",
      headers: { "Content-Type": "application/json" },
      body: JSON.stringify({ plan }),
    });
    if (res.ok) {
      const { url } = await res.json();
      window.location.href = url;
    }
  };

  const handlePortal = async () => {
    const res = await fetch(`${API_URL}/api/billing/portal`, { method: "POST" });
    if (res.ok) {
      const { url } = await res.json();
      window.location.href = url;
    }
  };

  const planCfg = PLAN_CONFIG[profile?.plan ?? "free"];
  const pct = profile ? Math.round((profile.tasks_used / profile.tasks_limit) * 100) : 0;

  return (
    <div className="min-h-full p-6 max-w-3xl mx-auto" style={{ background: "#0a0a0f" }}>
      {showUpgrade && (
        <UpgradeModal onClose={() => setShowUpgrade(false)} onSelect={handleUpgrade} />
      )}

      {/* Header */}
      <div className="flex items-center gap-3 mb-8">
        <Link href="/" className="p-2 rounded-lg hover:bg-white/5 transition-colors" style={{ color: "#6b6b8a" }}>
          <ArrowLeft size={16} />
        </Link>
        <div>
          <h1 className="text-lg font-semibold" style={{ color: "#e2e2f0" }}>Dashboard</h1>
          <p className="text-xs" style={{ color: "#6b6b8a" }}>Votre compte et votre usage</p>
        </div>
      </div>

      {loading ? (
        <div className="flex justify-center py-20">
          <div className="w-6 h-6 rounded-full border-2 border-t-transparent animate-spin" style={{ borderColor: "#7c6af7", borderTopColor: "transparent" }} />
        </div>
      ) : (
        <div className="space-y-4">
          {/* Plan actuel */}
          <div className="rounded-xl border p-5" style={{ background: "#111118", borderColor: "#1e1e2e" }}>
            <div className="flex items-center justify-between mb-4">
              <div className="flex items-center gap-2">
                <Crown size={16} style={{ color: planCfg.color }} />
                <span className="font-medium text-sm" style={{ color: "#e2e2f0" }}>
                  Plan {planCfg.label}
                </span>
                <span
                  className="text-xs px-2 py-0.5 rounded-full"
                  style={{ background: planCfg.color + "20", color: planCfg.color }}
                >
                  Actif
                </span>
              </div>
              {profile?.plan === "free" ? (
                <button
                  onClick={() => setShowUpgrade(true)}
                  className="text-xs px-3 py-1.5 rounded-lg font-medium"
                  style={{ background: "#7c6af7", color: "#fff" }}
                >
                  Upgrader
                </button>
              ) : (
                <button
                  onClick={handlePortal}
                  className="text-xs px-3 py-1.5 rounded-lg border transition-colors"
                  style={{ borderColor: "#1e1e2e", color: "#6b6b8a" }}
                >
                  Gérer l&apos;abonnement
                </button>
              )}
            </div>

            {/* Usage bar */}
            <div className="space-y-2">
              <div className="flex justify-between text-xs" style={{ color: "#6b6b8a" }}>
                <span>Tâches ce mois</span>
                <span style={{ color: "#e2e2f0" }}>
                  {profile?.tasks_used ?? 0} / {profile?.tasks_limit ?? 10}
                </span>
              </div>
              <div className="h-2 rounded-full overflow-hidden" style={{ background: "#1e1e2e" }}>
                <div
                  className="h-full rounded-full transition-all"
                  style={{
                    width: `${Math.min(pct, 100)}%`,
                    background: pct >= 90 ? "#ef4444" : pct >= 70 ? "#f59e0b" : "#7c6af7",
                  }}
                />
              </div>
              <p className="text-xs" style={{ color: "#6b6b8a" }}>
                {Math.max(0, (profile?.tasks_limit ?? 10) - (profile?.tasks_used ?? 0))} tâches restantes
              </p>
            </div>
          </div>

          {/* Stats rapides */}
          <div className="grid grid-cols-3 gap-3">
            {[
              { icon: <MessageSquare size={16} />, label: "Tâches utilisées", value: profile?.tasks_used ?? 0, color: "#7c6af7" },
              { icon: <TrendingUp size={16} />, label: "Tâches restantes", value: Math.max(0, (profile?.tasks_limit ?? 10) - (profile?.tasks_used ?? 0)), color: "#10b981" },
              { icon: <Zap size={16} />, label: "Limite mensuelle", value: profile?.tasks_limit ?? 10, color: "#f59e0b" },
            ].map((stat) => (
              <div key={stat.label} className="rounded-xl border p-4" style={{ background: "#111118", borderColor: "#1e1e2e" }}>
                <div className="mb-2" style={{ color: stat.color }}>{stat.icon}</div>
                <div className="text-2xl font-bold mb-0.5" style={{ color: "#e2e2f0" }}>{stat.value}</div>
                <div className="text-xs" style={{ color: "#6b6b8a" }}>{stat.label}</div>
              </div>
            ))}
          </div>

          {/* Comparaison des plans */}
          {profile?.plan === "free" && (
            <div className="rounded-xl border p-5" style={{ background: "#111118", borderColor: "#1e1e2e" }}>
              <h3 className="text-sm font-medium mb-4" style={{ color: "#e2e2f0" }}>Comparer les plans</h3>
              <div className="space-y-3">
                {[
                  { plan: "Gratuit", price: "0€", tasks: 10, current: profile.plan === "free" },
                  { plan: "Pro", price: "29€/mois", tasks: 150, current: false },
                  { plan: "Business", price: "99€/mois", tasks: 600, current: false },
                ].map((p) => (
                  <div
                    key={p.plan}
                    className="flex items-center justify-between p-3 rounded-lg"
                    style={{ background: p.current ? "#7c6af710" : "transparent", border: `1px solid ${p.current ? "#7c6af730" : "#1e1e2e"}` }}
                  >
                    <div className="flex items-center gap-3">
                      <span className="text-sm font-medium" style={{ color: p.current ? "#7c6af7" : "#e2e2f0" }}>{p.plan}</span>
                      {p.current && <span className="text-xs px-2 py-0.5 rounded-full" style={{ background: "#7c6af720", color: "#7c6af7" }}>Actuel</span>}
                    </div>
                    <div className="flex items-center gap-4 text-sm">
                      <span style={{ color: "#6b6b8a" }}>{p.tasks} tâches/mois</span>
                      <span style={{ color: "#e2e2f0" }}>{p.price}</span>
                    </div>
                  </div>
                ))}
              </div>
              <button
                onClick={() => setShowUpgrade(true)}
                className="w-full mt-4 py-2.5 rounded-lg text-sm font-medium"
                style={{ background: "#7c6af7", color: "#fff" }}
              >
                Passer à Pro — 29€/mois
              </button>
            </div>
          )}

          {/* Billing */}
          {profile?.plan !== "free" && (
            <div className="rounded-xl border p-5" style={{ background: "#111118", borderColor: "#1e1e2e" }}>
              <div className="flex items-center justify-between">
                <div className="flex items-center gap-2">
                  <CreditCard size={16} style={{ color: "#6b6b8a" }} />
                  <span className="text-sm" style={{ color: "#e2e2f0" }}>Facturation</span>
                </div>
                <button
                  onClick={handlePortal}
                  className="text-xs px-3 py-1.5 rounded-lg border"
                  style={{ borderColor: "#1e1e2e", color: "#6b6b8a" }}
                >
                  Gérer dans Stripe →
                </button>
              </div>
            </div>
          )}
        </div>
      )}
    </div>
  );
}
