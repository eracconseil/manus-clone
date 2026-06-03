"use client";
import { useState } from "react";
import Link from "next/link";
import { Zap, MessageSquare, TrendingUp, CreditCard, ArrowLeft, Crown } from "lucide-react";
import { useProfile } from "@/lib/useProfile";
import { UpgradeModal } from "@/components/UpgradeModal";

const API_URL = process.env.NEXT_PUBLIC_API_URL ?? "http://localhost:8000";

const PLAN_CONFIG = {
  free:     { label: "Gratuit",  color: "#8a7a6a", limit: 10 },
  pro:      { label: "Pro",      color: "#8B6914", limit: 150 },
  business: { label: "Business", color: "#0D0D0D", limit: 600 },
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
    <div className="min-h-full p-6 max-w-3xl mx-auto" style={{ background: "#F8F5EF" }}>
      {showUpgrade && (
        <UpgradeModal onClose={() => setShowUpgrade(false)} onSelect={handleUpgrade} />
      )}

      {/* Header */}
      <div className="flex items-center gap-3 mb-8">
        <Link href="/" className="p-2 rounded-lg transition-colors" style={{ color: "#8a7a6a" }}>
          <ArrowLeft size={16} />
        </Link>
        <div>
          <h1 className="text-lg font-bold tracking-wide" style={{ color: "#0D0D0D", fontFamily: "'Georgia', serif" }}>
            Dashboard
          </h1>
          <p className="text-xs" style={{ color: "#8a7a6a" }}>Votre compte et votre usage</p>
        </div>
      </div>

      {loading ? (
        <div className="flex justify-center py-20">
          <div className="w-6 h-6 rounded-full border-2 animate-spin" style={{ borderColor: "#8B6914", borderTopColor: "transparent" }} />
        </div>
      ) : (
        <div className="space-y-4">
          {/* Plan actuel */}
          <div className="rounded-xl border p-5" style={{ background: "#ffffff", borderColor: "#e8e0d0" }}>
            <div className="flex items-center justify-between mb-4">
              <div className="flex items-center gap-2">
                <Crown size={16} style={{ color: planCfg.color }} />
                <span className="font-medium text-sm" style={{ color: "#0D0D0D" }}>
                  Plan {planCfg.label}
                </span>
                <span
                  className="text-xs px-2 py-0.5 rounded-full"
                  style={{ background: planCfg.color + "15", color: planCfg.color, border: `1px solid ${planCfg.color}30` }}
                >
                  Actif
                </span>
              </div>
              {profile?.plan === "free" ? (
                <button
                  onClick={() => setShowUpgrade(true)}
                  className="text-xs px-3 py-1.5 rounded-lg font-medium"
                  style={{ background: "#0D0D0D", color: "#F8F5EF" }}
                >
                  Upgrader
                </button>
              ) : (
                <button
                  onClick={handlePortal}
                  className="text-xs px-3 py-1.5 rounded-lg border transition-colors"
                  style={{ borderColor: "#e8e0d0", color: "#8a7a6a" }}
                >
                  Gérer l&apos;abonnement
                </button>
              )}
            </div>

            {/* Usage bar */}
            <div className="space-y-2">
              <div className="flex justify-between text-xs" style={{ color: "#8a7a6a" }}>
                <span>Tâches ce mois</span>
                <span style={{ color: "#0D0D0D" }}>
                  {profile?.tasks_used ?? 0} / {profile?.tasks_limit ?? 10}
                </span>
              </div>
              <div className="h-2 rounded-full overflow-hidden" style={{ background: "#e8e0d0" }}>
                <div
                  className="h-full rounded-full transition-all"
                  style={{
                    width: `${Math.min(pct, 100)}%`,
                    background: pct >= 90 ? "#c0392b" : pct >= 70 ? "#8B6914" : "#0D0D0D",
                  }}
                />
              </div>
              <p className="text-xs" style={{ color: "#8a7a6a" }}>
                {Math.max(0, (profile?.tasks_limit ?? 10) - (profile?.tasks_used ?? 0))} tâches restantes
              </p>
            </div>
          </div>

          {/* Stats rapides */}
          <div className="grid grid-cols-3 gap-3">
            {[
              { icon: <MessageSquare size={16} />, label: "Tâches utilisées", value: profile?.tasks_used ?? 0, color: "#8B6914" },
              { icon: <TrendingUp size={16} />, label: "Tâches restantes", value: Math.max(0, (profile?.tasks_limit ?? 10) - (profile?.tasks_used ?? 0)), color: "#2d7a4a" },
              { icon: <Zap size={16} />, label: "Limite mensuelle", value: profile?.tasks_limit ?? 10, color: "#0D0D0D" },
            ].map((stat) => (
              <div key={stat.label} className="rounded-xl border p-4" style={{ background: "#ffffff", borderColor: "#e8e0d0" }}>
                <div className="mb-2" style={{ color: stat.color }}>{stat.icon}</div>
                <div className="text-2xl font-bold mb-0.5" style={{ color: "#0D0D0D" }}>{stat.value}</div>
                <div className="text-xs" style={{ color: "#8a7a6a" }}>{stat.label}</div>
              </div>
            ))}
          </div>

          {/* Comparaison des plans */}
          {profile?.plan === "free" && (
            <div className="rounded-xl border p-5" style={{ background: "#ffffff", borderColor: "#e8e0d0" }}>
              <h3 className="text-sm font-bold mb-4 tracking-wide" style={{ color: "#0D0D0D", fontFamily: "'Georgia', serif" }}>
                Comparer les plans
              </h3>
              <div className="space-y-3">
                {[
                  { plan: "Gratuit", price: "0€", tasks: 10, current: profile.plan === "free" },
                  { plan: "Pro", price: "29€/mois", tasks: 150, current: false },
                  { plan: "Business", price: "99€/mois", tasks: 600, current: false },
                ].map((p) => (
                  <div
                    key={p.plan}
                    className="flex items-center justify-between p-3 rounded-lg"
                    style={{
                      background: p.current ? "#f0ece4" : "transparent",
                      border: `1px solid ${p.current ? "#8B691440" : "#e8e0d0"}`,
                    }}
                  >
                    <div className="flex items-center gap-3">
                      <span className="text-sm font-medium" style={{ color: p.current ? "#8B6914" : "#0D0D0D" }}>{p.plan}</span>
                      {p.current && (
                        <span className="text-xs px-2 py-0.5 rounded-full" style={{ background: "#8B691420", color: "#8B6914" }}>
                          Actuel
                        </span>
                      )}
                    </div>
                    <div className="flex items-center gap-4 text-sm">
                      <span style={{ color: "#8a7a6a" }}>{p.tasks} tâches/mois</span>
                      <span style={{ color: "#0D0D0D" }}>{p.price}</span>
                    </div>
                  </div>
                ))}
              </div>
              <button
                onClick={() => setShowUpgrade(true)}
                className="w-full mt-4 py-2.5 rounded-lg text-sm font-medium"
                style={{ background: "#0D0D0D", color: "#F8F5EF" }}
              >
                Passer à Pro — 29€/mois
              </button>
            </div>
          )}

          {/* Billing */}
          {profile?.plan !== "free" && (
            <div className="rounded-xl border p-5" style={{ background: "#ffffff", borderColor: "#e8e0d0" }}>
              <div className="flex items-center justify-between">
                <div className="flex items-center gap-2">
                  <CreditCard size={16} style={{ color: "#8a7a6a" }} />
                  <span className="text-sm" style={{ color: "#0D0D0D" }}>Facturation</span>
                </div>
                <button
                  onClick={handlePortal}
                  className="text-xs px-3 py-1.5 rounded-lg border"
                  style={{ borderColor: "#e8e0d0", color: "#8a7a6a" }}
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
