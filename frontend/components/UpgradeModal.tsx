"use client";
import { X, Zap, Building2, Check } from "lucide-react";

const PLANS = [
  {
    id: "pro",
    name: "Pro",
    price: "29",
    tasks: 150,
    features: ["150 tâches/mois", "Tous les modèles", "Historique illimité", "Support prioritaire"],
    icon: <Zap size={18} />,
    accent: "#7c6af7",
  },
  {
    id: "business",
    name: "Business",
    price: "99",
    tasks: 600,
    features: ["600 tâches/mois", "API access", "Usage analytics", "SLA 99.9%", "Support dédié"],
    icon: <Building2 size={18} />,
    accent: "#f59e0b",
  },
];

interface Props {
  onClose: () => void;
  onSelect: (plan: string) => void;
}

export function UpgradeModal({ onClose, onSelect }: Props) {
  return (
    <div
      className="fixed inset-0 z-50 flex items-center justify-center p-4"
      style={{ background: "rgba(0,0,0,0.7)", backdropFilter: "blur(4px)" }}
      onClick={(e) => e.target === e.currentTarget && onClose()}
    >
      <div
        className="w-full max-w-2xl rounded-2xl border p-6"
        style={{ background: "#111118", borderColor: "#1e1e2e" }}
      >
        <div className="flex items-center justify-between mb-6">
          <div>
            <h2 className="text-lg font-semibold" style={{ color: "#e2e2f0" }}>
              Choisir un plan
            </h2>
            <p className="text-sm mt-0.5" style={{ color: "#6b6b8a" }}>
              Débloquez plus de tâches et toutes les fonctionnalités
            </p>
          </div>
          <button
            onClick={onClose}
            className="p-1.5 rounded-lg hover:bg-white/5"
            style={{ color: "#6b6b8a" }}
          >
            <X size={18} />
          </button>
        </div>

        <div className="grid grid-cols-2 gap-4">
          {PLANS.map((plan) => (
            <div
              key={plan.id}
              className="rounded-xl border p-5"
              style={{ borderColor: plan.accent + "40", background: plan.accent + "08" }}
            >
              <div className="flex items-center gap-2 mb-3" style={{ color: plan.accent }}>
                {plan.icon}
                <span className="font-semibold">{plan.name}</span>
              </div>

              <div className="mb-4">
                <span className="text-3xl font-bold" style={{ color: "#e2e2f0" }}>
                  {plan.price}€
                </span>
                <span className="text-sm ml-1" style={{ color: "#6b6b8a" }}>/mois</span>
              </div>

              <ul className="space-y-2 mb-5">
                {plan.features.map((f) => (
                  <li key={f} className="flex items-center gap-2 text-sm" style={{ color: "#a0a0c0" }}>
                    <Check size={13} style={{ color: plan.accent }} />
                    {f}
                  </li>
                ))}
              </ul>

              <button
                onClick={() => onSelect(plan.id)}
                className="w-full py-2 rounded-lg text-sm font-medium transition-opacity hover:opacity-90"
                style={{ background: plan.accent, color: "#fff" }}
              >
                Choisir {plan.name}
              </button>
            </div>
          ))}
        </div>
      </div>
    </div>
  );
}
