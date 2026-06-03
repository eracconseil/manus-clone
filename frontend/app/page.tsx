"use client";
import { useEffect, useRef, useState } from "react";
import Link from "next/link";
import { useAgent } from "@/lib/useAgent";
import { useProfile } from "@/lib/useProfile";
import { MessageBubble } from "@/components/MessageBubble";
import { ChatInput } from "@/components/ChatInput";
import { UsageBanner } from "@/components/UsageBanner";
import { UpgradeModal } from "@/components/UpgradeModal";
import { Zap, LayoutDashboard } from "lucide-react";

const API_URL = process.env.NEXT_PUBLIC_API_URL ?? "http://localhost:8000";

export default function Home() {
  const { messages, isLoading, sendMessage } = useAgent();
  const { profile, refresh } = useProfile();
  const [showUpgrade, setShowUpgrade] = useState(false);
  const bottomRef = useRef<HTMLDivElement>(null);

  useEffect(() => {
    bottomRef.current?.scrollIntoView({ behavior: "smooth" });
  }, [messages]);

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

  const handleSend = async (text: string) => {
    await sendMessage(text);
    refresh();
  };

  return (
    <div className="flex flex-col h-full" style={{ background: "#0a0a0f" }}>
      {showUpgrade && (
        <UpgradeModal onClose={() => setShowUpgrade(false)} onSelect={handleUpgrade} />
      )}

      {/* Header */}
      <header
        className="flex items-center justify-between px-6 py-3 border-b flex-shrink-0"
        style={{ borderColor: "#1e1e2e", background: "#0a0a0f" }}
      >
        <div className="flex items-center gap-2">
          <div className="w-7 h-7 rounded-lg flex items-center justify-center" style={{ background: "#7c6af7" }}>
            <Zap size={14} color="#fff" />
          </div>
          <span className="font-semibold text-sm" style={{ color: "#e2e2f0" }}>ManusClone</span>
          <span className="text-xs px-2 py-0.5 rounded-full border" style={{ color: "#6b6b8a", borderColor: "#1e1e2e" }}>
            beta
          </span>
        </div>

        <div className="flex items-center gap-4">
          {/* Model legend */}
          <div className="hidden sm:flex items-center gap-4 text-xs" style={{ color: "#6b6b8a" }}>
            <span className="flex items-center gap-1"><span className="w-1.5 h-1.5 rounded-full bg-emerald-400 inline-block" />Qwen · simple</span>
            <span className="flex items-center gap-1"><span className="w-1.5 h-1.5 rounded-full bg-blue-400 inline-block" />Kimi · long</span>
            <span className="flex items-center gap-1"><span className="w-1.5 h-1.5 rounded-full bg-amber-400 inline-block" />Claude · complexe</span>
          </div>

          {/* Usage pill */}
          {profile && (
            <button
              onClick={() => setShowUpgrade(true)}
              className="hidden sm:flex items-center gap-1.5 text-xs px-3 py-1.5 rounded-full border transition-colors hover:border-violet-500/40"
              style={{ borderColor: "#1e1e2e", color: "#6b6b8a" }}
            >
              <span style={{ color: "#e2e2f0" }}>{profile.tasks_used}/{profile.tasks_limit}</span>
              tâches · {profile.plan}
            </button>
          )}

          <Link
            href="/dashboard"
            className="p-1.5 rounded-lg hover:bg-white/5 transition-colors"
            style={{ color: "#6b6b8a" }}
          >
            <LayoutDashboard size={16} />
          </Link>
        </div>
      </header>

      {/* Usage banner si limite proche */}
      {profile && (
        <UsageBanner profile={profile} onUpgrade={() => setShowUpgrade(true)} />
      )}

      {/* Messages */}
      <div className="flex-1 overflow-y-auto px-4 py-6 max-w-3xl mx-auto w-full">
        {messages.length === 0 ? (
          <div className="flex flex-col items-center justify-center h-full text-center gap-4">
            <div
              className="w-16 h-16 rounded-2xl flex items-center justify-center"
              style={{ background: "#111118", border: "1px solid #1e1e2e" }}
            >
              <Zap size={28} style={{ color: "#7c6af7" }} />
            </div>
            <div>
              <h2 className="text-xl font-semibold mb-1" style={{ color: "#e2e2f0" }}>
                ManusClone Agent
              </h2>
              <p className="text-sm" style={{ color: "#6b6b8a" }}>
                Agent IA autonome · Recherche web · Exécution code · Gestion fichiers
              </p>
            </div>
          </div>
        ) : (
          messages.map((msg) => <MessageBubble key={msg.id} message={msg} />)
        )}
        <div ref={bottomRef} />
      </div>

      {/* Input */}
      <div className="flex-shrink-0 border-t max-w-3xl mx-auto w-full" style={{ borderColor: "#1e1e2e" }}>
        <ChatInput onSend={handleSend} disabled={isLoading} />
      </div>
    </div>
  );
}
